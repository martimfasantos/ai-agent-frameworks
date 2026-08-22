from dotenv import load_dotenv

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Creating an agent with create_deep_agent
- Passing a model string and a system prompt
- Invoking the agent with a chat-style message

Deep Agents is an "agent harness" built on LangChain and LangGraph. Even
this minimal agent already ships with built-in planning, a virtual
filesystem, and subagent tools — but here we just run the simplest
possible single-turn conversation to confirm the setup works.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/overview
-----------------------------------------------------------------------
"""

# --- 1. Create the deep agent ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    system_prompt="You are a helpful assistant. Be concise, reply with one sentence.",
)

# --- 2. Invoke the agent ---
print("=== Deep Agents Hello World ===")
question = "Where does the phrase 'hello world' come from?"
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

# --- 3. Print the final answer ---
answer = result["messages"][-1].text
print(f"\nUser: {question}")
print(f"Agent: {answer}")
