from strands import Agent
from strands.models.openai import OpenAIModel

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- Agents-as-tools multi-agent pattern
- Passing agents directly in the tools list (auto-converted)
- Using agent.as_tool() for custom name/description
- Orchestrator agent that routes to the right specialist

Since v1.34, Strands can auto-wrap Agent instances passed in the tools
list. You can also use agent.as_tool() to customise the tool name,
description, and context behaviour (e.g. preserve_context=True).

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/
-------------------------------------------------------
"""


# --- 1. Configure model ---
openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)


# --- 2. Create specialist agents ---
math_agent = Agent(
    model=openai_model,
    name="math_expert",
    description="Solve mathematical problems with step-by-step explanations.",
    system_prompt="You are a math expert. Solve problems step by step. Be concise (1-2 sentences).",
    callback_handler=None,
)

history_agent = Agent(
    model=openai_model,
    name="history_expert",
    description="Answer questions about historical events, people, and periods.",
    system_prompt="You are a history expert. Provide accurate, concise historical information (1-2 sentences).",
    callback_handler=None,
)


# --- 3. Create orchestrator using both patterns ---
# Pattern A: Pass agent directly in tools list (auto-converted since v1.34)
# Pattern B: Use agent.as_tool() for custom name/description
orchestrator = Agent(
    model=openai_model,
    system_prompt="""You are a helpful assistant that routes questions to specialized experts:
- For math problems -> use the math_expert tool
- For history questions -> use the history_assistant tool
- For simple questions -> answer directly

Always use the most appropriate expert for the question.""",
    tools=[
        math_agent,  # Pattern A: direct agent (auto-wrapped)
        history_agent.as_tool(  # Pattern B: custom name & description
            name="history_assistant",
            description="Research and answer historical questions with citations.",
        ),
    ],
)

# --- 4. Run the orchestrator ---
print("=== Multi-Agent Orchestration (Agents as Tools) ===\n")
result = orchestrator(
    "I have two questions:\n"
    "1. What is the factorial of 7?\n"
    "2. Who was the first person to walk on the moon and in what year?"
)

# --- 5. Print results ---
print(f"\n--- Orchestrator Response ---\n{result.message}")
