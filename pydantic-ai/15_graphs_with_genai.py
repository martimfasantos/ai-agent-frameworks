from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_graph import GraphBuilder, StepContext, TypeExpression

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic Graph + Pydantic AI with the following features:
- Agents called from inside @g.step functions for LLM-powered decisions
- Feedback loops where the LLM output drives graph transitions
- State accumulation across LLM-powered steps
- Combining deterministic graph flow with generative AI

This example shows how to embed Pydantic AI agents inside graph steps,
letting the LLM make decisions that drive the graph's control flow.
A content review pipeline uses one agent to draft content and another
to critique it, looping until quality is acceptable.

For more details, visit:
https://pydantic.dev/docs/ai/graph/builder/steps/
-----------------------------------------------------------------------
"""


# --- 1. Define shared state ---
@dataclass
class ReviewState:
    """State persisted across the content review pipeline."""

    topic: str = "the benefits of open source software"
    draft: str = ""
    feedback: str = ""
    revision_count: int = 0
    max_revisions: int = 2
    approved: bool = False
    history: list[str] = field(default_factory=list)


# --- 2. Signal returned by the reviewer when the draft is not good enough ---
@dataclass
class NeedsRevision:
    """Routing signal: send the draft back to the writer with feedback."""

    feedback: str


# --- 3. Create the agents ---
writer_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions=(
        "You are a concise technical writer. "
        "Write or revise content based on the given topic and feedback. "
        "Keep responses to 2-3 sentences."
    ),
)

reviewer_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions=(
        "You are a strict content reviewer. A draft is only acceptable if it "
        "names at least one concrete real-world project as an example.\n"
        "Respond with ONLY one of:\n"
        "- 'APPROVED' if the draft meets that bar\n"
        "- 'REVISE: <specific feedback>' if it does not\n"
        "Be concise."
    ),
)


# --- 4. Build the graph with LLM-powered steps ---
g = GraphBuilder(name="review_pipeline", state_type=ReviewState, output_type=str)


@g.step
async def write_draft(ctx: StepContext[ReviewState, None, object]) -> str:
    """Use the writer agent to create or revise content."""
    if ctx.state.feedback:
        prompt = (
            f"Revise this draft about '{ctx.state.topic}':\n"
            f"Draft: {ctx.state.draft}\n"
            f"Feedback: {ctx.state.feedback}"
        )
    else:
        prompt = f"Write a short paragraph about: {ctx.state.topic}"

    result = await writer_agent.run(prompt)
    ctx.state.draft = result.output
    ctx.state.revision_count += 1
    ctx.state.history.append(f"Draft v{ctx.state.revision_count}: {ctx.state.draft}")

    print(f"  [Writer] Draft v{ctx.state.revision_count}: {ctx.state.draft[:80]}...")
    return ctx.state.draft


@g.step
async def review_draft(
    ctx: StepContext[ReviewState, None, str],
) -> str | NeedsRevision:
    """Use the reviewer agent to evaluate the draft and decide the next hop."""
    result = await reviewer_agent.run(f"Review this draft:\n{ctx.inputs}")
    review = result.output.strip()

    if (
        review.upper().startswith("APPROVED")
        or ctx.state.revision_count >= ctx.state.max_revisions
    ):
        ctx.state.approved = True
        print("  [Reviewer] APPROVED")
        return ctx.state.draft

    ctx.state.feedback = review.replace("REVISE:", "").strip()
    print(f"  [Reviewer] Needs revision: {ctx.state.feedback[:60]}...")
    return NeedsRevision(feedback=ctx.state.feedback)


# --- 5. Wire the steps together, including the revision cycle ---
g.add(
    g.edge_from(g.start_node).to(write_draft),
    g.edge_from(write_draft).to(review_draft),
    g.edge_from(review_draft).to(
        g.decision()
        .branch(
            g.match(NeedsRevision).label("revise").to(write_draft),
        )
        .branch(
            g.match(TypeExpression[str]).label("approved").to(g.end_node),
        )
    ),
)

review_pipeline = g.build()


# --- 6. Run the pipeline ---
async def main():
    print("=== Graphs with GenAI: Content Review Pipeline ===\n")
    print("=" * 60)

    state = ReviewState()
    output = await review_pipeline.run(state=state)

    print()
    print("=" * 60)
    print(f"\nFinal content: {output}")
    print(f"Revisions: {state.revision_count}")
    print(f"Approved: {state.approved}")

    print(f"\nRevision history ({len(state.history)} versions):")
    for entry in state.history:
        print(f"  - {entry[:80]}...")

    print("\nMermaid Diagram:")
    print(review_pipeline.render(title="Content Review Pipeline", direction="TB"))


if __name__ == "__main__":
    asyncio.run(main())
