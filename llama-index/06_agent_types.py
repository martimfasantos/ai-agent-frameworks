import asyncio
import contextlib
import io
from typing import Any, Dict, Tuple

from llama_index.core.agent import ReActAgent, CodeActAgent, FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- ReAct Agent for reasoning and acting with tools
- Function Agent for function calling with multiple tools
- CodeAct Agent for writing and executing code with state persistence

The three agent types differ in how they decide what to do next: ReActAgent
reasons out loud in a Thought/Action/Observation loop, FunctionAgent uses the
model's native tool-calling API, and CodeActAgent writes Python and hands it to
a code executor you supply. All three are Workflow subclasses, so they share the
same `await agent.run(...)` interface.

For more details, visit:
https://developers.llamaindex.ai/python/framework/understanding/agent/
https://developers.llamaindex.ai/python/examples/agent/code_act_agent/
-------------------------------------------------------
"""

# --- 1. Create the LLM ---
llm = OpenAI(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
)


# --- 2. Create an example tool ---
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)


# --- 3.1 ReAct Agent: explicit Thought/Action/Observation loop ---
react_agent = ReActAgent(
    name="react_agent",
    description="A ReAct agent that reasons step-by-step using tools.",
    system_prompt="Answer with the final number only, no explanation.",
    tools=[multiply_tool],
    llm=llm,
)

# --- 3.2 Function Agent: native tool calling ---
function_agent = FunctionAgent(
    name="function_agent",
    description="A function-calling agent that invokes tools directly.",
    system_prompt="Answer with the final number only, no explanation.",
    tools=[multiply_tool],
    llm=llm,
)


# --- 3.3 CodeAct Agent: writes Python, a code executor runs it ---
class SimpleCodeExecutor:
    """
    Runs Python code with state that persists between executions.

    Globals and locals are kept on the instance, so variables defined in one
    execution are still available in the next.
    """

    def __init__(self, locals: Dict[str, Any], globals: Dict[str, Any]):
        self.globals = globals
        self.locals = locals

    def execute(self, code: str) -> Tuple[bool, str, Any]:
        """Execute Python code and capture whatever it prints"""
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, self.globals, self.locals)
        except Exception as e:
            return False, f"{type(e).__name__}: {e}", None
        return True, stdout.getvalue(), None


code_agent = CodeActAgent(
    name="code_agent",
    code_execute_fn=SimpleCodeExecutor(locals={}, globals={}).execute,
    tools=[multiply_tool],
    llm=llm,
)


# --- 4. Run each agent type on the same task ---
async def main():
    task = "What is 1234 multiplied by 4321?"

    print("=== ReActAgent ===")
    print(await react_agent.run(task))

    print("\n=== FunctionAgent ===")
    print(await function_agent.run(task))

    # A shared Context carries the chat history, and SimpleCodeExecutor keeps the
    # Python variables, so the second turn can reuse what the first one defined.
    ctx = Context(code_agent)

    print("\n=== CodeActAgent ===")
    print(await code_agent.run("Compute 1234 * 4321 and store it in `total`.", ctx=ctx))

    print("\n=== CodeActAgent (code state persists across runs) ===")
    print(await code_agent.run("Now print total // 1000 using `total`.", ctx=ctx))


if __name__ == "__main__":
    asyncio.run(main())
