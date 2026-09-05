import os
import asyncio
import logging
from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps import App
from google.adk.plugins import BasePlugin, ReflectAndRetryModelPlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from settings import settings
from utils import print_new_section

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

# Section 2 deliberately raises inside a tool. ADK logs the resulting traceback
# at ERROR level; silence it so the plugin hook output stays readable.
logging.getLogger("google_adk").setLevel(logging.CRITICAL)

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- BasePlugin: runner-global cross-cutting logic registered once, applied everywhere
- App(plugins=[...]) and Runner(plugins=[...]): the two registration points
- on_agent_error_callback / on_run_error_callback: the error notification hooks
- ReflectAndRetryModelPlugin: built-in self-healing recovery from model errors

Plugins are the runner-level counterpart of the per-agent callbacks in
06_callbacks.py. A callback is attached to one agent and fires only for that
agent; a plugin is registered once on the App (or Runner) and its hooks fire
for every agent, tool and invocation underneath it — which is what you want
for logging, auditing, metrics or policy enforcement.

For more details, visit:
https://adk.dev/plugins/
-------------------------------------------------------
"""


# ----------------------------------------------------------------
#                    1. Define a custom plugin
# ----------------------------------------------------------------
# Every hook is optional — override only the ones you need. Hooks that return
# a value can short-circuit execution, but the two error hooks below are
# notification-only: ADK always re-raises the exception after notifying.


class AuditPlugin(BasePlugin):
    """Records every invocation, agent and tool the runner touches."""

    def __init__(self, name: str = "audit_plugin") -> None:
        super().__init__(name=name)
        self.events: list[str] = []

    def _log(self, message: str) -> None:
        self.events.append(message)
        print(f"  [plugin:{self.name}] {message}")

    async def before_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> Optional[types.Content]:
        self._log(f"invocation started (root agent: {invocation_context.agent.name})")
        return None

    async def on_user_message_callback(
        self,
        *,
        invocation_context: InvocationContext,
        user_message: types.Content,
    ) -> Optional[types.Content]:
        text = user_message.parts[0].text if user_message.parts else ""
        self._log(f"user message: '{text}'")
        return None

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> Optional[types.Content]:
        self._log(f"agent starting: {agent.name}")
        return None

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ) -> Optional[dict[str, Any]]:
        self._log(f"tool call: {tool.name}({tool_args})")
        return None

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        result: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        self._log(f"tool result: {tool.name} -> {result}")
        return None

    # --- New in ADK 2.5.0: error notification hooks ---

    async def on_agent_error_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext, error: Exception
    ) -> None:
        self._log(
            f"AGENT ERROR in {agent.name}: {type(error).__name__}: {error} "
            "(notification only — ADK re-raises)"
        )

    async def on_run_error_callback(
        self, *, invocation_context: InvocationContext, error: Exception
    ) -> None:
        self._log(
            f"RUN ERROR: {type(error).__name__}: {error} "
            "(notification only — ADK re-raises)"
        )

    async def after_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> None:
        self._log("invocation finished")


# One plugin instance is shared by both sections below to show that the same
# cross-cutting logic covers different agents without touching them.
audit_plugin = AuditPlugin()

# Built-in plugin (new in ADK 2.6.0): if the model returns a malformed function
# call, it feeds the error back to the model as reflection guidance and retries
# the turn, up to max_retries times.
retry_plugin = ReflectAndRetryModelPlugin(max_retries=2)


# ----------------------------------------------------------------
#         2. App(plugins=[...]) — plugin hooks vs. agent callbacks
# ----------------------------------------------------------------


def get_stock_level(sku: str) -> dict[str, Any]:
    """Returns the warehouse stock level for a product SKU."""
    stock = {"SKU-100": 42, "SKU-200": 0}
    return {"sku": sku, "units": stock.get(sku, 7)}


def agent_local_before_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """A per-agent callback — fires only for the agent it is attached to."""
    print(f"  [agent-callback] before_agent on {callback_context.agent_name}")
    return None


inventory_agent = LlmAgent(
    name="InventoryAgent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You answer stock questions using the get_stock_level tool. "
        "Reply in exactly one short sentence."
    ),
    tools=[get_stock_level],
    before_agent_callback=agent_local_before_agent,
)

# Plugins are registered on the App, so they cover every agent it contains.
inventory_app = App(
    name="plugin_demo",
    root_agent=inventory_agent,
    plugins=[audit_plugin, retry_plugin],
)


async def run(app_or_agent, query: str) -> None:
    """Runs one invocation, printing the final answer or the raised error."""
    session_service = InMemorySessionService()
    if isinstance(app_or_agent, App):
        await session_service.create_session(
            app_name=app_or_agent.name, user_id="user", session_id="s1"
        )
        runner = Runner(app=app_or_agent, session_service=session_service)
    else:
        # Runner(plugins=[...]) is the alternative registration point when you
        # do not wrap the agent in an App.
        await session_service.create_session(
            app_name="plugin_demo", user_id="user", session_id="s1"
        )
        runner = Runner(
            agent=app_or_agent,
            app_name="plugin_demo",
            session_service=session_service,
            plugins=[audit_plugin],
        )

    message = types.Content(role="user", parts=[types.Part(text=query)])
    try:
        async for event in runner.run_async(
            user_id="user", session_id="s1", new_message=message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"\n  Final answer: {event.content.parts[0].text.strip()}")
    except Exception as error:
        print(f"\n  Exception reached the caller: {type(error).__name__}: {error}")


print_new_section("1. App(plugins=[...]): plugin hooks vs. agent callbacks")

print("Query: How many units of SKU-100 do we have?\n")
asyncio.run(run(inventory_app, "How many units of SKU-100 do we have?"))
print(
    "\n  Note: [agent-callback] fired once, only for InventoryAgent."
    "\n        [plugin:audit_plugin] saw the whole invocation — run, agent, tool."
)


# ----------------------------------------------------------------
#      3. Runner(plugins=[...]) — the 2.5.0 error hooks in action
# ----------------------------------------------------------------
# The same plugin instance, a different agent that has no callbacks of its own,
# and a tool that always raises. The exception travels
# tool -> on_agent_error_callback -> on_run_error_callback -> caller.


def charge_card(order_id: str) -> dict[str, Any]:
    """Charges the customer's card for an order."""
    raise RuntimeError(f"payment gateway timed out for {order_id}")


