# Deep Agents Examples — Outputs

Captured output from running all examples with `deepagents==0.6.12`, `langchain==1.3.11`, `langchain-openai==1.3.3`, `langchain-quickjs==0.3.2`, and `gpt-4o-mini`.

LLM output is non-deterministic, so exact wording will vary between runs. The structure and demonstrated behavior stay the same.

---

## 00_hello_world.py

> **Feature:** The minimal Deep Agent created with `create_deep_agent`. The output shows a single agent answering a question — the simplest possible Deep Agents application.

```
=== Deep Agents Hello World ===

User: Where does the phrase 'hello world' come from?
Agent: The phrase "Hello, World!" is commonly used as a simple program to illustrate basic syntax in programming languages. It originated from the 1978 book "The C Programming Language" by Brian Kernighan and Dennis Ritchie, where it was used as the first program example to demonstrate how to output text.
```

---

## 01_tools.py

> **Feature:** Giving an agent custom tools. The agent calls a `get_weather` tool twice (once per city) and synthesizes the results into a single answer.

```
=== Deep Agents Tools ===
[tool] get_weather called with city='Lisbon'
[tool] get_weather called with city='Tokyo'

User: What's the weather like in Lisbon and Tokyo?
Agent: The weather in Lisbon is sunny with a temperature of 25°C, while Tokyo is cloudy with a temperature of 19°C.
```

---

## 02_task_planning.py

> **Feature:** The built-in `write_todos` planning tool. The agent breaks a multi-step request into an explicit todo list held in state, then works through it.

```
=== Deep Agents Task Planning ===

Task: Plan a 3-step process for launching a simple blog: pick a platform, write a first post, and publish it.

Agent created 3 todo(s):
  1. [in_progress] Choose a blogging platform (e.g. WordPress, Blogger, Medium) that suits your needs.
  2. [pending] Draft your first blog post, focusing on a topic you are passionate about.
  3. [pending] Publish the blog post on the chosen platform, ensuring it is formatted correctly and visually appealing.

Summary: 1. Choose a blogging platform (e.g., WordPress, Blogger, Medium) that suits your needs.
2. Draft your first blog post, focusing on a topic you are passionate about.
3. Publish the blog post on the chosen platform, ensuring it is formatted correctly and visually appealing.
```

---

## 03_virtual_filesystem.py

> **Feature:** The built-in virtual filesystem (default `StateBackend`). The agent writes a file with `write_file`; we read it back out of the returned state under the `files` key.

```
=== Deep Agents Virtual Filesystem ===

Files in the virtual filesystem: ['/haiku.txt']

--- /haiku.txt ---
Waves whisper secrets,
Endless blue embraces sky,
Salt air, calm hearts sigh.

Agent: I saved the haiku about the ocean in a file named haiku.txt.
```

---

## 04_filesystem_permissions.py

> **Feature:** `FilesystemPermission` rules that guard filesystem paths. A deny rule blocks writes to `secret.txt` while allowing `notes.txt` — the blocked file never appears in state.

```
=== Deep Agents Filesystem Permissions ===

Files that were actually written: ['/notes.txt']
(secret.txt should be missing — the deny rule blocked it)

Agent: The file `notes.txt` was successfully created with the content "hello." However, I encountered a permission error while attempting to write to `secret.txt`.
```

---

## 05_structured_output.py

> **Feature:** Typed structured output via `response_format=<PydanticModel>`. The agent extracts fields from free text and returns a validated `ContactInfo` object read from `result["structured_response"]`.

```
=== Deep Agents Structured Output ===

Input text: Hey, I'm Ada Lovelace from Analytical Engines Inc. You can reach me at ada@analyticalengines.io.

Parsed ContactInfo object:
  name    = 'Ada Lovelace'
  email   = 'ada@analyticalengines.io'
  company = 'Analytical Engines Inc.'

Type: ContactInfo
```

---

## 06_streaming.py

> **Feature:** Streaming intermediate steps with `agent.stream(..., stream_mode="updates")`. Tool calls and tool results are printed as they arrive, before the final answer.

