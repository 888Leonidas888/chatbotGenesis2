import chainlit as cl
import requests

URL_BASE = "http://localhost:8001"

@cl.on_message
async def main(message: cl.Message):
    api_chat = f"{URL_BASE}/chat"
    response = requests.post(api_chat, json={"question": message.content})

    if response.status_code == 200:
        data = response.json()
        await cl.Message(content=data["answer"]).send()
    else:
        await cl.Message(content="Houston tenemos un problema...").send()
