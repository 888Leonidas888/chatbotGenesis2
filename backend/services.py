import os
from typing import Dict, Any, AsyncGenerator
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from rag_core import get_vectorstore, get_llm


class IngestionService:
    """
    Servicio encargado de la ingesta de documentos (ETL).
    Implementa carga perezosa (lazy loading) y recursiva para manejo eficiente de memoria.
    """

    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        self.vector_store = get_vectorstore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=350
        )

    def ingest_all(self, batch_size: int = 50):
        """
        Carga documentos anidados de forma perezosa y los procesa en lotes.
        batch_size: Cantidad de páginas a procesar en memoria antes de enviar a la BD.
        """
        if not os.path.exists(self.directory_path):
            try:
                os.makedirs(self.directory_path)
                print(
                    f"Directorio {self.directory_path} creado. Por favor añade PDFs.")
                return
            except OSError as e:
                print(
                    f"Error al acceder/crear el directorio {self.directory_path}: {e}")
                return

        print(f"Iniciando escaneo recursivo en '{self.directory_path}'...")

        loader = PyPDFDirectoryLoader(self.directory_path, glob="**/*.pdf")

        docs_buffer = []
        total_chunks = 0

        for doc in loader.lazy_load():
            docs_buffer.append(doc)

            if len(docs_buffer) >= batch_size:
                total_chunks += self._process_batch(docs_buffer)
                docs_buffer = []

        if docs_buffer:
            total_chunks += self._process_batch(docs_buffer)

        print(
            f"Ingesta finalizada. Total de fragmentos indexados: {total_chunks}")

    def ingest_one_pdf(self, file_path: str):

        if os.path.exists(file_path):
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            if docs:
                splits = self.text_splitter.split_documents(docs)
                self._process_batch(splits)
            else:
                print("No se encontraron documentos para procesar.")
        else:
            print(f"El archivo {file_path} no existe.")

    def _process_batch(self, docs: list) -> int:
        splits = self.text_splitter.split_documents(docs)
        if splits:
            print(
                f"Insertando lote de {len(splits)} fragmentos en ChromaDB...")
            self.vector_store.add_documents(documents=splits)
            return len(splits)
        return 0

    def clear_database(self):
        print("Eliminando colección de la base de datos...")
        try:
            self.vector_store.delete_collection()
            print("Colección eliminada exitosamente.")
        except Exception as e:
            print(f"Error al eliminar colección: {e}")

    def collection_count(self):
        self.vector_store.get()
        return self.vector_store._collection.count()


class ChatService:
    """
    Servicio encargado de la lógica de negocio del Chatbot RAG.
    """

    SYSTEM_PROMPT = (
        "Eres un asistente experto en programación y documentación técnica. "
        "Utiliza el siguiente contexto recuperado para responder a la pregunta del usuario. "
        "Si la respuesta no se encuentra en el contexto, di amablemente que no tienes esa información. "
        "Mantén la respuesta concisa y técnica."
        "\n\n"
        "{context}"
    )

    def __init__(self):
        self.llm = get_llm()
        self.vector_store = get_vectorstore()
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 6}, search_type="mmr")
        self.rag_chain = self._build_chain()

    def _build_chain(self):
        """Construye cadena RAG moderna con LCEL (reemplaza create_retrieval_chain)"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", "{input}")
        ])

        # Cadena RAG moderna: retrieve → format → LLM → parse
        return (
            {"context": self.retriever, "input": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask2(self, question: str) -> Dict[str, Any]:

        context_docs = self.retriever.invoke(question)

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", "{input}")
        ])

        content_text = "\n\n".join([doc.page_content for doc in context_docs])
        messages = prompt.invoke({"context": content_text, "input": question})

        ia_messages = self.llm.invoke(messages)

        return {'answer': ia_messages.content}

    def ask(self, question: str) -> Dict[str, Any]:
        """Respuesta síncrona con contexto completo"""
        result = self.rag_chain.invoke(question)
        return {"answer": result}

    # -> AsyncGenerator[Dict[str, Any], None]:
    async def ask_stream(self, question: str):
        """
        Generador asíncrono que emite fragmentos de la respuesta y las fuentes al final.
        Yields:
            dict: {"type": "answer", "content": "..."} o {"type": "sources", "content": [...]}
        """
        context_docs = self.retriever.invoke(question)

        # 1. Formatear el contexto manualmente
        context_text = "\n\n".join([doc.page_content for doc in context_docs])

        # 2. Construir los mensajes con el prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", "{input}")
        ])
        messages = prompt_template.invoke(
            {"context": context_text, "input": question})

        # 3. Stream de tokens usando los mensajes enriquecidos
        async for token in self.llm.astream(messages):
            if token:
                yield {"type": "answer", "content": token.content}

        # Fuentes al final
        sources = []
        for doc in context_docs[:3]:  # Top 3 fuentes
            if "source" in doc.metadata:
                sources.append(doc.metadata["source"].split("/")[-1])

        yield {"type": "sources", "content": list(set(sources))}
