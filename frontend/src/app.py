import chainlit as cl
import requests

URL_BASE = "http://localhost:8001"

# @cl.on_message
# async def main(message: cl.Message):
#     api_chat = f"{URL_BASE}/chat"
#     response = requests.post(api_chat, json={"question": message.content})

#     if response.status_code == 200:
#         data = response.json()
#         await cl.Message(content=data["answer"]).send()
#     else:
#         await cl.Message(content="Houston tenemos un problema...").send()


@cl.on_message
async def main(message: cl.Message):
    import json
    import httpx

    payload = {"question": message.content}
    url = f"{URL_BASE}/chat/stream"

    msg = cl.Message(content="")

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        msg_type = data.get("type")
                        content = data.get("content", "")
                        
                        if msg_type == "answer":
                            await msg.stream_token(content)
                        elif msg_type == "sources":
                            sources_text = "\n\n**Fuentes:**\n" + \
                                "\n".join([f"- {src}" for src in content])
                            await msg.stream_token(sources_text)
                await msg.update()
            else:
                msg.content = "Houston tenemos un problema..."
                await msg.update()
