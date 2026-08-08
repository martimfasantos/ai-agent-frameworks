# Deep Agents Examples — Outputs

Captured output from running all examples with `deepagents==0.7.4`, `langchain==1.3.14`, `langchain-openai==1.4.1`, `langchain-quickjs==0.3.5`, and `gpt-4o-mini`.

LLM output is non-deterministic, so exact wording will vary between runs. The structure and demonstrated behavior stay the same.

> Every transcript below was recaptured for 0.7.4. That release ships a much leaner default system prompt (the authored base prompt is now empty), which changes what the model volunteers to do, so older captures no longer match.

---

## 00_hello_world.py

> **Feature:** The minimal Deep Agent created with `create_deep_agent`. The output shows a single agent answering a question — the simplest possible Deep Agents application.

```
=== Deep Agents Hello World ===

User: Where does the phrase 'hello world' come from?
Agent: The phrase "Hello, World!" originated from a simple programming example in the early days of computing, notably popularized by the 1978 book "The C Programming Language" by Brian Kernighan and Dennis Ritchie.
```

---

## 01_tools.py

> **Feature:** Giving an agent custom tools. The agent calls a `get_weather` tool twice (once per city) and synthesizes the results into a single answer.

```
=== Deep Agents Tools ===
[tool] get_weather called with city='Lisbon'
[tool] get_weather called with city='Tokyo'

User: What's the weather like in Lisbon and Tokyo?
Agent: The weather in Lisbon is sunny at 25°C, while Tokyo is cloudy at 19°C.
```

---

## 02_task_planning.py

> **Feature:** Task planning via `TodoListMiddleware`, which supplies the `write_todos` tool and the `todos` state channel. Since 0.7.0 this middleware is no longer in the default stack, so it is passed explicitly — without it there is no `write_todos` tool and `result["todos"]` is always empty.

```
=== Deep Agents Task Planning ===

Task: Plan a 3-step process for launching a simple blog: pick a platform, write a first post, and publish it.

Agent created 3 todo(s):
  1. [completed] Selected WordPress as the blogging platform for launching the blog.
  2. [completed] Draft the first blog post including title and content.
  3. [completed] Published the blog post on the chosen platform.

Summary: I have successfully completed all steps to launch the blog: 

1. Selected WordPress as the blogging platform.
2. Drafted the first blog post.
3. Published the blog post on the platform.

The blog is now live and ready for readers!
```

---

## 03_virtual_filesystem.py

> **Feature:** The built-in virtual filesystem (default `StateBackend`). The agent writes a file with `write_file`; we read it back out of the returned state under the `files` key.

```
=== Deep Agents Virtual Filesystem ===

Files in the virtual filesystem: ['/haiku.txt']

--- /haiku.txt ---
Waves whisper secrets,
Dancing on the golden shore,
Endless blue beckons.

Agent: I saved the haiku in a file named haiku.txt.
```

---

## 04_filesystem_permissions.py

> **Feature:** `FilesystemPermission` rules that guard filesystem paths. A deny rule blocks writes to `secret.txt` while allowing `notes.txt`. The second half shows that 0.7.0's recursive `delete` tool is classified as a `"write"` operation, so the same rules gate deletion: `/draft.txt` is removed but `/protected/config.txt` survives.

```
=== Deep Agents Filesystem Permissions ===

Files that were actually written: ['/notes.txt']
(secret.txt should be missing — the deny rule blocked it)

Agent: The file `notes.txt` was successfully created with the content 'hello', but writing to `secret.txt` was blocked due to permission restrictions.

=== Deletes are gated by the same write rules ===
Seeded files: ['/draft.txt', '/protected/config.txt']
Files remaining: ['/protected/config.txt']
(/draft.txt was deleted; /protected/config.txt survived the write-deny rule)

Agent: The deletion of `/draft.txt` succeeded, while the deletion of `/protected/config.txt` was blocked due to permissions.
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
  [tools] tool result -> 22 million
  [tools] tool result -> 37 million

Agent: Tokyo is bigger by population, with about 37 million people compared to Cairo's 22 million.
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

Agent: The files have been created successfully.
```

