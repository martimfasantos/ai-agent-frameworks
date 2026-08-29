# LlamaIndex

- Repo: https://github.com/run-llama/llama_index
- Documentation: https://developers.llamaindex.ai/
- Version: **0.14.23**

## What is LlamaIndex?

LlamaIndex (formerly GPT Index) is a data framework for LLM applications. It provides tools to build agentic systems with a focus on Retrieval-Augmented Generation (RAG). 

This folder contains **simple and straightforward examples** that demonstrate LlamaIndex's core features. Each example is focused, minimal, and easy to understand.

Key strengths include:
- **RAG-first architecture**: Built for document-based reasoning and retrieval
- **Event-driven workflows**: Flexible, composable workflow orchestration
- **Agent tools**: Function calling and query engines as tools
- **Memory management**: Conversation history and context persistence
- **Streaming**: First-class streaming support for tokens and events
- **Community tools**: 40+ integrations available via LlamaHub

## LlamaIndex Examples

### How to setup

#### Create a virtual environment and install dependencies

Run the following command to create a virtual environment and install dependencies using UV:

```bash
uv sync
```

Alternatively, use UV to run files directly without manual activation:
```bash
uv run <example_name>.py
```

#### .env

See .env.example and create a .env (on the root of the repository).
You need to get an OpenAI endpoint and key and fill them in.

### Example Progression

**Core Fundamentals** (Required):
- `00_hello_world.py` - Basic RAG with document loading and querying
- `01_tools.py` - Function calling agents with custom tools
- `02_structured_outputs.py` - Enforcing response schemas with Pydantic
- `03_memory.py` - Conversation memory and context management
- `04_streaming.py` - Real-time event and token streaming
- `05_memory_advanced.py` - Memory with initial_messages for persistent context

**Agent Capabilities** (Recommended):
- `06_agent_types.py` - ReAct, Function Calling and CodeAct agents side by side
- `07_multi_modal_agents.py` - Vision agents for image understanding
- `08_manual_agents.py` - Manual agent control with step execution
- `09_agent_delegation.py` - Wrapping agents as tools for delegation
- `10_agentic_rag.py` - Multiple query engines with intelligent tool selection
- `11_agent_workflows.py` - Corrective RAG workflow combining retrieval and reasoning
- `12_agent_human_in_the_loop.py` - A tool that pauses on `ctx.wait_for_event()` for approval
- `13_multi_agent_handoff.py` - `AgentWorkflow` handoffs with `can_handoff_to` and shared state
- `14_mcp_tools.py` - Consuming MCP tools, and publishing a workflow as an MCP server

### Examples

| # | File | Topics |
|---|------|--------|
| 00 | `00_hello_world.py` | FunctionAgent, basic run |
| 01 | `01_tools.py` | Function calling with custom tools |
| 02 | `02_structured_outputs.py` | `output_cls`, `structured_output_fn`, `AgentStreamStructuredOutput` |
| 03 | `03_memory.py` | Conversation memory and context |
| 04 | `04_streaming.py` | Event and token streaming |
| 05 | `05_memory_advanced.py` | Memory blocks, `initial_messages` |
| 06 | `06_agent_types.py` | ReActAgent, FunctionAgent, CodeActAgent |
| 07 | `07_multi_modal_agents.py` | Vision agents |
| 08 | `08_manual_agents.py` | Manual step execution |
| 09 | `09_agent_delegation.py` | Agents as tools |
| 10 | `10_agentic_rag.py` | `QueryEngineTool`, vector vs summary engines |
| 11 | `11_agent_workflows.py` | Custom Workflow, retrieve/grade/rewrite loop |
| 12 | `12_agent_human_in_the_loop.py` | `ctx.wait_for_event`, `InputRequiredEvent`, `requirements` |
| 13 | `13_multi_agent_handoff.py` | `AgentWorkflow`, `can_handoff_to`, `initial_state` |
| 14 | `14_mcp_tools.py` | `BasicMCPClient`, `McpToolSpec`, `workflow_as_mcp` |

### Run examples

