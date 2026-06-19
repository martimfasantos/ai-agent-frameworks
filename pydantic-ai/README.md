# Pydantic AI

- Repo: https://github.com/pydantic/pydantic-ai
- Documentation: https://ai.pydantic.dev/

Pydantic AI is a Python agent framework built by the creators of Pydantic. It provides a type-safe, model-agnostic way to build AI agents with structured outputs, tool use, dependency injection, streaming, multi-agent patterns, graph-based workflows, and more.

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

### 3. Run an example

```bash
uv run python 00_hello_world.py
```

## Examples

| File | Feature | Description |
|------|---------|-------------|
| `00_hello_world.py` | Hello World | Simplest possible agent — one question, one answer |
| `01_tools_and_metrics.py` | Custom Tools & Metrics | Tool decorators, Tool objects, RunContext, usage tracking and limits |
| `02_dependencies.py` | Dependency Injection | Typed deps via `deps_type`, dynamic system prompts and tools via `RunContext` |
| `03_built_in_tools.py` | Built-in Tools | WebSearchTool, CodeExecutionTool with OpenAI Responses API |
| `04_structured_outputs.py` | Structured Outputs | Pydantic model outputs, union types, ToolOutput/NativeOutput/PromptedOutput modes |
| `05_output_validators.py` | Output Validators | `@agent.output_validator`, ModelRetry for automatic retries, partial output validation |
| `06_output_functions.py` | Output Functions | TextOutput wrapper for post-processing, function-based output types |
| `07_streaming.py` | Streaming | `run_stream`, `run_stream_events`, custom event stream handlers |
| `08_message_history.py` | Message History | Multi-turn conversations, JSON serialization, history processors |
| `09_agent_delegation.py` | Agent Delegation | Agent-as-tool pattern, shared usage tracking across agents |
| `10_programmatic_handoff.py` | Programmatic Handoff | Sequential agents orchestrated by application code, shared message history |
| `11_toolsets.py` | Toolsets | FunctionToolset, PrefixedToolset, FilteredToolset, CombinedToolset |
| `12_mcp_client.py` | MCP Client | Connect to MCP servers via stdio transport for external tool access |
| `13_agent_iteration.py` | Agent Iteration | `agent.iter()` for step-by-step control over the agent execution loop |
| `14_stateful_graphs.py` | Stateful Graphs | `pydantic_graph` state machines with typed nodes and transitions |
| `15_graphs_with_genai.py` | Graphs + GenAI | LLM-powered graph nodes with feedback loops (content review pipeline) |
| `16_human_in_the_loop.py` | Human-in-the-Loop | Deferred tool approval with `DeferredToolRequests` and `ToolApproved`/`ToolDenied` |
| `17_evals.py` | Evaluation | `pydantic-evals` Dataset, Case, and evaluate_sync for systematic agent testing |
| `18_a2a.py` | A2A Protocol | Expose agents as A2A-compatible HTTP servers with `agent.to_a2a()` |
| `19_capabilities.py` | Capabilities | Composable behavior units: built-in Thinking/Hooks, custom capabilities with tools and instructions |
| `20_agent_spec.py` | Agent Spec | Declarative agent definitions via YAML/JSON/dict with `AgentSpec` and `Agent.from_spec()` |
| `21_tool_choice.py` | Tool Choice | Control tool calling behavior with `tool_choice` model setting (`auto`, `required`, `none`) |
| `22_advanced_capabilities.py` | Advanced Capabilities | CombinedCapability, CapabilityOrdering, PrepareTools, and `output_retries` |
| `23_tool_search.py` | Tool Search | Deferred tool loading with `defer_loading=True`, native provider tool search |

## Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pydantic-ai` | 1.104.0 | Core agent framework |
| `pydantic-ai-slim[a2a]` | 1.104.0 | A2A protocol support (required for `18_a2a.py`) |
| `pydantic-evals` | >=0.2.0 | Evaluation framework (required for `17_evals.py`) |
| `pydantic-graph` | >=0.2.0 | Graph/FSM library (required for `14_stateful_graphs.py`, `15_graphs_with_genai.py`) |
| `pydantic` | >=2.10.0 | Data validation and structured output schemas |
| `pydantic-settings` | >=2.7.0 | `.env` file loading via `BaseSettings` |
| `openai` | >=1.60.0 | OpenAI API client |
| `mcp` | >=1.0.0 | MCP protocol client (required for `12_mcp_client.py`) |
| `uvicorn` | >=0.30.0 | ASGI server (required for `18_a2a.py`) |

## Notes

- **Built-in tools** (`03_built_in_tools.py`) require the OpenAI Responses API (`OpenAIResponsesModel`), not the default Chat Completions API.
- **MCP client** (`12_mcp_client.py`) requires Node.js and an MCP server binary. The example exits gracefully if unavailable.
- **A2A** (`18_a2a.py`) starts an HTTP server — run it standalone and test with curl.
- **Graphs** (`14_stateful_graphs.py`) use `pydantic_graph`, which is a standalone library with no dependency on `pydantic-ai`.
