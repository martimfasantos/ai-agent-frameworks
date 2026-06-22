# Microsoft Agent Framework

- Repo: https://github.com/microsoft/agent-framework
- Documentation: https://learn.microsoft.com/en-us/agent-framework/

Microsoft Agent Framework is an open-source SDK for building, orchestrating, and deploying AI agents and multi-agent workflows. It unifies the capabilities of AutoGen and Semantic Kernel, providing a comprehensive platform for creating intelligent agents with tool use, middleware, sessions, structured outputs, MCP integration, and graph-based workflows with human-in-the-loop support.

> **Note:** The framework is currently in public preview (RC). APIs may change before the 1.0 stable release.

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
| `01_function_tools.py` | Function Tools | Define and call Python functions as agent tools with `@tool` |
| `02_streaming.py` | Streaming | Stream agent responses token-by-token with `stream=True` |
| `03_structured_output.py` | Structured Output | Enforce typed JSON output using Pydantic schemas |
| `04_multi_turn_sessions.py` | Multi-Turn Sessions | Maintain conversation context across multiple turns |
| `05_built_in_tools.py` | Built-in Tools | Code interpreter and web search via OpenAIResponsesClient |
| `06_multimodal.py` | Multimodal Input | Send images alongside text using `Content.from_uri()` |
| `07_middleware.py` | Middleware | Intercept agent, chat, and function calls with middleware |
| `08_rag.py` | RAG / Context Providers | Inject domain knowledge via `BaseContextProvider` |
| `09_local_mcp_tools.py` | Local MCP Tools | Connect to MCP servers via `MCPStdioTool` (stdio transport) |
| `10_tool_approval.py` | Tool Approval | Gate sensitive tool calls through function middleware |
| `11_agent_as_tool.py` | Agent as Tool | Compose agents by wrapping sub-agents as callable tools |
| `12_declarative_agents.py` | Declarative Agents | Define agents in YAML and load with `AgentFactory` |
| `13_background_responses.py` | Background Responses | Async fire-and-forget with polling for completion |
| `14_multi_agent_orchestration.py` | Multi-Agent Orchestration | Sequential and Handoff orchestration patterns |
| `15_workflows_basics.py` | Workflows: Basics | Function-based executors with conditional routing |
| `16_workflows_agents.py` | Workflows: Agents | Chain LLM-powered agents in a workflow graph |
| `17_workflows_human_in_the_loop.py` | Workflows: HITL | Pause workflows for human approval via `request_info` |
| `18_workflows_visualization.py` | Workflows: Visualization | Export workflow graphs as Mermaid diagrams and PNG images |
| `19_class_skill.py` | ClassSkill | Class-based skills with `@ClassSkill.resource` and `@ClassSkill.script` |
| `20_prompt_injection_defense.py` | Prompt Injection Defense | FIDES information-flow control with integrity and confidentiality labels |
| `21_harness_agent.py` | Harness Agent | Batteries-included agent with memory, todos, modes, and compaction |

## Key dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `agent-framework` | 1.9.0 | Core framework (agents, tools, middleware, workflows) |
| `agent-framework-core` | 1.9.0 | Core abstractions and base classes |
| `agent-framework-declarative` | 1.0.0b260409 | YAML/JSON declarative agent definitions |
| `agent-framework-orchestrations` | 1.0.0b260409 | Sequential and Handoff orchestration builders |
| `pydantic` | >=2.0 | Structured output schemas |
| `pydantic-settings` | >=2.0 | `.env` file loading via `BaseSettings` |
| `python-dotenv` | >=1.0 | Explicit `.env` loading (framework does not auto-load) |
| `graphviz` | >=0.21 | Workflow PNG export (requires system `graphviz` package) |

## Notes

- The framework does **not** auto-load `.env` files. Every example calls `load_dotenv()` explicitly.
- Examples 05 and 13 require `OpenAIResponsesClient` (Responses API) rather than `OpenAIChatClient`.
- Example 09 requires Node.js / `npx` for the MCP filesystem server.
- Example 18 requires the system `graphviz` package for PNG export (`brew install graphviz` on macOS).
