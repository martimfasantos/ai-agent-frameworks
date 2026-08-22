from collections.abc import Callable

from dotenv import load_dotenv
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)
from langchain_core.messages import AIMessage

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Writing a custom AgentMiddleware from scratch
- The wrap_model_call hook to intercept every model call
- Deterministically observing and reshaping the model's response

Middleware is the core extension point of Deep Agents: every built-in
capability (filesystem, subagents, summarization) is middleware. You can
write your own to observe or reshape the agent loop. Here we implement a
middleware that (1) counts how many times the model is invoked and (2)
deterministically appends a sign-off line to every final answer by
rewriting the model's response — proof the middleware reshaped the output
regardless of what the model chose to say.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/middleware/custom
-----------------------------------------------------------------------
"""


# --- 1. Define a custom middleware by subclassing AgentMiddleware ---
class SignOffMiddleware(AgentMiddleware):
    """Counts model calls and stamps a sign-off onto every final answer."""

    def __init__(self) -> None:
        super().__init__()
        self.model_calls = 0

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        # (a) Observe: count every model invocation.
        self.model_calls += 1
        print(f"  [middleware] intercepted model call #{self.model_calls}")

        # (b) Let the model run, then deterministically reshape its output.
        response = handler(request)
        last = response.result[-1]
        if isinstance(last, AIMessage) and not last.tool_calls:
            stamped = AIMessage(content=(last.text or "") + "\n-- handled by SignOffMiddleware")
            response.result = response.result[:-1] + [stamped]
        return response


# --- 2. Attach the custom middleware to the agent ---
middleware = SignOffMiddleware()
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    middleware=[middleware],
    system_prompt="You are a concise assistant.",
)

# --- 3. Ask a simple question ---
print("=== Deep Agents Custom Middleware ===")
question = "In one sentence, what is a vector database?"
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

# --- 4. Show the stamped answer and the observed call count ---
print(f"\nUser: {question}")
print(f"Agent:\n{result['messages'][-1].text}")
print(f"\nModel calls counted by middleware: {middleware.model_calls}")
stamped = "handled by SignOffMiddleware" in result["messages"][-1].text
print(f"Response reshaped by middleware: {stamped}")
