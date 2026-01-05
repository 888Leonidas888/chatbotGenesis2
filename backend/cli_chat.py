from services import ChatService
import asyncio
import sys
import os


async def main():
    print("--- Inicializando Sistema RAG (Cargando BD y Modelos) ---")
    try:
        chat_service = ChatService()
        print("Sistema listo. Escribe 'salir' para terminar.\n")
    except Exception as e:
        print(f"Error crítico al iniciar: {e}")
        return

    while True:
        question = input("\nUsuario: ")
        if question.lower() in ["salir", "exit", "quit"]:
            break

        print("Asistente: ", end="", flush=True)

        sources = []
        try:
            # Consumimos el generador asíncrono
            async for event in chat_service.ask_stream(question):
                if event["type"] == "answer":
                    print(event["content"], end="", flush=True)
                elif event["type"] == "sources":
                    sources = event["content"]

            # Mostrar fuentes al final de la respuesta
            if sources:
                print(f"\n\n[Fuentes: {', '.join(sources)}]")

        except Exception as e:
            print(f"\nError generando respuesta: {e}")

if __name__ == "__main__":
    asyncio.run(main())
