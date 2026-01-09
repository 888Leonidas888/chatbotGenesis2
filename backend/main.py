# """
# api.py: Servidor FastAPI para el Chatbot RAG.
# Ejecutar con: uvicorn api:app --reload --port 8001
# """
# import json
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# from services import ChatService

# app = FastAPI(title="Chatbot Genesis AI",
#               description="API de Chatbot con RAG usando LangChain y Gemini")


# class ChatRequest(BaseModel):
#     question: str


# class ChatResponse(BaseModel):
#     answer: str
#     sources: list[str] = []


# chat_service = ChatService()


# @app.get("/", tags=["Home"])
# async def root():
#     return {"message": "Chatbot Genesis API está en línea"}


# @app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
# async def chat_endpoint(request: ChatRequest):
#     try:
#         # Invocar la cadena RAG
#         response = chat_service.ask(request.question)

#         # Procesar fuentes (metadata de los documentos recuperados)
#         sources = []
#         if "context" in response:
#             for doc in response["context"]:
#                 if "source" in doc.metadata:
#                     # Limpiamos la ruta para mostrar solo el nombre del archivo si se desea
#                     source_name = doc.metadata["source"].split("/")[-1]
#                     sources.append(source_name)

#         # Eliminar duplicados de fuentes
#         unique_sources = list(set(sources))

#         return ChatResponse(
#             answer=response["answer"],
#             sources=unique_sources
#         )

#     except Exception as e:
#         print(f"Error en el chat: {e}")
#         raise HTTPException(
#             status_code=500, detail="Ocurrió un error interno procesando tu solicitud.")


# @app.post("/api/v1/chat/stream", tags=["Chat"])
# async def chat_stream_endpoint(request: ChatRequest):
#     """
#     Endpoint de streaming. Devuelve fragmentos JSON línea por línea.
#     """
#     async def generate():
#         try:
#             async for chunk in chat_service.ask_stream(request.question):
#                 # Enviamos cada fragmento como una línea JSON
#                 yield json.dumps(chunk) + "\n"
#         except Exception as e:
#             print(f"Error en el stream: {e}")
#             yield json.dumps({"type": "error", "content": str(e)}) + "\n"

#     return StreamingResponse(generate(), media_type="application/x-ndjson")

from api import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
    # uvicorn.run(app)
