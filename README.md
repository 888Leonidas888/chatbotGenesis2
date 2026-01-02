# Chatbot Genesis AI 🤖

Este proyecto es un Chatbot inteligente basado en **RAG (Retrieval-Augmented Generation)**. Utiliza **FastAPI** para exponer una API REST, **LangChain** para la orquestación, **ChromaDB** como base de datos vectorial y **Google Gemini** como modelo de lenguaje (LLM).

## 📂 Estructura del Proyecto

El proyecto funciona como un monorepo con la siguiente estructura:

```text
chatbot_genesis2/
├── backend/           # Código fuente del servidor y lógica RAG
│   ├── api.py         # API FastAPI
│   ├── manage_db.py   # Script para cargar/limpiar la base de datos
│   ├── services.py    # Lógica de negocio (Ingesta y Chat)
│   └── rag_core.py    # Configuración central (LLM, Embeddings, DB)
├── documents/         # Carpeta donde debes colocar tus archivos PDF
└── .env               # Variables de entorno (API Keys)
```

## 🛠️ Requisitos Previos

*   Python 3.10 o superior.
*   Una API Key de Google AI (Gemini).
*   ChromaDB ejecutándose (localmente o en Docker).

## 🚀 Instalación

1.  **Clona el repositorio** y entra en la carpeta:
    ```bash
    cd chatbot_genesis2
    ```

2.  **Crea un entorno virtual** (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias**:
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Configura las variables de entorno**:
    Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

    ```ini
    GOOGLE_API_KEY=tu_api_key_aqui
    CHROMA_HOST=localhost
    CHROMA_PORT=8000
    ```

## 🏃‍♂️ Ejecución

### 1. Iniciar ChromaDB
El proyecto requiere que ChromaDB esté corriendo en el puerto 8000. Abre una terminal nueva y ejecuta:

```bash
# Opción A: Si tienes chroma instalado localmente
chroma run --path ./chroma-data --port 8000

# Opción B: Usando Docker (Recomendado)
docker run -p 8000:8000 chromadb/chroma
```

### 2. Cargar Documentos (Ingesta)
Coloca tus archivos PDF dentro de la carpeta `documents/` en la raíz del proyecto. Luego, ejecuta el script de gestión:

```bash
cd backend
python manage_db.py ingest
```
*Esto leerá los PDFs, generará los embeddings y los guardará en ChromaDB.*

### 3. Iniciar la API del Chatbot
Una vez cargados los datos, levanta el servidor FastAPI (correrá en el puerto 8001 para no chocar con Chroma):

```bash
cd backend
uvicorn api:app --reload --port 8001
```

## 📡 Uso de la API

*   **Documentación Interactiva (Swagger):** Visita `http://localhost:8001/docs`
*   **Endpoint de Chat:** `POST /chat`
*   **Endpoint de Streaming:** `POST /chat/stream`