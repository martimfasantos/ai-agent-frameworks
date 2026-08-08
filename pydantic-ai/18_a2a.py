"""
NOTE: This example creates an A2A server that listens on port 8000.
Run it with:  python 18_a2a.py
Then test with: curl -X POST http://localhost:8000/ -H "Content-Type: application/json" \\
    -d '{"jsonrpc":"2.0","method":"message/send","id":"1","params":{"message":{"role":"user","kind":"message","messageId":"m1","parts":[{"kind":"text","text":"What is 2+2?"}]}}}'

The agent card is served at http://localhost:8000/.well-known/agent-card.json
"""

from dotenv import load_dotenv

from fasta2a.pydantic_ai import agent_to_a2a
from pydantic_ai import Agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- A2A (Agent-to-Agent) protocol support
- Exposing a Pydantic AI agent as an A2A-compatible HTTP server
- fasta2a.pydantic_ai.agent_to_a2a() for zero-config server creation
- FastA2A ASGI application for production deployment

The A2A protocol enables agents built with different frameworks to
communicate over HTTP using a standardized JSON-RPC interface. FastA2A
makes it trivial to expose any Pydantic AI agent as an A2A server with a
single function call. The resulting FastA2A app is an ASGI application
that can be deployed with uvicorn or any ASGI server.

NOTE: A2A support lives in the separate `fasta2a` package. In Pydantic AI
v1 the same thing was available as the `agent.to_a2a()` method, which was
removed in v2 together with the `pydantic-ai-slim[a2a]` extra.

For more details, visit:
https://github.com/datalayer/fasta2a
-----------------------------------------------------------------------
"""

# --- 1. Create the agent ---
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions=(
        "You are a helpful math tutor. Explain concepts clearly "
        "and solve problems step by step. Be concise."
    ),
)


# --- 2. Add a tool ---
@agent.tool_plain
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., '2 + 3 * 4').
    """
    try:
        # Only allow safe math operations
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return f"Invalid expression: {expression}"
        result = eval(expression)  # noqa: S307
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# --- 3. Expose agent as A2A server ---
app = agent_to_a2a(
    agent,
    name="Math Tutor Agent",
    version="1.0.0",
    description="A helpful math tutor that can explain and calculate.",
)


# --- 4. Print server info and run ---
if __name__ == "__main__":
    print("=== A2A Protocol Example ===\n")
    print("Starting Math Tutor A2A server...")
    print(f"  Agent: Math Tutor")
    print(f"  Protocol: A2A (Agent-to-Agent)")
    print(f"  URL: http://localhost:8000")
    print()
    print("Test with:")
    print("  curl -X POST http://localhost:8000/ \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"jsonrpc":"2.0","method":"message/send","id":"1","params":')
    print('        {"message":{"role":"user","kind":"message","messageId":"m1",')
    print('          "parts":[{"kind":"text","text":"What is 15 * 23?"}]}}}\'')
    print()
    print("Agent card: http://localhost:8000/.well-known/agent-card.json")
    print()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
