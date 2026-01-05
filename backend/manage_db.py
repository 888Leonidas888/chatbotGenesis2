"""
manage_db.py: Script de consola para gestionar la base de datos vectorial.
Uso:
    python manage_db.py ingest  -> Carga documentos desde la carpeta
    python manage_db.py ingest_one_pdf --file -> Carga un pdf documento desde la ruta indicada
    python manage_db.py clear   -> Elimina toda la colección
"""
import argparse
import os
from services import IngestionService

DIRECTORY_PATH_PDFS = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "documents")


def ingest_data():
    """Carga o actualiza los datos en ChromaDB."""
    service = IngestionService(DIRECTORY_PATH_PDFS)
    service.ingest_all()


def ingest_data_one_pdf(pdf_path: str):
    """Carga o actualiza los datos en ChromaDB."""
    service = IngestionService(pdf_path)
    service.ingest_one_pdf(pdf_path)


def clear_data():
    """Elimina la colección de la base de datos."""
    service = IngestionService(DIRECTORY_PATH_PDFS)
    service.clear_database()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gestión de la Base de Datos Vectorial (RAG)")
    parser.add_argument("action", choices=[
                        "ingest", "ingest_one_pdf", "clear"], help="Acción a realizar: 'ingest' para cargar todo, 'ingest_one_pdf' para un archivo, 'clear' para borrar la BD.")
    parser.add_argument(
        "--file", type=str, help="Ruta del archivo PDF (requerido para ingest_one_pdf)")

    args = parser.parse_args()

    if args.action == "ingest":
        ingest_data()
    elif args.action == "ingest_one_pdf":
        if args.file:
            ingest_data_one_pdf(args.file)
        else:
            print("Error: Debes especificar el archivo con --file")
    elif args.action == "clear":
        clear_data()
