import asyncio

from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.schema import NodeWithScore
from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- A custom Workflow that combines retrieval with LLM reasoning
- Self-correcting RAG: grade the retrieved context, rewrite the query, retry
- A bounded loop implemented with plain events (no DAG edges to encode)
- Context state (ctx.store) to carry the attempt counter across steps

A workflow is an event-driven, step-based way to control execution flow: steps
are triggered by events and emit events that trigger further steps, so loops and
branches are ordinary Python instead of graph edges. Here that buys a corrective
RAG pipeline — retrieve, let the LLM judge whether the context is good enough,
and either synthesize an answer or reformulate the question and retrieve again.

Note: `llama-index-core` bundles the Workflows library, so it can be imported
either as `llama_index.core.workflow` (stable re-export, used here) or directly
from the standalone `workflows` package.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/
-------------------------------------------------------
"""

MAX_ATTEMPTS = 2

# --- 1. A tiny in-memory corpus to retrieve over ---
DOCUMENTS = [
    Document(
        text=(
            "Tram line 28 runs from Martim Moniz to Campo Ourique in Lisbon. "
            "It uses the historic Remodelado cars built in the 1930s and climbs "
            "the steep streets of Alfama, Graca and Estrela."
        )
    ),
    Document(
        text=(
            "The Santa Justa Lift is a 45-metre wrought-iron elevator in Lisbon's "
            "Baixa district, opened in 1902. It connects Rua do Ouro to Largo do Carmo "
            "and was designed by Raoul Mesnier du Ponsard."
        )
    ),
    Document(
        text=(
            "Lisbon's funiculars — Gloria, Bica and Lavra — are short cable railways "
            "that link the lower city to the hilltop neighbourhoods. Gloria opened in "
            "1885 and carries passengers between Restauradores and Bairro Alto."
        )
    ),
]


# --- 2. Define the events that wire the steps together ---
class RetrieveEvent(Event):
    query: str


class RetrievedEvent(Event):
    query: str
    nodes: list[NodeWithScore]


class SynthesizeEvent(Event):
    query: str
    nodes: list[NodeWithScore]
    grounded: bool


# --- 3. The workflow: retrieve -> grade -> (rewrite | synthesize) ---
class CorrectiveRagWorkflow(Workflow):
    def __init__(self, *args, index: VectorStoreIndex, llm: OpenAI, **kwargs):
        super().__init__(*args, **kwargs)
        self.retriever = index.as_retriever(similarity_top_k=2)
        self.llm = llm

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> RetrieveEvent:
        await ctx.store.set("attempt", 0)
        await ctx.store.set("original_query", ev.query)
        return RetrieveEvent(query=ev.query)

    @step
    async def retrieve(self, ctx: Context, ev: RetrieveEvent) -> RetrievedEvent:
        """Semantic retrieval over the index"""
        attempt = await ctx.store.get("attempt") + 1
        await ctx.store.set("attempt", attempt)

        nodes = await self.retriever.aretrieve(ev.query)
        print(f"  [retrieve] attempt {attempt} for {ev.query!r}")
        for node in nodes:
            print(f"    score={node.score:.3f} {node.text[:60]}...")
        return RetrievedEvent(query=ev.query, nodes=nodes)

    @step
    async def grade(
        self, ctx: Context, ev: RetrievedEvent
    ) -> RetrieveEvent | SynthesizeEvent:
        """Reasoning step: does the retrieved context actually answer the question?"""
        context = "\n\n".join(node.text for node in ev.nodes)
        verdict = await self.llm.acomplete(
            "Does the context below contain the information needed to answer the "
            f"question? Answer with exactly YES or NO.\n\nQuestion: {ev.query}\n\n"
            f"Context:\n{context}"
        )
        relevant = str(verdict).strip().upper().startswith("YES")
        print(f"  [grade] context is {'sufficient' if relevant else 'insufficient'}")

        if relevant:
            return SynthesizeEvent(query=ev.query, nodes=ev.nodes, grounded=True)

        # Branch: reformulate and loop back, but only up to MAX_ATTEMPTS
        if await ctx.store.get("attempt") < MAX_ATTEMPTS:
            original = await ctx.store.get("original_query")
            rewritten = await self.llm.acomplete(
                "Rewrite this search query to be more explicit and keyword-rich. "
                f"Reply with the query only.\n\n{original}"
            )
            print(f"  [rewrite] {str(rewritten).strip()!r}")
            return RetrieveEvent(query=str(rewritten).strip())

        return SynthesizeEvent(query=ev.query, nodes=ev.nodes, grounded=False)

    @step
    async def synthesize(self, ctx: Context, ev: SynthesizeEvent) -> StopEvent:
        """Answer from the retrieved context, or admit the corpus does not cover it"""
        if not ev.grounded:
            return StopEvent(
                result="Not answerable from the indexed documents."
            )

        context = "\n\n".join(node.text for node in ev.nodes)
        answer = await self.llm.acomplete(
            "Answer the question in one sentence using only the context.\n\n"
            f"Question: {ev.query}\n\nContext:\n{context}"
        )
        return StopEvent(result=str(answer).strip())


# --- 4. Run the workflow on an answerable and an unanswerable question ---
async def main():
    llm = OpenAI(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )
    Settings.llm = llm
    Settings.embed_model = OpenAIEmbedding(
        model=settings.OPENAI_EMBEDDINGS_MODEL,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    index = VectorStoreIndex.from_documents(DOCUMENTS)
    workflow = CorrectiveRagWorkflow(timeout=120, index=index, llm=llm)

    print("=== Answerable question (straight to synthesis) ===")
    result = await workflow.run(query="Which cars does tram line 28 use?")
    print(f"Answer: {result}\n")

    print("=== Unanswerable question (grade fails, query is rewritten, then gives up) ===")
    result = await workflow.run(query="How much does a Lisbon metro day pass cost?")
    print(f"Answer: {result}")


if __name__ == "__main__":
    asyncio.run(main())
