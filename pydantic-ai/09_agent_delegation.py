from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits

from utils import show_metrics
from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Multi-Agent Applications patterns
- One agent delegating work to another agent via tools
- Parent agent calls child agent, then takes back control when finished
- Passing ctx.usage to track combined usage across multiple agents

"Agent delegation" refers to the scenario where an agent delegates work 
to another agent, then takes back control when the delegate agent 
(the agent called from within a tool) finishes.

For more details, visit:
https://ai.pydantic.dev/multi-agent-applications/#agent-delegation
-----------------------------------------------------------------------
"""

# --- 1. Create a specialist agent that generates jokes ---
joke_generator = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=list[str],
    system_prompt="Generate short, funny jokes on the given topic",
)

# --- 2. Create a coordinator agent that selects the best joke ---
joke_selector = Agent(
    model=settings.OPENAI_MODEL_NAME,
    system_prompt=(
        "Use the joke_factory tool to generate multiple jokes, "
        "then choose and return only the best one."
    ),
)


# --- 3. Define delegation tool that calls the specialist agent ---
@joke_selector.tool
async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
    print(f"  Generating {count} jokes...")

    # Delegate to specialist agent, passing usage for tracking
    result = await joke_generator.run(
        f"Generate {count} jokes about cats",
        usage=ctx.usage,  # Track combined usage across both agents
    )

    return result.output


# --- 4. Run the workflow ---
print("=== Simple Agent Delegation Example ===\n")

# Run the coordinator agent which will delegate to the specialist
result = joke_selector.run_sync(
    "Tell me a joke about cats",
    usage_limits=UsageLimits(request_limit=5, total_tokens_limit=500),
)

print(f"Selected joke:\n{result.output}\n")

# Show combined metrics from both agents
# > The usage includes API calls from both joke_generator and joke_selector
show_metrics(result.usage)
