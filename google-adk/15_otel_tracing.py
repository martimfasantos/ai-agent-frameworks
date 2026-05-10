import os
import asyncio

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.telemetry.setup import OTelHooks, maybe_set_otel_providers
from google.genai.types import Content, Part

from settings import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- Native OpenTelemetry integration via OTelHooks
- Custom span exporter to capture and format trace data
- In-memory metric reader for agentic metrics
- Semantic convention attributes (gen_ai.* namespace)

ADK 1.32+ ships native OpenTelemetry agentic metrics alongside
its existing tracing support. This example shows how to configure
both span processors and metric readers using OTelHooks, then
inspect the captured telemetry after an agent run.

For more details, visit:
https://adk.dev/observability/traces/
-------------------------------------------------------
"""


# --- 1. In-memory span exporter to collect traces ---
class InMemorySpanExporter(SpanExporter):
    """Collects spans in memory for later inspection."""

    def __init__(self):
        self.spans: list[ReadableSpan] = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


# --- 2. Configure OpenTelemetry hooks ---
span_exporter = InMemorySpanExporter()
metric_reader = InMemoryMetricReader()

otel_hooks = OTelHooks(
    span_processors=[SimpleSpanProcessor(span_exporter)],
    metric_readers=[metric_reader],
)
maybe_set_otel_providers([otel_hooks])
print("OpenTelemetry configured with in-memory span exporter and metric reader.\n")

# --- 3. Create a simple agent ---
agent = LlmAgent(
    name="otel_demo_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="You are a helpful assistant. Respond in exactly one sentence.",
    description="Agent with OTel tracing enabled.",
)


# --- 4. Run the agent and inspect telemetry ---
async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="otel_demo", user_id="user", session_id="trace-session"
    )
    runner = Runner(
        agent=agent, app_name="otel_demo", session_service=session_service
    )

    content = Content(role="user", parts=[Part(text="What is OpenTelemetry?")])
    async for event in runner.run_async(
        user_id="user", session_id="trace-session", new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"[AGENT RESPONSE] {event.content.parts[0].text}\n")

    # --- 5. Print captured trace spans ---
    print("=== Captured Trace Spans ===\n")
    for span in span_exporter.spans:
        attrs = dict(span.attributes) if span.attributes else {}
        gen_ai_attrs = {k: v for k, v in attrs.items() if k.startswith("gen_ai.")}
        print(f"  Span: {span.name}")
        print(f"    Duration: {(span.end_time - span.start_time) / 1e6:.0f}ms")
        if gen_ai_attrs:
            for k, v in gen_ai_attrs.items():
                print(f"    {k}: {v}")
        print()

    # --- 6. Print collected metrics (if any) ---
    print("=== Collected OTel Metrics ===\n")
    metrics_data = metric_reader.get_metrics_data()
    found = False
    if metrics_data and metrics_data.resource_metrics:
        for rm in metrics_data.resource_metrics:
            for sm in rm.scope_metrics:
                for metric in sm.metrics:
                    found = True
                    print(f"  {metric.name}: {metric.description}")
                    for dp in metric.data.data_points:
                        value = getattr(dp, "value", getattr(dp, "sum", "N/A"))
                        print(f"    Value: {value}")
    if not found:
        print("  No standalone metrics emitted (token usage is on span attributes above).")


if __name__ == "__main__":
    asyncio.run(main())
