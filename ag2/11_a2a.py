import asyncio
import os

import httpx
import uvicorn

from ag2 import Agent, tool
from ag2.a2a import A2AConfig, A2AServer, build_card
from ag2.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- A2AServer + build_card to expose an Agent over the A2A protocol
- A2AConfig as a ModelConfig, making a remote agent look local
- Server-side tools executing on the server, not the caller

In AG2 1.0 the remote agent is no longer a special Agent subclass:
A2AConfig is a model config, so a plain Agent pointed at a card URL
speaks A2A and keeps the familiar ask() / reply.ask() shape. The
server publishes an agent card at /.well-known/agent-card.json,
which the client fetches to pick a transport.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/a2a/server.mdx
-------------------------------------------------------
"""

PORT = 18765
BASE_URL = f"http://127.0.0.1:{PORT}"


# --- 1. A tool that runs on the SERVER side ---
@tool
def glossary(term: str) -> str:
    """Look up the house translation for a term."""
    house_style = {"agent": "agent (fr: « agent »)", "tool": "outil"}
    return house_style.get(term.lower(), f"no house entry for {term}")


def build_server() -> uvicorn.Server:
    """Build the A2A JSON-RPC server around a translator agent."""
    server_agent = Agent(
        "translator",
        prompt=(
            "You are a translator. Translate the user's text to French. "
            "Consult the glossary tool for any term that might have a house "
            "translation. Output only the French translation."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[glossary],
    )

    # --- 2. Wrap it: build_card publishes discovery metadata ---
    a2a_server = A2AServer(server_agent)
    card = build_card(server_agent, url=BASE_URL)
    asgi = a2a_server.build_jsonrpc(url=BASE_URL, card=card)

    return uvicorn.Server(
        uvicorn.Config(asgi, host="127.0.0.1", port=PORT, log_level="warning")
    )


async def main() -> None:
    print("=== A2A: agent-to-agent over JSON-RPC ===\n")

    # --- 3. Start the server in the background ---
    server = build_server()
    server_task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.1)
    print(f"Server listening on {BASE_URL}")

    # --- 4. Fetch the published agent card ---
    async with httpx.AsyncClient() as client:
        card = (await client.get(f"{BASE_URL}/.well-known/agent-card.json")).json()
    print(f"Agent card: name={card['name']!r} version={card['version']}")
    bindings = [i["protocolBinding"] for i in card["supportedInterfaces"]]
    print(f"Bindings:   {bindings}")
    print(f"Skills:     {[s['id'] for s in card['skills']]}\n")

    # --- 5. A plain Agent whose 'model' is the remote A2A server ---
    remote = Agent("remote_translator", config=A2AConfig(card_url=BASE_URL))

    reply = await remote.ask("Translate: 'Hello, how are you today?'")
    print("Turn 1")
    print("  sent:     Hello, how are you today?")
    print(f"  received: {reply.body}")

    # --- 6. Continuation: history is shipped with every A2A call ---
    reply2 = await reply.ask("Now translate: 'The agent used a tool.'")
    print("\nTurn 2 (same conversation, server-side glossary tool consulted)")
    print("  sent:     The agent used a tool.")
    print(f"  received: {reply2.body}")

    # --- 7. Shut the server down ---
    server.should_exit = True
    await server_task
    print("\n=== A2A demo complete ===")


if __name__ == "__main__":
    asyncio.run(main())