---

## 09_human_in_the_loop.py

> **Feature:** Human-in-the-loop approvals via `interrupt_on` + a checkpointer. The agent pauses before a guarded `delete_file` tool call; a rejected request is not executed, an approved one runs.

```
=== Deep Agents Human-in-the-Loop ===

[Case 1] Reject the deletion:
  PAUSED — agent wants to call delete_file({'name': 'important.txt'})
  Human decision: REJECT
  Agent: The file important.txt could not be deleted.

[Case 2] Approve the deletion:
  PAUSED — agent wants to call delete_file({'name': 'temp.log'})
  Human decision: APPROVE
  [tool] delete_file('temp.log') EXECUTED
  Agent: The file temp.log has been deleted.
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

> **Feature:** Skills — on-demand capabilities described in `SKILL.md` files. The agent discovers the `haiku-writer` skill, reads it with `read_file` (progressive disclosure), and follows its instructions — proven by the required `(fin)` marker. With 0.7.0's leaner default prompt the example's own `system_prompt` has to spell out the read-then-follow step; without it `gpt-4o-mini` answers from general knowledge and never opens the skill.

```
=== Deep Agents Skills ===

[agent read the skill] /skills/haiku-writer/SKILL.md

User: Please write a haiku about the ocean.
Agent:
Waves dance with the tide,  
Whispers of the deep call forth,  
Secrets held in blue. (fin)

Skill discovered & read: True
Skill instructions followed (ends with '(fin)'): True
```

---

## 12_local_filesystem_backend.py

> **Feature:** `FilesystemBackend` writing to a real directory on disk. The agent creates a file that we then read back directly from the filesystem. `virtual_mode=True` (agent path `/notes.txt` -> `<root_dir>/notes.txt`) became the default in 0.7.0 and is passed explicitly only to make the mapping visible.

```
=== Deep Agents Local Filesystem Backend ===
Workspace on disk: /var/folders/qm/1yt5968d2fq18bjj_zff6jtc0000gn/T/deepagents_fs_s144ign_

Agent: The file **notes.txt** has been created containing the text: **Hello from disk**.

Real files written to disk:
  notes.txt -> 'Hello from disk'
```

---

## 13_store_backend.py

> **Feature:** `StoreBackend` for durable, cross-conversation storage. Conversation 1 saves a file; a brand-new agent in conversation 2 — with no shared message history — reads it back from the store.

```
=== Deep Agents Store Backend ===

[Conversation 1 - write] Agent: The file **preferences.txt** has been saved with the content: "favorite color is teal."

Files now living in the durable store:
  key=/preferences.txt content='favorite color is teal'

[Conversation 2 - read] Agent: Your favorite color is teal.

(Conversation 2 had no shared message history — only the store persisted it.)
```

---

## 14_summarization.py

> **Feature:** Conversation summarization via the `compact_conversation` tool (`SummarizationToolMiddleware`) with a low token trigger. The agent folds a bloated conversation into a compact summary on demand. `system_prompt` defaults to `None` since 0.7.0, so the compaction nudge is passed explicitly.

```
=== Deep Agents Summarization ===

Messages after a detailed turn: 2

[agent called tool] compact_conversation
[tool result] Conversation compacted. Summarized 2 messages into a concise summary.

Agent: The conversation has been compacted, and the older messages have been summarized to free up context space. If you have another topic or question, feel free to ask!
```

---

## 15_custom_middleware.py

> **Feature:** A custom `AgentMiddleware` using `wrap_model_call`. The middleware counts model invocations and deterministically stamps a sign-off line onto the final answer by rewriting the response.

```
=== Deep Agents Custom Middleware ===
  [middleware] intercepted model call #1

User: In one sentence, what is a vector database?
Agent:
A vector database is a type of database designed to store and query data represented as high-dimensional vectors, often used in applications involving machine learning and similarity searches.
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
Agent: You are Marie, and you are on the gold tier.

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

