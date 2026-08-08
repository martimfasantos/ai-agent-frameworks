# Deep Agents

- Repo: https://github.com/langchain-ai/deepagents
- Documentation: https://docs.langchain.com/oss/python/deepagents/overview

Deep Agents is a framework from LangChain for building agents that can plan and execute complex, long-horizon tasks. Built on top of LangChain and LangGraph, a single `create_deep_agent` call gives you a harness with built-in task planning, a virtual filesystem, subagent delegation, and configurable middleware — plus pluggable backends (in-memory, local disk, durable store), skills, memory, permissions, human-in-the-loop approval, and code interpreters.

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment variables

Copy the example file and fill in your OpenAI API key:

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

| File | Feature | Key APIs |
|------|---------|----------|
| `00_hello_world.py` | Hello World | `create_deep_agent`, `invoke` |
| `01_tools.py` | Custom Tools | `@tool`, `tools=[...]` |
| `02_task_planning.py` | Task Planning | `TodoListMiddleware`, `write_todos` tool, `result["todos"]` |
| `03_virtual_filesystem.py` | Virtual Filesystem | `write_file`/`read_file`, `result["files"]` (default `StateBackend`) |
| `04_filesystem_permissions.py` | Filesystem Permissions | `FilesystemPermission`, `permissions=[...]`, gating the `delete` tool |
| `05_structured_output.py` | Structured Output | `response_format=<PydanticModel>`, `result["structured_response"]` |
| `06_streaming.py` | Streaming | `agent.stream(..., stream_mode="updates")` |
| `07_subagents.py` | Subagents | `SubAgent`, `subagents=[...]`, built-in `task` tool |
| `08_composite_backend.py` | Composite Backend | `CompositeBackend`, `StateBackend`, `StoreBackend`, path routing |
| `09_human_in_the_loop.py` | Human-in-the-Loop | `interrupt_on`, `Command(resume=...)`, checkpointer |
| `10_memory.py` | Long-Term Memory | `memory=[...]` (AGENTS.md), `create_file_data` |
| `11_skills.py` | Skills | `skills=[...]`, `SKILL.md` progressive disclosure |
| `12_local_filesystem_backend.py` | Local Filesystem Backend | `FilesystemBackend(root_dir=..., virtual_mode=True)` |
| `13_store_backend.py` | Store Backend | `StoreBackend`, `InMemoryStore`, cross-conversation persistence |
| `14_summarization.py` | Summarization | `SummarizationToolMiddleware`, `compact_conversation` tool |
| `15_custom_middleware.py` | Custom Middleware | `AgentMiddleware`, `wrap_model_call` |
| `16_runtime_context.py` | Runtime Context | `context_schema`, `ToolRuntime`, `context=` at invoke |
| `17_rubric_middleware.py` | Rubric Middleware | `RubricMiddleware`, grader loop, `rubric` state key |
| `18_harness_profiles.py` | Harness Profiles | `HarnessProfile`, `register_harness_profile`, `excluded_tools` |
| `19_interpreters.py` | Code Interpreters | `CodeInterpreterMiddleware` (QuickJS `eval` tool) |
| `20_filesystem_tool_allowlist.py` | Filesystem Tool Allowlist | `FilesystemMiddleware(tools=[...])`, `FsToolName`, middleware override by `.name` |

See [`OUTPUTS.md`](./OUTPUTS.md) for captured output from every example.

## Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `deepagents` | >=0.7.4 | Core Deep Agents framework (`create_deep_agent`, backends, middleware) |
| `langchain` | >=1.3.14 | LangChain base library (middleware, tools, runtime) |
| `langchain-core` | >=1.5.0 | Core message/tool/runtime primitives (pulled in by `deepagents`) |
| `langchain-openai` | >=1.3.3 | OpenAI model integration (`ChatOpenAI`) |
| `langchain-quickjs` | >=0.3.3 | Sandboxed JavaScript code interpreter (`19_interpreters.py`), installed via the `deepagents[quickjs]` extra |
| `pydantic` | >=2.13.4 | Structured outputs and context schemas |
| `pydantic-settings` | >=2.14.2 | `.env` file loading via `BaseSettings` |
| `python-dotenv` | >=1.2.2 | Environment variable loading |

## Notes

- **Backends.** The default backend is an ephemeral in-memory `StateBackend` scoped to a conversation. Swap in `FilesystemBackend` for real disk (`12`), `StoreBackend` for durable cross-conversation storage (`13`), or `CompositeBackend` to route different path prefixes to different backends (`08`).
- **Async subagents.** Deep Agents also supports remote/background `AsyncSubAgent`s via `AsyncSubAgentMiddleware`. These require a deployed LangGraph platform graph (a `graph_id`/`url`) to run against, so they are not included as a runnable example here. The synchronous `SubAgent` delegation pattern is shown in `07_subagents.py`.
- **Out of scope.** Examples requiring external infrastructure — Docker/E2B sandbox backends, MCP tool servers, and provider-specific prompt caching — are intentionally omitted so every file runs with only an OpenAI API key.