```bash
uv run 00_hello_world.py
uv run 01_tools.py
uv run 02_structured_outputs.py
uv run 03_memory.py
uv run 04_streaming.py
uv run 05_memory_advanced.py
uv run 06_agent_types.py
uv run 07_multi_modal_agents.py
uv run 08_manual_agents.py
uv run 09_agent_delegation.py
uv run 10_agentic_rag.py
uv run 11_agent_workflows.py
uv run 12_agent_human_in_the_loop.py
uv run 13_multi_agent_handoff.py
uv run 14_mcp_tools.py

# Workflow examples (run from this directory)
uv run agent_workflows/01_gettings_started.py
uv run agent_workflows/02_branches_and_loops.py
uv run agent_workflows/03_managing_state.py
uv run agent_workflows/04_streaming.py
uv run agent_workflows/05_concurrent_execution.py
uv run agent_workflows/06_human_in_the_loop.py
uv run agent_workflows/07_customizing_entry_exit_points.py
uv run agent_workflows/08_drawing_workflow.py
uv run agent_workflows/09_resource_objects.py
uv run agent_workflows/10_retry_steps_execution.py
uv run agent_workflows/11_workflow_as_a_server.py
uv run agent_workflows/12_observability.py
uv run agent_workflows/13_error_recovery.py
uv run agent_workflows/14_durable_workflows.py
uv run agent_workflows/15_testing_workflows.py
```

### Workflow Examples (agent_workflows/)

**Getting Started**:
- `01_gettings_started.py` - Basic workflow with events and steps
- `02_branches_and_loops.py` - Conditional branching and looping patterns

**State & Data Flow**:
- `03_managing_state.py` - Context state (typed/untyped, locking, persistence)
- `04_streaming.py` - Streaming progress events and handling termination
- `05_concurrent_execution.py` - `list[Event]` fan-out/fan-in, `Collect(Take(n))`, dynamic API

**Advanced Patterns**:
- `06_human_in_the_loop.py` - InputRequiredEvent for human interaction
- `07_customizing_entry_exit_points.py` - Custom StartEvent/StopEvent for type safety
- `08_drawing_workflow.py` - Visualizing workflows (HTML, Mermaid, agent handoff graphs)
- `09_resource_objects.py` - Dependency injection with Resource/ResourceConfig
- `10_retry_steps_execution.py` - Composable retry policies with `retry_policy()`
- `11_workflow_as_a_server.py` - Exposing workflows via HTTP API
- `12_observability.py` - OpenTelemetry tracing and observability tools
- `13_error_recovery.py` - `@catch_error`, `StepFailedEvent`, `Context.retry_info()`
- `14_durable_workflows.py` - Snapshot with `ctx.to_dict()`, resume with `Context.from_dict()`
- `15_testing_workflows.py` - `WorkflowTestRunner` for end-to-end workflow tests

### Key LlamaIndex Differentiators

| Aspect | LlamaIndex Specialty |
|--------|----------------------|
| **Document Processing** | Native RAG with indices, chunking, metadata |
| **Query Flexibility** | Router engines, multiple query strategies |
| **Memory System** | Sophisticated blocks with semantic memory |
| **Workflows** | Event-driven with full custom control |
| **Community** | 40+ tools via LlamaHub ecosystem |
| **Streaming** | First-class event + token streaming |
| **Enterprise** | LlamaParse for complex documents, multimodal support |

### Key dependencies

| Package | Version |
|---------|---------|
| `llama-index` / `llama-index-core` | 0.14.23 |
| `llama-index-workflows` | 2.23.0 |
| `llama-agents-server` | 0.7.0 |
| `llama-index-utils-workflow` | 0.11.0 |
| `llama-index-llms-openai` | 0.7.10 |
| `llama-index-tools-mcp` | 0.4.8 |

### Documentation References

- Main Docs: https://developers.llamaindex.ai/
- Agents Guide: https://developers.llamaindex.ai/python/framework/use_cases/agents/
- Workflows: https://developers.llamaindex.ai/python/llamaagents/workflows/
- Workflow API Reference: https://developers.llamaindex.ai/python/workflows-api-reference/
- Memory: https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/memory/
- Streaming: https://developers.llamaindex.ai/python/framework/understanding/agent/streaming/
- LlamaHub: https://llamahub.ai/