1. **Improved Code Quality**: Unit testing helps identify bugs early in the development process, leading to cleaner and more reliable code.

2. **Facilitates Changes**: A solid suite of unit tests allows developers to refactor or modify code confidently, reducing the risk of introducing new bugs.

3. **Faster Debugging**: When a unit test fails, it pinpoints the location of the issue, making it quicker to diagnose and fix the problem.

STATUS: COMPLETE
```

---

## 18_harness_profiles.py

> **Feature:** `HarnessProfile` registered per model with `register_harness_profile`. Both halves of the profile are proven: the prompt suffix forces the `AHOY:` prefix, and `excluded_tools` strips `write_todos` before the model sees it, so no todos reach state even though `TodoListMiddleware` really installed the tool. Note `excluded_tools` is a plain name filter — excluding a name nothing installed is a silent no-op.

```
=== Deep Agents Harness Profiles ===
Registered profile for: openai:gpt-4o-mini
  system_prompt_suffix: enforces the 'AHOY:' house style
  excluded_tools: {'write_todos'}

Tools installed by TodoListMiddleware: ['write_todos']

User: Plan a 2-step process for brewing tea, then answer briefly.
Agent: AHOY: 

1. Boil water to the desired temperature depending on the type of tea.
2. Steep the tea leaves or tea bags in the hot water for the recommended time.

House-style suffix applied (answer starts with 'AHOY:'): True
write_todos installed in the harness: True
Todos recorded in state after the run: 0 -> the profile stripped write_todos before the model ever saw it
```

---

## 19_interpreters.py

> **Feature:** A sandboxed code interpreter via the QuickJS `CodeInterpreterMiddleware` (`eval` tool). The agent writes JavaScript, executes it in an isolated engine, and grounds its answer in the real computed result.

```
=== Deep Agents Interpreters ===

[agent ran JS]
let sumOfSquares = 0; for (let i = 1; i <= 20; i++) { sumOfSquares += i * i; } sumOfSquares;

[sandbox output] <result>2870</result>

User: Using the eval tool, compute the sum of squares from 1 to 20. Show the number.
Agent: The sum of squares from 1 to 20 is **2870**.
```

---

## 20_filesystem_tool_allowlist.py

> **Feature:** `FilesystemMiddleware(tools=[...])` narrows the filesystem tool set (typed by the exported `FsToolName`), and passing the configured instance through `middleware=[...]` replaces the default `FilesystemMiddleware` by `.name` match. The resulting agent can read but not mutate: `write_file`, `edit_file` and `delete` are gone from its tool node, and the delete request fails. Omitting `read_file` from the list is rejected with a `ValueError`.

```
=== Deep Agents Filesystem Tool Allowlist ===
FsToolName options: ['ls', 'read_file', 'write_file', 'edit_file', 'delete', 'glob', 'grep', 'execute']
Default agent tools: ['delete', 'edit_file', 'execute', 'glob', 'grep', 'ls', 'read_file', 'task', 'write_file']

Allowlisted middleware 'FilesystemMiddleware' exposes: ['ls', 'read_file', 'glob', 'grep']
Agent tools after the override: ['glob', 'grep', 'ls', 'read_file', 'task']
Mutating tools write_file / edit_file / delete are absent ✅

FilesystemMiddleware(tools=['ls', 'glob']) -> ValueError: read_file must be included in tools; it is required by FilesystemMiddleware

User: Read /report.md and tell me the revenue figure, then delete the file.
Agent: The revenue figure mentioned in the file is that it "grew 12%." However, I cannot delete the file as I'm only able to read and not modify or delete files.

Files still present: ['/report.md']

Caveat: create_deep_agent(permissions=...) is wired into the *default* FilesystemMiddleware, so replacing that instance silently drops allow/deny enforcement (only interrupt rules survive). Configure permissions on the backend or keep the default middleware when you need a real boundary.
```

> An allowlist keeps the model's options tidy; it is not a security boundary. `permissions=` reaches the filesystem layer only through the default `FilesystemMiddleware` instance, so overriding that instance drops allow/deny enforcement with no warning.
