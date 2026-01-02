"""
manage_db.py: Script de consola para gestionar la base de datos vectorial.
Uso:
    python manage_db.py ingest  -> Carga documentos desde la carpeta
    python manage_db.py clear   -> Elimina toda la colección
"""
import argparse
import os
from services import IngestionService

# Ajustamos la ruta asumiendo que 'documents' está en la raíz del monorepo (un nivel arriba de backend)
DIRECTORY_PATH_PDFS = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "documents")


def ingest_data():
    """Carga o actualiza los datos en ChromaDB."""
    service = IngestionService(DIRECTORY_PATH_PDFS)
    service.ingest_all()


def clear_data():
    """Elimina la colección de la base de datos."""
    service = IngestionService(DIRECTORY_PATH_PDFS)
    service.clear_database()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gestión de la Base de Datos Vectorial (RAG)")
    parser.add_argument("action", choices=[
                        "ingest", "clear"], help="Acción a realizar: 'ingest' para cargar datos, 'clear' para borrar la BD.")

    args = parser.parse_args()

    if args.action == "ingest":
        ingest_data()
    elif args.action == "clear":
        clear_data()
