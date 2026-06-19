# LangGraph

- Repo: https://github.com/langchain-ai/langgraph
- Documentation: https://docs.langchain.com/oss/python/langgraph/overview

LangGraph is a framework from LangChain for building stateful, multi-actor agents as graphs. Nodes are functions, edges define control flow, and built-in persistence turns any graph into a conversational agent with memory, human-in-the-loop approval, time-travel debugging, and streaming — all with a small, composable API.

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
| `00_hello_world.py` | Hello World | `StateGraph`, `MessagesState`, `START`, `END`, `invoke` |
| `01_state_and_reducers.py` | State & Reducers | `TypedDict`, `Annotated`, `operator.add`, `add_conditional_edges` |
| `02_pydantic_state.py` | Pydantic State Validation | `BaseModel` as state schema, runtime validation |
| `03_input_output_schemas.py` | Input/Output Schema Filtering | `StateGraph(State, input_schema=..., output_schema=...)` |
| `04_graph_visualization.py` | Graph Visualization | `draw_mermaid()`, `draw_ascii()` |
| `05_tool_calling.py` | Tool Calling | `@tool`, `bind_tools`, `ToolNode`, `tools_condition` |
| `06_command_from_tools.py` | Command from Tools | `Command(update=..., goto=...)` returned from `@tool` |
| `07_prompt_chaining_and_routing.py` | Prompt Chaining & Routing | `with_structured_output`, conditional routing |
| `08_streaming.py` | Streaming Modes | `graph.astream()`, modes: `updates`, `messages` |
| `09_custom_streaming.py` | Custom Stream Writer | `get_stream_writer()`, `stream_mode="custom"` |
| `10_persistence.py` | Short-Term Memory | `InMemorySaver`, `thread_id`, multi-turn |
| `11_message_management.py` | Message Management | `trim_messages`, `RemoveMessage`, summary pattern |
| `12_long_term_memory.py` | Long-Term Memory Store | `InMemoryStore`, `get_store()`, `store.put()`, `store.search()` |
| `13_time_travel.py` | Replay & Fork | `get_state_history()`, `update_state()` |
| `14_human_in_the_loop.py` | Human-in-the-Loop | `interrupt()`, `Command(resume=...)` |
| `15_retry_policies.py` | Retry Policies | `RetryPolicy`, `add_node(..., retry_policy=...)` |
| `16_map_reduce.py` | Map-Reduce (Fan-out) | `Send`, parallel workers, aggregation |
| `17_subgraphs.py` | Subgraph Composition | Subgraph as node, shared/different state |
| `18_multi_agent_handoffs.py` | Multi-Agent Handoffs | `Command(goto=...)`, specialist agents |
| `19_orchestrator_worker.py` | Orchestrator-Worker | `Send`, `with_structured_output` for planning |
| `20_evaluator_optimizer.py` | Evaluator-Optimizer Loop | Conditional looping, structured evaluation |
| `21_functional_api.py` | Functional API | `@entrypoint`, `@task`, `entrypoint.final`, futures |
| `22_error_handling_and_caching.py` | Error Handling & Caching | Node-level `error_handler`, `CachePolicy` with TTL |

## Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `langgraph` | >=1.1.3 | Core graph framework |
| `langchain` | >=1.2.13 | LangChain base library |
| `langchain-openai` | >=1.1.12 | OpenAI model integration (`ChatOpenAI`) |
| `pydantic` | >=2.12.5 | State validation and structured outputs |
| `pydantic-settings` | >=2.13.1 | `.env` file loading via `BaseSettings` |
| `python-dotenv` | >=1.2.2 | Environment variable loading |
| `grandalf` | >=0.8 | ASCII graph rendering (used by `04_graph_visualization.py`) |
