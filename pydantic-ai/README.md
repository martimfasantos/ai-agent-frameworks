# Pydantic AI

Version: **2.24.0**

- Repo: https://github.com/pydantic/pydantic-ai
- Documentation: https://pydantic.dev/docs/ai/overview/

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
OPENAI_MODEL_NAME=openai-chat:gpt-4o-mini
```

> Pydantic AI v2 removed bare model names — the provider prefix is now required, and
> an unprefixed name raises a `UserError`. `openai-chat:` selects the Chat Completions
> API (what these examples used before v2); `openai-responses:` — which is also what a
> bare `openai:` now means — selects the Responses API.

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
| `03_built_in_tools.py` | Native Tools | WebSearchTool, CodeExecutionTool via the `NativeTool` capability (Responses API) |
| `04_structured_outputs.py` | Structured Outputs | Pydantic model outputs, union types, ToolOutput/NativeOutput/PromptedOutput modes |
| `05_output_validators.py` | Output Validators | `@agent.output_validator`, ModelRetry for automatic retries, partial output validation |
| `06_output_functions.py` | Output Functions | TextOutput wrapper for post-processing, function-based output types |
| `07_streaming.py` | Streaming | `run_stream`, `run_stream_events`, custom event stream handlers |
| `08_message_history.py` | Message History | Multi-turn conversations, JSON serialization, the `ProcessHistory` capability |
| `09_agent_delegation.py` | Agent Delegation | Agent-as-tool pattern, shared usage tracking across agents |
| `10_programmatic_handoff.py` | Programmatic Handoff | Sequential agents orchestrated by application code, shared message history |
| `11_toolsets.py` | Toolsets | FunctionToolset, PrefixedToolset, FilteredToolset, CombinedToolset |
| `12_mcp_client.py` | MCP Client | `MCPToolset` against an in-process FastMCP server, namespaced with `PrefixedToolset` |
| `13_agent_iteration.py` | Agent Iteration | `agent.iter()` for step-by-step control over the agent execution loop |
| `14_stateful_graphs.py` | Stateful Graphs | `GraphBuilder` steps, decision routing, cycles, and `Graph.render()` |
| `15_graphs_with_genai.py` | Graphs + GenAI | Agents inside `GraphBuilder` steps with a revision feedback loop |
| `16_human_in_the_loop.py` | Human-in-the-Loop | Deferred tool approval with `DeferredToolRequests` and `ToolApproved`/`ToolDenied` |
| `17_evals.py` | Evaluation | `pydantic-evals` Dataset, Case, and evaluate_sync for systematic agent testing |
| `18_a2a.py` | A2A Protocol | Expose agents as A2A-compatible HTTP servers with `fasta2a.pydantic_ai.agent_to_a2a()` |
| `19_capabilities.py` | Capabilities | Composable behavior units: built-in Thinking/Hooks, custom capabilities with tools and instructions |
| `20_agent_spec.py` | Agent Spec | Declarative agent definitions via YAML/JSON/dict with `AgentSpec` and `Agent.from_spec()` |
| `21_tool_choice.py` | Tool Choice | Control tool calling behavior with `tool_choice` model setting (`auto`, `required`, `none`) |
| `22_advanced_capabilities.py` | Advanced Capabilities | CombinedCapability, CapabilityOrdering, PrepareTools, and `retries={'output': N}` |
| `23_tool_search.py` | Tool Search | Deferred tool loading with `defer_loading=True`, native provider tool search |
| `24_cost_and_usage_limits.py` | Cost & Usage Limits | `RunUsage.cost`, `UsageLimits(cost_limit=)`, `per_request_input_tokens_limit` |
| `25_agentic_evals.py` | Agentic Evals | ToolCorrectness, TrajectoryMatch, ArgumentCorrectness, MaxToolCalls, GEval |
| `26_tool_failures.py` | Tool Failures | `ToolFailed` vs `ModelRetry`, retry budgets, `RunContext.is_tool_available` |

## Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pydantic-ai[spec]` | 2.24.0 | Core agent framework; the `spec` extra is required for `20_agent_spec.py` |
| `fasta2a` | 0.6.1 | A2A protocol support (required for `18_a2a.py`) |
| `pydantic-evals` | 2.24.0 | Evaluation framework (required for `17_evals.py`, `25_agentic_evals.py`) |
| `pydantic-graph` | 2.24.0 | Graph/FSM library (required for `14_stateful_graphs.py`, `15_graphs_with_genai.py`) |
| `pydantic` | >=2.10.0 | Data validation and structured output schemas |
| `pydantic-settings` | >=2.7.0 | `.env` file loading via `BaseSettings` |
| `openai` | >=1.60.0 | OpenAI API client |
| `mcp` | >=1.0.0 | MCP protocol client (required for `12_mcp_client.py`) |
| `uvicorn` | >=0.30.0 | ASGI server (required for `18_a2a.py`) |

## Notes

- **Model names need a provider prefix** in v2 — a bare `gpt-4o-mini` raises a `UserError`. These examples default to `openai-chat:gpt-4o-mini` (Chat Completions).
- **Native tools** (`03_built_in_tools.py`) are only supported on the OpenAI Responses API, so that example is the one that overrides the model from `settings.py` to `openai-responses:`.
- **MCP client** (`12_mcp_client.py`) runs an in-process FastMCP server, so it needs no Node.js, no subprocess, and no network beyond the LLM.
- **A2A** (`18_a2a.py`) starts an HTTP server — run it standalone and test with curl.
- **Agentic evals** (`25_agentic_evals.py`) configure logfire with `send_to_logfire=False` to capture spans locally; no Logfire account or network access is needed.
- **Graphs** (`14_stateful_graphs.py`) use `pydantic_graph`, which is a standalone library with no dependency on `pydantic-ai`.
