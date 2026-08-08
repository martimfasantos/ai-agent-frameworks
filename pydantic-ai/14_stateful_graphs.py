from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from dotenv import load_dotenv
from pydantic_graph import GraphBuilder, StepContext, TypeExpression

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic Graph with the following features:
- GraphBuilder for declaratively wiring a graph out of @g.step functions
- State object persisting throughout entire workflow execution
- Steps reading and modifying shared state via ctx.state
- Decision nodes routing on a step's return type, including a cycle
- Rendering the built graph as a Mermaid state diagram

Graphs and finite state machines (FSMs) are a powerful abstraction to model,
execute, control and visualize complex workflows. While pydantic-graph is
developed as part of Pydantic AI, it has no dependency on pydantic-ai and
can be used as a standalone graph-based state machine library.

NOTE: This example does not use GenAI capabilities. See 15_graphs_with_genai.py
for an example that combines graph control flow with LLM-powered nodes.

For more details, visit:
https://pydantic.dev/docs/ai/graph/builder/
-----------------------------------------------------------------------
"""


# --- 1. Define state object that persists throughout the workflow ---
@dataclass
class MachineState:
    """State shared across all steps in the vending machine graph."""

    user_balance: float = 0.0
    product: str | None = None
    coins_to_insert: list[float] = field(default_factory=list)


# --- 2. Define the product catalog ---
PRODUCTS = {
    "water": 1.25,
    "soda": 1.50,
    "crisps": 1.75,
    "chocolate": 2.00,
}

# Simulated user actions (replaces interactive Prompt.ask)
SIMULATED_COINS = [1.00, 0.50, 0.50]
SIMULATED_PRODUCT = "soda"


# --- 3. Signal returned by `purchase` when the balance is too low ---
@dataclass
class NeedMoreCoins:
    """Routing signal: the purchase failed and more money is required."""

    shortfall: float


# --- 4. Build the graph ---
g = GraphBuilder(name="vending_machine", state_type=MachineState, output_type=str)


@g.step
async def insert_coin(ctx: StepContext[MachineState, None, object]) -> str | None:
    """Insert the next simulated coin; returns the already-selected product, if any."""
    amount = ctx.state.coins_to_insert.pop(0) if ctx.state.coins_to_insert else 0.25

    # Modify shared state (persists across step executions)
    ctx.state.user_balance += amount
    print(f"  Inserted ${amount:.2f}")
    print(f"   Balance: ${ctx.state.user_balance:.2f}")

    # None on the first pass, the product name once one has been chosen
    return ctx.state.product


@g.step
async def select_product(ctx: StepContext[MachineState, None, None]) -> str:
    """Select a product (simulated) and record it in the shared state."""
    print("Available products:")
    for product, price in PRODUCTS.items():
        print(f"   - {product}: ${price:.2f}")

    ctx.state.product = SIMULATED_PRODUCT
    print(f"  Selected: {SIMULATED_PRODUCT}")
    return SIMULATED_PRODUCT


@g.step
async def purchase(ctx: StepContext[MachineState, None, str]) -> str | NeedMoreCoins:
    """Attempt the purchase; a str output ends the graph, NeedMoreCoins loops back."""
    price = PRODUCTS[ctx.inputs]

    if ctx.state.user_balance >= price:
        ctx.state.user_balance -= price
        print(f"  Purchased {ctx.inputs}!")
        print(f"  Change returned: ${ctx.state.user_balance:.2f}")
        return "Enjoy your purchase!"

    shortfall = price - ctx.state.user_balance
    print(f"  Insufficient funds for {ctx.inputs}")
    print(f"   Need ${shortfall:.2f} more")
    return NeedMoreCoins(shortfall=shortfall)


# --- 5. Wire the steps together, including the retry cycle ---
g.add(
    g.edge_from(g.start_node).to(insert_coin),
    g.edge_from(insert_coin).to(
        g.decision()
        .branch(
            g.match(TypeExpression[str]).label("product chosen").to(purchase),
        )
        .branch(
            g.match(TypeExpression[None]).label("nothing chosen yet").to(select_product),
        )
    ),
    g.edge_from(select_product).to(purchase),
    g.edge_from(purchase).to(
        g.decision()
        .branch(
            g.match(NeedMoreCoins).label("insufficient funds").to(insert_coin),
        )
        .branch(
            g.match(TypeExpression[str]).label("paid").to(g.end_node),
        )
    ),
)

vending_machine_graph = g.build()


# --- 6. Run the stateful graph workflow ---
async def main():
    print("=== Stateful Graph Example ===\n")
    print("Vending Machine Workflow")
    print("=" * 60)

    # Initialize state with simulated coin inserts
    state = MachineState(coins_to_insert=list(SIMULATED_COINS))

    # graph.run() is keyword-only and returns the end node's value directly
    output = await vending_machine_graph.run(state=state)

    print()
    print("=" * 60)
    print(f"Result: {output}")
    print("Final state:")
    print(f"   Balance: ${state.user_balance:.2f}")
    print(f"   Product: {state.product}")

    print("\nMermaid Diagram of Graph:")
    print(vending_machine_graph.render(title="Vending Machine", direction="TB"))


if __name__ == "__main__":
    asyncio.run(main())
