# LlamaIndex Agent Workflows Examples

This directory contains examples demonstrating various features of LlamaIndex Workflows. Each example is self-contained and showcases a specific workflow capability.

## Overview

Workflows in LlamaIndex provide a flexible way to orchestrate complex multi-step operations with features like branching, looping, state management, concurrency, and more.

## Examples

| # | File | Features | Documentation |
|---|------|----------|---------------|
| 01 | `01_gettings_started.py` | Events, steps, a first workflow | [getting_started](https://developers.llamaindex.ai/python/llamaagents/workflows/) |
| 02 | `02_branches_and_loops.py` | Conditional branching, loops, termination | [branches_and_loops](https://developers.llamaindex.ai/python/llamaagents/workflows/branches_and_loops/) |
| 03 | `03_managing_state.py` | Untyped/typed state, locking, persistence | [managing_state](https://developers.llamaindex.ai/python/llamaagents/workflows/managing_state/) |
| 04 | `04_streaming.py` | `write_event_to_stream()`, token streaming, termination events | [streaming](https://developers.llamaindex.ai/python/llamaagents/workflows/streaming/) |
| 05 | `05_concurrent_execution.py` | `list[Event]` fan-out/fan-in, `Collect(Take(n))`, multi-parameter joins, `num_workers`, dynamic `send_event`/`collect_events` | [concurrent_execution](https://developers.llamaindex.ai/python/llamaagents/workflows/concurrent_execution/) |
| 06 | `06_human_in_the_loop.py` | `InputRequiredEvent`, `HumanResponseEvent`, stop/resume | [human_in_the_loop](https://developers.llamaindex.ai/python/llamaagents/workflows/human_in_the_loop/) |
| 07 | `07_customizing_entry_exit_points.py` | Custom `StartEvent` / `StopEvent` for type safety | [customizing_entry_exit_points](https://developers.llamaindex.ai/python/llamaagents/workflows/customizing_entry_exit_points/) |
| 08 | `08_drawing_workflow.py` | HTML and Mermaid renderers, `draw_agent_workflow` | [drawing](https://developers.llamaindex.ai/python/llamaagents/workflows/drawing/) |
| 09 | `09_resource_objects.py` | `Resource` / `ResourceConfig` dependency injection | [resources](https://developers.llamaindex.ai/python/llamaagents/workflows/resources/) |
| 10 | `10_retry_steps_execution.py` | `retry_policy(retry=, wait=, stop=)` composed from primitives | [retry_steps](https://developers.llamaindex.ai/python/llamaagents/workflows/retry_steps/) |
| 11 | `11_workflow_as_a_server.py` | `WorkflowServer`, HTTP API, debugger UI, `accept_context_api` | [deployment](https://developers.llamaindex.ai/python/llamaagents/workflows/deployment/) |
| 12 | `12_observability.py` | OpenTelemetry tracing, `verbose=True` step logging | [observability](https://developers.llamaindex.ai/python/llamaagents/workflows/observability/) |
| 13 | `13_error_recovery.py` | `@catch_error`, `StepFailedEvent`, `Context.retry_info()`, `max_recoveries` | [retry_steps](https://developers.llamaindex.ai/python/llamaagents/workflows/retry_steps/) |
| 14 | `14_durable_workflows.py` | `ctx.to_dict()` / `Context.from_dict()`, `StepStateChanged`, `Resource` | [durable_workflows](https://developers.llamaindex.ai/python/llamaagents/workflows/durable_workflows/) |
| 15 | `15_testing_workflows.py` | `WorkflowTestRunner`, `.collected` / `.event_types` / `.ctx` | [testing](https://developers.llamaindex.ai/python/llamaagents/workflows/testing/) |

## Running the Examples

Run them from the parent `llama-index/` directory so `settings.py` and `res/` resolve:

```bash
cd llama-index
uv run agent_workflows/01_gettings_started.py
uv run agent_workflows/05_concurrent_execution.py
# ... etc
```

`08_drawing_workflow.py` writes its diagrams into `llama-index/res/`.
`11_workflow_as_a_server.py` serves on `0.0.0.0:8080` until interrupted.

## Prerequisites

Make sure you have the required dependencies installed:

```bash
# Install LlamaIndex workflows
pip install llama-index-core workflows

# For OpenAI examples
pip install llama-index-llms-openai

# For visualization (optional)
pip install llama-index-utils-workflow

# For observability (optional)
pip install llama-index-observability-otel
```

## Environment Setup

Some examples require API keys. Set up your environment:

```bash
# Create a .env file or export directly
export OPENAI_API_KEY="your-api-key-here"
```

Or configure in `settings.py` as used throughout the llama-index examples.

## Learn More

- **Official Documentation:** https://developers.llamaindex.ai/python/llamaagents/workflows/
- **API Reference:** https://developers.llamaindex.ai/python/workflows-api-reference/
- **LlamaIndex Main Docs:** https://docs.llamaindex.ai/

## Contributing

These examples follow the structure established in the parent directory's examples (e.g., `00_hello_world.py`, `01_tools.py`). Each file includes:

- Clear docstring explaining the example
- Feature list with bullet points
- Link to official documentation
- Simple, runnable code
- Educational comments