payment_agent = LlmAgent(
    name="PaymentAgent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="Charge the card for the order the user names using charge_card.",
    tools=[charge_card],
)

print_new_section("2. Runner(plugins=[...]): on_agent_error / on_run_error")

print("Query: Charge the card for order ORD-7 (the tool will raise)\n")
asyncio.run(run(payment_agent, "Charge the card for order ORD-7."))
print(
    "\n  Note: both error hooks fired for PaymentAgent, which declares no"
    "\n        callbacks at all — and the RuntimeError still reached the caller,"
    "\n        because both hooks are notification-only."
)


# ----------------------------------------------------------------
#            4. ReflectAndRetryModelPlugin configuration
# ----------------------------------------------------------------
# Registered on inventory_app above, so it was active during section 1. It is a
# standby recovery plugin: it only acts when the model itself fails, so a
# healthy run like section 1 produces no output from it.

print_new_section("3. ReflectAndRetryModelPlugin (built-in, ADK 2.6.0)")

print(f"  name:                             {retry_plugin.name}")
print(f"  max_retries:                      {retry_plugin.max_retries}")
print(f"  throw_exception_if_retry_exceeded: {retry_plugin.throw_exception_if_retry_exceeded}")
print(f"  tracking_scope:                   {retry_plugin.scope.value}")
print(f"  on_model_errors:                  {[r.name for r in retry_plugin.on_model_errors]}")
print(
    "\n  On a tracked model error it injects reflection guidance and re-runs the"
    "\n  turn; after max_retries consecutive failures it raises RuntimeError."
    "\n  Section 1's model behaved, so it stayed silent."
)

print_new_section("Summary")

print(f"  Plugins registered on the App: {[p.name for p in inventory_app.plugins]}")
print(f"  Hook events recorded by the one shared AuditPlugin instance: {len(audit_plugin.events)}")
print("  Agents covered without any per-agent wiring: InventoryAgent, PaymentAgent")
