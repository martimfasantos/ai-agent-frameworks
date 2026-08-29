import asyncio
import os

from ag2 import Agent
from ag2.config import OpenAIConfig
from ag2.events import ToolCallEvent, ToolResultEvent
from ag2.tools import LocalEnvironment, SandboxCodeTool

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- SandboxCodeTool: code execution exposed to the agent as a tool
- LocalEnvironment as the execution backend (no Docker needed)
- State persisting across calls inside one environment instance

AG2 1.0 replaces the classic code-executor agent pair with a single
tool. SandboxCodeTool gives the model a run_code(code, language)
function and the CodeEnvironment decides where it runs — here a
local subprocess in res/sandbox. Because one environment backs every
call, files written by one snippet are visible to the next.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/tools/code_execution.mdx
-------------------------------------------------------
"""


async def main() -> None:
    # --- 1. Create a working directory for the sandbox ---
    os.makedirs("res/sandbox", exist_ok=True)

    # --- 2. Build the code execution tool over a local environment ---
    # LocalEnvironment runs code as a subprocess on this host: fast and
    # dependency-free, but with no isolation. Swap in DockerEnvironment or
    # DaytonaEnvironment when the code cannot be trusted.
    environment = LocalEnvironment("res/sandbox", timeout=30)
    code_tool = SandboxCodeTool(environment, languages=("python",))

    agent = Agent(
        "analyst",
        prompt=(
            "You are a Python analyst. Always compute answers by calling "
            "run_code rather than reasoning them out. Report the printed "
            "result in one sentence."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[code_tool],
    )

    # --- 3. First task: compute and persist to a file ---
    print("=== Task 1: compute the first 10 Fibonacci numbers ===\n")
    reply = await agent.ask(
        "Compute the first 10 Fibonacci numbers, print them, and also write "
        "them to fib.txt in the working directory."
    )
    print(f"Agent: {reply.body}")

    # --- 4. Second task: proves the sandbox filesystem persisted ---
    print("\n=== Task 2: read the file back from the same sandbox ===\n")
    reply2 = await reply.ask("Read fib.txt back and print its contents.")
    print(f"Agent: {reply2.body}")

    # --- 5. Show the code the model actually ran ---
    print("\n=== Executed snippets ===")
    for event in await reply2.context.stream.history.get_events():
        if isinstance(event, ToolCallEvent):
            print(f"  -> {event.name}: {event.arguments[:120]}")
        elif isinstance(event, ToolResultEvent):
            output = " ".join(str(part.content) for part in event.result.parts)
            print(f"  <- {output.strip()[:200]}")

    print(f"\nSandbox files: {sorted(os.listdir('res/sandbox'))}")


if __name__ == "__main__":
    asyncio.run(main())
