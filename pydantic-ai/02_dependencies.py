from dataclasses import dataclass

from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Dependency injection with deps_type and RunContext
- Typed dependencies using dataclasses
- Dynamic system prompts that read from dependencies via RunContext
- Tools that access dependency data through RunContext

Dependency injection lets you pass runtime data (database connections,
user sessions, config objects) into agents without hard-coding values.
Tools and system prompts receive a typed RunContext containing your
dependencies, enabling clean separation between agent logic and
application state.

For more details, visit:
https://pydantic.dev/docs/ai/core-concepts/dependencies/
-----------------------------------------------------------------------
"""


# --- 1. Define a dependency dataclass ---
@dataclass
class SupportDeps:
    """Dependencies available to the support agent at runtime."""

    customer_name: str
    account_tier: str  # "free", "pro", "enterprise"
    recent_purchases: list[str]


# --- 2. Create agent with typed dependencies ---
support_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    deps_type=SupportDeps,
    instructions="You are a customer support agent. Be helpful and concise.",
)


# --- 3. Dynamic system prompt that reads from dependencies ---
@support_agent.system_prompt
def add_customer_context(ctx: RunContext[SupportDeps]) -> str:
    """Inject customer info into the system prompt at runtime."""
    return (
        f"You are helping customer '{ctx.deps.customer_name}' "
        f"who is on the '{ctx.deps.account_tier}' plan. "
        f"Their recent purchases: {', '.join(ctx.deps.recent_purchases) or 'none'}."
    )


# --- 4. Tool that accesses dependencies ---
@support_agent.tool
def check_upgrade_eligibility(ctx: RunContext[SupportDeps]) -> str:
    """Check if the customer is eligible for a plan upgrade."""
    tier = ctx.deps.account_tier
    if tier == "free":
        return f"{ctx.deps.customer_name} is eligible for Pro upgrade ($9.99/mo)."
    elif tier == "pro":
        return (
            f"{ctx.deps.customer_name} is eligible for Enterprise upgrade ($49.99/mo)."
        )
    else:
        return f"{ctx.deps.customer_name} is already on the highest tier."


@support_agent.tool
def lookup_purchase_details(ctx: RunContext[SupportDeps], product_name: str) -> str:
    """Look up details of a recent purchase.

    Args:
        product_name: The name of the product to look up.
    """
    if product_name.lower() in [p.lower() for p in ctx.deps.recent_purchases]:
        return f"Found purchase: {product_name} - delivered on 2025-03-15, order #ORD-42178."
    return f"No purchase found matching '{product_name}'."


# --- 5. Run examples ---
if __name__ == "__main__":
    # --------------------------------------------------------------
    # Example 1: Free-tier customer asking about upgrades
    # --------------------------------------------------------------
    print("=== Example 1: Free-Tier Customer ===")

    free_deps = SupportDeps(
        customer_name="Alice",
        account_tier="free",
        recent_purchases=["Basic Widget"],
    )

    result1 = support_agent.run_sync(
        "Am I eligible for an upgrade?",
        deps=free_deps,
    )
    print(f"Response: {result1.output}")
    print()

    # --------------------------------------------------------------
    # Example 2: Pro customer asking about a purchase
    # --------------------------------------------------------------
    print("=== Example 2: Pro Customer with Purchases ===")

    pro_deps = SupportDeps(
        customer_name="Bob",
        account_tier="pro",
        recent_purchases=["Premium Gadget", "Super Adapter", "Deluxe Cable"],
    )

    result2 = support_agent.run_sync(
        "Can you check on my Premium Gadget order?",
        deps=pro_deps,
    )
    print(f"Response: {result2.output}")
    print()

    # --------------------------------------------------------------
    # Example 3: Enterprise customer — no upgrade available
    # --------------------------------------------------------------
    print("=== Example 3: Enterprise Customer ===")

    enterprise_deps = SupportDeps(
        customer_name="Carol",
        account_tier="enterprise",
        recent_purchases=[],
    )

    result3 = support_agent.run_sync(
        "What upgrade options do I have?",
        deps=enterprise_deps,
    )
    print(f"Response: {result3.output}")