```
=== Deep Agents Streaming ===
User: Which is bigger by population, Tokyo or Cairo?

Streaming updates as they arrive:
  [model] tool call -> get_population({'city': 'Tokyo'})
  [model] tool call -> get_population({'city': 'Cairo'})
  [tools] tool result -> 37 million
  [tools] tool result -> 22 million

Agent: Tokyo, with a population of approximately 37 million, is bigger than Cairo, which has a population of about 22 million.
```

---

## 07_subagents.py

> **Feature:** Delegation to a `SubAgent`. The main agent calls the built-in `task` tool to hand a subproblem to a specialized subagent, which uses its own `multiply` tool.

```
=== Deep Agents Subagents ===
[subagent tool] multiply(23.0, 17.0)

Tools the main agent called: ['task']
(the 'task' tool means work was delegated to a subagent)

Agent: The total number of boxes in the warehouse is 391.
```

---

## 08_composite_backend.py

> **Feature:** `CompositeBackend` routing paths to different backends. `/memories/` is routed to a durable `StoreBackend` while everything else stays in the ephemeral `StateBackend` — files land in the correct store based on their path prefix.

```
=== Deep Agents Composite Backend ===

StateBackend (ephemeral, thread state): ['/scratch.txt']
StoreBackend (durable, /memories/ route):
  namespace=('memories',) key=/profile.txt content='the user prefers tea'

Agent: The files have been successfully written: `/scratch.txt` with "temporary note" and `/memories/profile.txt` with "the user prefers tea."
```

---

## 09_human_in_the_loop.py

> **Feature:** Human-in-the-loop approvals via `interrupt_on` + a checkpointer. The agent pauses before a guarded `delete_file` tool call; a rejected request is not executed, an approved one runs.

```
=== Deep Agents Human-in-the-Loop ===

[Case 1] Reject the deletion:
  PAUSED — agent wants to call delete_file({'name': 'important.txt'})
  Human decision: REJECT
  Agent: The file deletion request was rejected. Please confirm if you'd like to proceed with deleting "important.txt."

[Case 2] Approve the deletion:
  PAUSED — agent wants to call delete_file({'name': 'temp.log'})
  Human decision: APPROVE
  [tool] delete_file('temp.log') EXECUTED
  Agent: The file `temp.log` has been deleted.
```

---

## 10_memory.py

> **Feature:** Long-term memory via the `memory=` parameter. An `AGENTS.md` file is loaded into the system prompt at startup, so the agent recalls persistent facts about the user.

```
=== Deep Agents Memory ===

Loaded memory from /memory/AGENTS.md
User: Remind me — who am I and what do I do for work?
Agent: You are Marie, a marine biologist based in Lisbon.
```

---

## 11_skills.py

> **Feature:** Skills — on-demand capabilities described in `SKILL.md` files. The agent discovers the `haiku-writer` skill, reads it with `read_file` (progressive disclosure), and follows its instructions — proven by the required `(fin)` marker.

```
=== Deep Agents Skills ===

[agent read the skill] /skills/haiku-writer/SKILL.md

User: Please write a haiku about the ocean.
Agent:
Here’s a haiku about the ocean:

Waves whisper to shore,  
Dancing light on endless blue,  
Secrets deep beneath. (fin)

Skill discovered & read: True
Skill instructions followed (ends with '(fin)'): True
```

---

## 12_local_filesystem_backend.py

> **Feature:** `FilesystemBackend` with `virtual_mode=True` writing to a real directory on disk. The agent creates a file that we then read back directly from the filesystem.

```
=== Deep Agents Local Filesystem Backend ===
Workspace on disk: /var/folders/qm/1yt5968d2fq18bjj_zff6jtc0000gn/T/deepagents_fs_mzh3sncm

Agent: The file `notes.txt` has been created with the content: "Hello from disk".

Real files written to disk:
  notes.txt -> 'Hello from disk'
```

---

## 13_store_backend.py

> **Feature:** `StoreBackend` for durable, cross-conversation storage. Conversation 1 saves a file; a brand-new agent in conversation 2 — with no shared message history — reads it back from the store.

