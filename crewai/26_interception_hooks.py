import os
import re

from crewai import Agent, Task, Crew
from crewai.hooks import HookAborted, InterceptionPoint, clear_all_hooks, on

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Unified interception hooks registered with @on(InterceptionPoint....)
- Execution boundaries: EXECUTION_START, INPUT, OUTPUT, EXECUTION_END
- Step boundaries: PRE_STEP and POST_STEP around every task
- Aborting a run from a hook with HookAborted, and clear_all_hooks()

The interception API replaces the four legacy decorator pairs (still shown in
18_execution_hooks.py) with one registration point and one contract: mutate
ctx.payload in place, return a replacement, or raise HookAborted to stop the
operation. This reaches run-level concerns the LLM/tool-only hooks could not
express - injecting missing inputs, redacting the final output, and gating a
run against a policy. EXECUTION_END fires exactly once per run, on success and
on failure alike.

For more details, visit:
https://docs.crewai.com/en/learn/execution-boundary-hooks
-------------------------------------------------------
"""

EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


# --- 1. Boundary hooks: observe the run, rewrite its inputs, redact its output ---
# Hooks are global, so they also see CrewAI's internal agent flows. Context
# fields are nullable by design - `ctx.crew is None` filters those out.
@on(InterceptionPoint.EXECUTION_START)
def announce_run(ctx):
    """Fires before the crew starts. ctx.payload is the raw inputs dict."""
    if ctx.crew is None:
        return
    print(f"[EXECUTION_START] inputs={ctx.payload}")


@on(InterceptionPoint.INPUT)
def inject_missing_audience(ctx):
    """Fires after inputs resolve, before task interpolation.

    The task template requires {audience} but the caller never passes it, so
    this in-place edit is what makes interpolation succeed.
    """
    if ctx.crew is None:
        return
    ctx.payload.setdefault("audience", "backend engineers")
    print(f"[INPUT] injected audience -> {ctx.payload['audience']}")


@on(InterceptionPoint.OUTPUT)
def redact_emails(ctx):
    """Fires with the finished CrewOutput as ctx.payload, before the caller sees it."""
    if ctx.crew is None:
        return
    redacted = EMAIL_PATTERN.sub("[EMAIL-REDACTED]", ctx.payload.raw)
    if redacted != ctx.payload.raw:
        ctx.payload.raw = redacted
        print("[OUTPUT] redacted an email address from the final answer")


@on(InterceptionPoint.EXECUTION_END)
def report_outcome(ctx):
    """Fires once per run, whether it completed or failed."""
    if ctx.crew is None:
        return
    print(f"[EXECUTION_END] status={ctx.status} error={ctx.error!r}")


# --- 2. Step hooks: kind="task" for crew tasks, "flow_method" for flow steps ---
@on(InterceptionPoint.PRE_STEP)
def trace_step_start(ctx):
    if ctx.kind != "task":
        return
    print(f"[PRE_STEP] kind={ctx.kind} step={ctx.step_name[:40]!r} agent={ctx.agent_role}")


@on(InterceptionPoint.POST_STEP)
def trace_step_end(ctx):
    if ctx.kind != "task":
        return
    print(f"[POST_STEP] step={ctx.step_name[:40]!r} chars={len(ctx.payload.raw)}")


# --- 3. Create the agent and task ---
agent = Agent(
    role="Release Notes Writer",
    goal="Write short, factual release notes",
    backstory="You write terse release notes and never pad them.",
    llm=settings.OPENAI_MODEL_NAME,
)

task = Task(
    description=(
        "Write exactly two sentences about {topic} for an audience of {audience}. "
        "Then add the final line exactly as: Contact: support@example.com"
    ),
    expected_output="Two sentences followed by the contact line.",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task])

# --- 4. Run with the hooks active (note: no "audience" input is passed) ---
print("=== Run 1: boundary + step hooks on a successful run ===")
result = crew.kickoff(inputs={"topic": "the new interception hooks"})
print("\nFinal (post-redaction) output:")
print(result.raw)

# --- 5. Swap in a policy gate that aborts the run ---
clear_all_hooks()
print("\n=== Run 2: a hook aborts the run with HookAborted ===")

ALLOWED_TOPICS = {"the new interception hooks", "frame streaming"}


@on(InterceptionPoint.EXECUTION_END)
def report_failed_outcome(ctx):
    if ctx.crew is None:
        return
    print(f"[EXECUTION_END] status={ctx.status} error={ctx.error!r}")


@on(InterceptionPoint.PRE_STEP)
def enforce_topic_allowlist(ctx):
    """Gate the step, not the run start: aborting at EXECUTION_START would skip
    EXECUTION_END, which only fires for runs whose EXECUTION_START dispatched."""
    if ctx.kind != "task":
        return
    topic = (ctx.task.description or "").lower()
    if not any(allowed in topic for allowed in ALLOWED_TOPICS):
        raise HookAborted(
            reason="topic is not on the approved release-notes allowlist",
            source="topic-allowlist",
        )


try:
    # "audience" is passed explicitly now - the INPUT hook that injected it is gone.
    crew.kickoff(
        inputs={"topic": "unapproved internal roadmap", "audience": "backend engineers"}
    )
except HookAborted as aborted:
    print(f"kickoff() raised HookAborted: {aborted.reason} (source={aborted.source})")
