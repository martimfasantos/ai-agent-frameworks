from strands import Agent, InterventionHandler, tool
from strands.hooks import BeforeToolCallEvent
from strands.interventions import Deny, Guide, Proceed, Transform
from strands.models.openai import OpenAIModel

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- Agent(interventions=[...]) — the intervention control plane (new in v1.44.0)
- Subclassing InterventionHandler and overriding before_tool_call
- Returning the typed actions Proceed, Deny, Guide, and Transform
- Short-circuiting on Deny and feedback accumulation across handlers

Interventions are the documented way to do authorization and guardrails.
Unlike hooks (see 09_hooks.py), which mutate the event object directly, an
intervention handler RETURNS a typed decision and the framework applies it —
blocking the call, feeding guidance back to the model, or rewriting arguments.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/interventions/
-------------------------------------------------------
"""

RESTRICTED_TABLES = {"salaries", "ssn"}
KNOWN_METRICS = {"revenue", "signups", "churn"}
SANDBOX_CHANNEL = "#ops-sandbox"


# --- 1. Define tools that need guarding ---
@tool
def query_database(table: str) -> str:
    """Read all rows from a table.

    Args:
        table: Name of the table to read.
    """
    return f"3 rows returned from '{table}'"


@tool
def get_metric(name: str) -> str:
    """Look up the current value of a business metric.

    Args:
        name: Metric name.
    """
    return f"{name} = 42"


@tool
def send_notification(channel: str, message: str) -> str:
    """Post a message to a chat channel.

    Args:
        channel: Channel to post into (e.g. '#production').
        message: Message body.
    """
    return f"posted to {channel}: {message}"


# --- 2. An intervention handler returning all four action types ---
class AccessPolicy(InterventionHandler):
    """Authorization and argument policy applied before every tool call."""

    name = "access-policy"

    def before_tool_call(self, event: BeforeToolCallEvent, **kwargs) -> object:
        tool_name = event.tool_use["name"]
        tool_input = event.tool_use.get("input", {})

        if tool_name == "query_database" and tool_input.get("table") in RESTRICTED_TABLES:
            print(f"  [access-policy] Deny -> {tool_name}(table={tool_input.get('table')!r})")
            return Deny(reason="Table contains PII and is not readable by this agent.")

        if tool_name == "get_metric" and tool_input.get("name") not in KNOWN_METRICS:
            print(f"  [access-policy] Guide -> {tool_name}(name={tool_input.get('name')!r})")
            return Guide(feedback=f"Unknown metric. Valid names: {sorted(KNOWN_METRICS)}.")

        if tool_name == "send_notification" and tool_input.get("channel") != SANDBOX_CHANNEL:
            original = tool_input.get("channel")
            print(f"  [access-policy] Transform -> rewrite channel {original!r} to {SANDBOX_CHANNEL!r}")

            def redirect(e: BeforeToolCallEvent) -> None:
                e.tool_use["input"]["channel"] = SANDBOX_CHANNEL

            return Transform(apply=redirect)

        print(f"  [access-policy] Proceed -> {tool_name}")
        return Proceed()


# --- 3. A second handler, registered after the first, to show short-circuiting ---
class AuditTrail(InterventionHandler):
    """Records every tool call that survives the policy handler."""

    name = "audit-trail"

    def __init__(self) -> None:
        self.recorded: list[str] = []

    def before_tool_call(self, event: BeforeToolCallEvent, **kwargs) -> object:
        tool_name = event.tool_use["name"]
        self.recorded.append(tool_name)
        print(f"  [audit-trail]   saw {tool_name}")
        return Proceed()


# --- 4. Create the agent with both interventions ---
openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)

audit = AuditTrail()
agent = Agent(
    model=openai_model,
    system_prompt="You are an ops assistant. Use the tools. Answer in one short sentence.",
    tools=[query_database, get_metric, send_notification],
    interventions=[AccessPolicy(), audit],
    callback_handler=None,
)

print("=== Interventions: Typed Decisions on Tool Calls ===\n")

# --- 5. Deny: the call is blocked and the model is told why ---
print("--- Deny: reading a restricted table ---")
result = agent("Read every row from the salaries table.")
print(f"Agent: {result.message['content'][0]['text']}\n")

# --- 6. Guide: the call is cancelled with feedback so the model retries ---
print("--- Guide: a misspelled metric name ---")
result = agent("What is the current value of the 'revenu' metric?")
print(f"Agent: {result.message['content'][0]['text']}\n")

# --- 7. Transform: the arguments are rewritten before the tool runs ---
print("--- Transform: rewriting a tool argument ---")
result = agent("Notify #production that the deploy finished.")
print(f"Agent: {result.message['content'][0]['text']}\n")

# --- 8. Summary ---
print("--- Summary ---")
print(f"Tool calls reaching audit-trail: {audit.recorded}")
print("  query_database was denied, so the second handler never saw it.\n")
print("Interventions vs hooks (09_hooks.py):")
print("  hooks         -> callbacks that MUTATE the event (event.cancel_tool = ...)")
print("  interventions -> handlers that RETURN a decision the framework applies")
print("  Deny short-circuits remaining handlers; Guides from several handlers")
print("  accumulate into one feedback message; conflicts resolve by precedence.")