```
=== Deep Agents Store Backend ===

[Conversation 1 - write] Agent: The file `preferences.txt` has been created with the content: "favorite color is teal."

Files now living in the durable store:
  key=/preferences.txt content='favorite color is teal'

[Conversation 2 - read] Agent: Your favorite color is teal.

(Conversation 2 had no shared message history — only the store persisted it.)
```

---

## 14_summarization.py

> **Feature:** Conversation summarization via the `compact_conversation` tool (`SummarizationToolMiddleware`) with a low token trigger. The agent folds a bloated conversation into a compact summary on demand.

```
=== Deep Agents Summarization ===

Messages after a detailed turn: 2

[agent called tool] compact_conversation
[tool result] Conversation compacted. Summarized 2 messages into a concise summary.

Agent: The conversation context has been refreshed.
```

---

## 15_custom_middleware.py

> **Feature:** A custom `AgentMiddleware` using `wrap_model_call`. The middleware counts model invocations and deterministically stamps a sign-off line onto the final answer by rewriting the response.

```
=== Deep Agents Custom Middleware ===
  [middleware] intercepted model call #1

User: In one sentence, what is a vector database?
Agent:
A vector database is a storage system that uses high-dimensional vectors to represent and retrieve data efficiently, enabling advanced similarity search and machine learning applications.
-- handled by SignOffMiddleware

Model calls counted by middleware: 1
Response reshaped by middleware: True
```

---

## 16_runtime_context.py

> **Feature:** Runtime context via a `context_schema` and `ToolRuntime`. Request-scoped data (user, tier) is passed at invoke time and read inside a tool — the same agent answers differently per user with no code changes.

```
=== Deep Agents Runtime Context ===

context=UserContext(user_name='Marie', tier='gold')
Agent: You are Marie, and you are on the Gold tier.

context=UserContext(user_name='Tom', tier='free')
Agent: You are Tom, and you are on the free tier.
```

---

## 17_rubric_middleware.py

> **Feature:** `RubricMiddleware` for self-evaluated iteration. A grader sub-agent checks the answer against a rubric; the first attempt needs revision, and the agent iterates until the grader is satisfied.

```
=== Deep Agents Rubric Middleware ===
Rubric: exactly 3 numbered benefits + a final 'STATUS: COMPLETE' line

  [grader] iteration 0: result=needs_revision
  [grader] iteration 1: result=satisfied

Grading iterations: 2

Final answer (passed the rubric):
Here are three key benefits of unit testing:

1. **Early Bug Detection**: Identifies issues at an early stage, reducing the cost and effort of fixing bugs later in the development process.

2. **Improved Code Quality**: Encourages better code structure and design, leading to cleaner and more maintainable code.

3. **Refactoring Confidence**: Facilitates safe code changes by ensuring that modifications do not break existing functionality.

STATUS: COMPLETE
```

---

## 18_harness_profiles.py

> **Feature:** `HarnessProfile` registered per model with `register_harness_profile`. The profile injects a house-style prompt suffix and excludes a tool automatically — every answer starts with the enforced `AHOY:` prefix.

```
=== Deep Agents Harness Profiles ===
Registered profile for: openai:gpt-4o-mini
  system_prompt_suffix: enforces the 'AHOY:' house style
  excluded_tools: {'write_todos'}

User: What is 2 + 2? Answer briefly.
Agent: AHOY: 2 + 2 equals 4.

House-style profile applied (answer starts with 'AHOY:'): True
```

---

## 19_interpreters.py

> **Feature:** A sandboxed code interpreter via the QuickJS `CodeInterpreterMiddleware` (`eval` tool). The agent writes JavaScript, executes it in an isolated engine, and grounds its answer in the real computed result.

```
=== Deep Agents Interpreters ===

[agent ran JS]
let sumOfSquares = 0;
for (let i = 1; i <= 20; i++) {
    sumOfSquares += i * i;
}
sumOfSquares;

[sandbox output] <result>2870</result>

User: Using the eval tool, compute the sum of squares from 1 to 20. Show the number.
Agent: The sum of squares from 1 to 20 is **2870**.
```
