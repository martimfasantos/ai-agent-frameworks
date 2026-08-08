import os
import json
import asyncio
import logging

from google.adk import Event
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow, Edge, node, START
from google.genai import types
from pydantic import BaseModel, Field

from settings import settings
from utils import print_new_section

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

# Suppress the SDK's "non-text parts in response" informational warning
logging.getLogger("google_genai.types").setLevel(logging.ERROR)

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- Workflow: a graph of nodes and edges as the unit of orchestration
- @node / Edge: declaring nodes and wiring them explicitly
- Conditional routing: Event(route=[...]) plus a dict edge to pick a branch
- Node-as-tool: passing a Workflow straight into LlmAgent(tools=[...])

Graph workflows are the successor to the SequentialAgent / ParallelAgent /
LoopAgent trio used in 05_workflow_agents.py, all three of which ADK 2.6.x
deprecates "in favor of Workflow". A graph gives explicit routing and lets
plain Python nodes run with no model call at all. Since 2.4.0 a Workflow can
also be handed to an LlmAgent as a tool, so the same graph serves as both a
standalone deterministic pipeline and a callable skill.

For more details, visit:
https://adk.dev/graphs/
-------------------------------------------------------
"""


# ----------------------------------------------------------------
#                   1. Declare the graph nodes
# ----------------------------------------------------------------
# A node is any callable wrapped by @node. Returning an Event lets a node both
# emit a human-readable message and set `output`, which becomes the next node's
# input, plus `route` to select an outgoing branch.


class Ticket(BaseModel):
    """Input contract for the workflow — also the tool schema in section 3."""

    text: str = Field(description="The raw customer support ticket text.")


@node(name="normalize")
def normalize(node_input: Ticket, ctx) -> Event:
    """Collapses whitespace and lowercases the ticket text."""
    cleaned = " ".join(node_input.text.split()).lower()
    return Event(message=f"normalized: '{cleaned}'", output=cleaned)


@node(name="classify")
def classify(node_input: str, ctx) -> Event:
    """Picks the branch to follow — no model call, just rules."""
    billing_terms = ("invoice", "charge", "refund", "billed")
    label = "BILLING" if any(t in node_input for t in billing_terms) else "TECHNICAL"
    return Event(message=f"classified as {label}", route=[label], output=node_input)


@node(name="issue_refund")
def issue_refund(node_input: str, ctx) -> str:
    """Terminal node for the BILLING branch."""
    return "Refund issued and the case was closed."


@node(name="escalate")
def escalate(node_input: str, ctx) -> str:
    """Terminal node for the TECHNICAL branch."""
    return "Escalated to engineering with a 24h SLA."


# ----------------------------------------------------------------
#                     2. Wire nodes into a graph
# ----------------------------------------------------------------
# Edges accept an explicit Edge(...), a tuple for a straight hop, or a dict to
# fan out on the route a node emitted. `description` and `input_schema` are what
# make this Workflow usable as an LlmAgent tool in section 3 — NodeTool raises
# without an input_schema.

triage_workflow = Workflow(
    name="triage_workflow",
    description="Triages a customer support ticket and resolves or escalates it.",
    input_schema=Ticket,
    edges=[
        Edge(from_node=START, to_node=normalize),
        (normalize, classify),
        (classify, {"BILLING": issue_refund, "TECHNICAL": escalate}),
    ],
)


# ----------------------------------------------------------------
#             3. Run the graph on its own (no LLM involved)
# ----------------------------------------------------------------
# Runner(node=...) drives a Workflow directly. The user message is validated
# against input_schema, so we send it as JSON.


async def run_graph(ticket: str) -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="graph_demo", user_id="user", session_id="s1"
    )
    runner = Runner(
        node=triage_workflow, app_name="graph_demo", session_service=session_service
    )

    message = types.Content(
        role="user", parts=[types.Part(text=json.dumps({"text": ticket}))]
    )
    async for event in runner.run_async(
        user_id="user", session_id="s1", new_message=message
    ):
        node_name = getattr(event, "node_name", None)
        if node_name:
            print(f"    node {node_name:<13} -> {getattr(event, 'output', None)!r}")


print_new_section("1. Running the Workflow graph directly")

for ticket in ["I was charged twice on   invoice 88", "My SERVER keeps crashing"]:
    print(f"  Ticket: {ticket!r}")
    asyncio.run(run_graph(ticket))
    print()

print(
    "  The two tickets took different branches out of `classify`, decided by"
    "\n  Event(route=[...]) — and not one model call was made."
)


# ----------------------------------------------------------------
#          4. Node-as-tool: the same graph inside an LlmAgent
# ----------------------------------------------------------------
# New in ADK 2.4.0: LlmAgent auto-wraps a Workflow (or any @node) passed in
# tools=[...] as a NodeTool, deriving the tool declaration from `description`
# and `input_schema`.
# See https://github.com/google/adk-python/blob/v2.6.2/contributing/samples/workflows/node_as_tool/agent.py

support_agent = LlmAgent(
    name="SupportDesk",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are a support desk. Call triage_workflow with the customer's "
        "ticket text, then report its outcome in one short sentence."
    ),
    tools=[triage_workflow],
)


async def run_agent(query: str) -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="agent_demo", user_id="user", session_id="s1"
    )
    runner = Runner(
        agent=support_agent, app_name="agent_demo", session_service=session_service
    )

    message = types.Content(role="user", parts=[types.Part(text=query)])
    final_text = ""
    async for event in runner.run_async(
        user_id="user", session_id="s1", new_message=message
    ):
        for call in event.get_function_calls():
            print(f"    tool call:   {call.name}({dict(call.args)})")
        # Events are stamped with the node that produced them; the agent itself
        # is one node, the graph's nodes are the others.
        node_name = getattr(event, "node_name", None)
        is_graph_node = node_name is not None and node_name != support_agent.name
        if is_graph_node:
            print(f"    node {node_name:<13} ran inside the tool")
        for response in event.get_function_responses():
            print(f"    tool result: {response.response}")
        if (
            not is_graph_node
            and event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_text = event.content.parts[0].text
    print(f"\n  Agent: {final_text.strip()}")


print_new_section("2. The same Workflow used as an LlmAgent tool")

query = "Ticket: I was charged twice on invoice 88, please help."
print(f"  Query: {query}\n")
asyncio.run(run_agent(query))

print(
    f"\n  Tool declaration derived from the Workflow:"
    f"\n    name:        {support_agent.tools[0].name}"
    f"\n    description: {support_agent.tools[0].description}"
    f"\n    input:       {list(Ticket.model_fields)}"
)
