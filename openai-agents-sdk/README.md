# OpenAI Agents SDK

- Repo: https://github.com/openai/openai-agents-python
- Documentation: https://openai.github.io/openai-agents-python/
- SDK Version: >= 0.17.6

## Key Features

The OpenAI Agents SDK provides a lightweight framework for building multi-agent workflows. Features that make it **distinct from other frameworks**:

- **Voice Agents** — VoicePipeline for STT → Agent → TTS voice applications with streaming audio
- **Sandbox Agents** — Persistent isolated workspaces with manifests, shell, filesystem, and session resume
- **Sessions** — Built-in persistent memory across turns (SQLite, Redis, SQLAlchemy, etc.) with no manual history management
- **Human-in-the-Loop** — Pause/resume execution for tool approval with serializable `RunState`
- **MCP Tools** — First-class Model Context Protocol support, including `HostedMCPTool` (OpenAI-hosted, no local server needed)
- **Realtime Agents** — WebSocket-based voice agents with sub-second latency (`RealtimeAgent` + `RealtimeRunner`)
- **Agent Visualization** — Generate Graphviz diagrams of agent architectures with `draw_graph()`
- **Handoffs & Orchestration** — Native agent-to-agent delegation with streaming support
- **Guardrails** — Input/output validation, tool input guardrails, and LLM-as-a-judge patterns
- **Tracing** — Built-in OpenAI trace integration for debugging

## Examples

| # | File | Feature |
|---|------|---------|
| 0 | `00_hello_world.py` | Basic agent setup and execution |
| 1 | `01_tools_and_metrics.py` | Function tools with structured tool results |
| 2 | `02_structured_outputs.py` | Pydantic-based structured output parsing |
| 3 | `03_parallelization_in_workflow.py` | Running multiple agents in parallel |
| 4 | `04_handoffs_and_streaming.py` | Agent handoffs with streaming output |
| 5 | `05_agents_as_tools.py` | Using agents as callable tools |
| 6 | `06_output_guardrails.py` | Output validation guardrails |
| 7 | `07_llm_as_a_judge.py` | LLM-as-a-judge evaluation pattern |
| 8 | `08_tracing.py` | OpenAI trace integration |
| 9 | `09_sessions.py` | **Sessions** — persistent multi-turn memory with SQLiteSession |
| 10 | `10_human_in_the_loop.py` | **Human-in-the-Loop** — tool approval, RunState serialize/resume |
| 11 | `11_mcp_tools.py` | **MCP Tools** — HostedMCPTool with streaming and approval |
| 12 | `12_realtime_agent.py` | **Realtime Agents** — WebSocket voice agents with RealtimeRunner |
| 13 | `13_agent_visualization.py` | **Agent Visualization** — draw_graph() for agent architecture |
| 14 | `14_voice_agent.py` | **Voice Agents** — VoicePipeline (STT → Agent → TTS) with streaming |
| 15 | `15_sandbox_agent.py` | **Sandbox Agents** — SandboxAgent, Manifest, UnixLocalSandboxClient |
| 16 | `16_tool_input_guardrails.py` | **Tool Input Guardrails** — pre-execution arg checks with allow/reject/raise |

## How to Setup

### Prerequisites

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- For visualization: [Graphviz](https://graphviz.org/) installed (`brew install graphviz` on macOS)

### Install dependencies

```bash
uv sync
```

### .env

Copy `.env.example` to `.env` and fill in your OpenAI API key:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

### Run an example

```bash
uv run python 00_hello_world.py
uv run python 09_sessions.py
uv run python 14_voice_agent.py
uv run python 15_sandbox_agent.py
```
