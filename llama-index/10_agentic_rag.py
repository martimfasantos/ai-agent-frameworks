import asyncio
import logging
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.agent import FunctionAgent
from llama_index.core.agent.workflow.workflow_events import ToolCall
from settings import settings

# llama_index.readers.file calls logging.basicConfig() on import, which would
# otherwise turn every HTTP call into a log line
logging.disable(logging.INFO)


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- Multiple query engines (vector search vs summary)
- QueryEngineTool for wrapping engines as agent tools
- Agentic RAG pattern with tool selection
- similarity_top_k for controlling retrieval

This demonstrates LlamaIndex's strength: giving agents the ability to intelligently
select different retrieval strategies based on the question type. Feel free to
explore also another types of retrievers and query engines! LlamaIndex allows for great flexibility 
in how you set up your embeddings, vector stores, indices, and/or query engines as tools for your agents.

By default, LlamaIndex hides away the complexities and let you query your data in under 5 lines of code
Under the hood, LlamaIndex also supports a swappable storage layer that allows you to customize where 
ingested documents (i.e., Node objects), embedding vectors, and index metadata are stored.

For more details, visit:
- https://developers.llamaindex.ai/python/framework/module_guides/deploying/query_engine/
- https://developers.llamaindex.ai/python/framework/module_guides/storing/customization/
- https://developers.llamaindex.ai/python/examples/agent/openai_agent_with_query_engine/
-------------------------------------------------------
"""


async def main():
    # --- 1. Configure the LLM and embedding model ---
    llm = OpenAI(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value()
    )
    Settings.llm = llm  # Set the global LLM in settings for use in query engines
    embed_model = OpenAIEmbedding(
        model=settings.OPENAI_EMBEDDINGS_MODEL,
        api_key=settings.OPENAI_API_KEY.get_secret_value()
    )
    Settings.embed_model = embed_model  # Set the global embedding model in settings

    # --- 2. Load documents and create index ---
    documents = SimpleDirectoryReader(
        input_files=["res/metagpt.pdf"]
    ).load_data()

    print(f"Loaded {len(documents)} document(s)")
    print("-" * 50)
    
    # --- [OPTIONAL] 3. Split documents into nodes ---
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)

    # --- 4. Create multiple query engines with different strategies ---
    # Vector index for semantic search (good for specific facts)
    vector_index = VectorStoreIndex.from_documents(documents)  # from the documents directly - no use of the nodes 
    vector_engine = vector_index.as_query_engine(
        similarity_top_k=3,  # Return top 3 most relevant chunks
        response_mode="compact"  # Combine chunks into a single response
    )

    # Summary index for high-level overviews (good for summarization)
    summary_index = SummaryIndex(nodes)  # Using the split nodes - more control over chunking for summarization
    summary_engine = summary_index.as_query_engine(
        response_mode="tree_summarize"  # Hierarchical summarization
    )

    print("Created vector and summary query engines")
    print("-" * 50)

    # --- 5. Wrap query engines as tools ---
    # The agent can now intelligently choose which tool to use
    vector_tool = QueryEngineTool(
        query_engine=vector_engine,
        metadata=ToolMetadata(
            name="vector_search",
            description=(
                "Useful for searching specific information, facts, and details "
                "from the MetaGPT research paper. Use this when you need precise "
                "information or technical details."
            )
        )
    )

    summary_tool = QueryEngineTool(
        query_engine=summary_engine,
        metadata=ToolMetadata(
            name="document_summary",
            description=(
                "Useful for getting high-level overviews and summaries of the "
                "MetaGPT research paper. Use this when you need general understanding "
                "or a broad summary."
            )
        )
    )

    print("Created QueryEngineTools with different strategies")
    print("-" * 50)

    # --- 6. Create agent with both tools ---
    agent = FunctionAgent(
        llm=llm,
        tools=[vector_tool, summary_tool],
        verbose=False  # step logging became functional in workflows 2.15.0
    )

    print("Agent created with multiple query strategies")
    print("-" * 50)

    # --- 7. Ask specific question (should use vector_search) ---
    query1 = "What are the specific roles defined in MetaGPT?"
    handler1 = agent.run(query1)
    
    async for ev in handler1.stream_events():
        if isinstance(ev, ToolCall):
            print(f"Tool selected: {ev.tool_name}")

    response1 = await handler1

    print(f"Query 1: {query1}")
    print(f"Response: {response1}")
    print("-" * 50)

    # --- 8. Ask for overview (should use document_summary) ---
    query2 = "Give me a high-level overview of what MetaGPT is about"
    handler2 = agent.run(query2)

    async for ev in handler2.stream_events():
        if isinstance(ev, ToolCall):
            print(f"Tool selected: {ev.tool_name}")

    response2 = await handler2

    print(f"Query 2: {query2}")
    print(f"Response: {response2}")
    print("-" * 50)

    """
    Expected output:
    - Query 1: Agent selects vector_search for specific information
    - Query 2: Agent selects document_summary for high-level overview
    - Demonstrates intelligent tool selection based on query type
    - Shows LlamaIndex's agentic RAG strength
    """

if __name__ == "__main__":
    asyncio.run(main())
