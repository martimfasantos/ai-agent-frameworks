import os
import asyncio

from google.adk import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from settings import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- Built-in code execution via UnsafeLocalCodeExecutor
- Letting agents write and run Python code to solve problems
- Combining code execution with natural language responses

ADK v2.0 introduced the code_executor parameter on Agent, which
allows the agent to generate and execute code as part of its
reasoning. UnsafeLocalCodeExecutor runs code in the local process
(use only in trusted environments). For production, consider
sandboxed alternatives.

For more details, visit:
https://google.github.io/adk-docs/tools/code-execution/
-------------------------------------------------------
"""

APP_NAME = "code_executor_demo"
USER_ID = "user"


# --- 1. Create an agent with code execution capability ---
math_agent = Agent(
    name="math_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="""You are a math assistant. When asked a math question,
    write and execute Python code to compute the answer accurately.
    Show the code you used and the result.""",
    code_executor=UnsafeLocalCodeExecutor(),
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    runner = Runner(
        agent=math_agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=InMemoryArtifactService(),
    )

    # --- Ask a computation question ---
    print("=== Math with code execution ===")
    user_message = Content(
        role="user",
        parts=[Part(text="What is the sum of the first 100 prime numbers?")],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=user_message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text and part.text.strip():
                    print(f"[{event.author}]: {part.text.strip()}")
                if hasattr(part, "executable_code") and part.executable_code:
                    print(f"\n--- Generated Code ---")
                    print(part.executable_code.code)
                    print("--- End Code ---\n")
                if hasattr(part, "code_execution_result") and part.code_execution_result:
                    print(f"--- Execution Result ---")
                    print(part.code_execution_result.output)
                    print("--- End Result ---\n")


if __name__ == "__main__":
    asyncio.run(main())
