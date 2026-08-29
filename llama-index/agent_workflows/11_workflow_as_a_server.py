import asyncio
from workflows import Workflow, step
from workflows.context import Context
from workflows.events import Event, StartEvent, StopEvent
from llama_agents.server import WorkflowServer


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- Exposing workflows over HTTP with WorkflowServer
- Running the server programmatically or via CLI
- Workflow Debugger UI for visualization and debugging
- Streaming events via SSE or NDJSON
- Sending events to running workflows (human-in-the-loop via API)
- Canceling workflow runs
- Opting into the context API with accept_context_api=True
- Using WorkflowClient for programmatic server interaction

The WorkflowServer class exposes workflows over a RESTful HTTP API.
It includes a debugger UI at the root / path for visualizing, running,
and debugging workflows in real time. Workflows can be run synchronously
(/workflows/{name}/run) or asynchronously (/workflows/{name}/run-nowait),
with events streamed via /events/{handler_id}. The WorkflowClient provides
a Python interface for listing workflows, running them, streaming events,
and sending human-in-the-loop responses programmatically.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/deployment/
https://developers.llamaindex.ai/python/llamaagents/workflows/client/
-------------------------------------------------------
"""


# --- 1. Define a streaming event and a simple workflow ---
class StreamEvent(Event):
    sequence: int


class GreetingWorkflow(Workflow):
    @step
    async def greet(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """Greet the user, streaming progress events"""
        for i in range(3):
            ctx.write_event_to_stream(StreamEvent(sequence=i))
            await asyncio.sleep(0.3)

        name = ev.get("name", "World")
        return StopEvent(result=f"Hello, {name}!")


# --- 2. Create a WorkflowServer and add workflows ---
greet_wf = GreetingWorkflow()

# Since llama-agents-server 0.4.0 the context API is opt-in: without
# accept_context_api=True a run request carrying a "context" field is rejected
# with a 400 ("Context API is disabled").
server = WorkflowServer(accept_context_api=True)
server.add_workflow("greet", greet_wf)


# --- 3. Run the server programmatically ---
async def main():
    await server.serve(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    asyncio.run(main())

# --- 4. Run the server via CLI ---
# Run the server with:
#   uv run 11_workflow_as_a_server.py
#
# The server starts on 0.0.0.0:8080 by default.
# Configure with WORKFLOWS_PY_SERVER_HOST and WORKFLOWS_PY_SERVER_PORT env vars.

# --- 5. Debugger UI ---
# Open http://localhost:8080 to see the Workflow Debugger UI.
# Features: workflow visualization, event logging, human-in-the-loop support,
# multiple runs tracking, and automatic schema detection.

# --- 6. API Endpoints (as reported by server.openapi_schema()) ---
# GET  /health                       → {"status": "healthy"}
# GET  /workflows                    → list of registered workflow names
# GET  /workflows/{name}/schema      → JSON schema of the start/stop events
# GET  /workflows/{name}/events      → event types the workflow can emit
# GET  /workflows/{name}/representation → structure for the debugger UI
# POST /workflows/{name}/run         → run synchronously, returns result
# POST /workflows/{name}/run-nowait  → run async, returns handler_id
# GET  /events/{handler_id}          → stream events (SSE or NDJSON)
# POST /events/{handler_id}          → send an event (human-in-the-loop)
# GET  /handlers                     → list all handlers (running + completed)
# GET  /handlers/{handler_id}        → handler status
# GET  /results/{handler_id}         → workflow result (202 if still running)
# POST /handlers/{handler_id}/cancel → cancel a running workflow