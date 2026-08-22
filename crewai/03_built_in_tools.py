import os

from crewai import Agent, Task, Crew
from crewai_tools import (
    WebsiteSearchTool,
    FileReadTool,
    DirectoryReadTool,
    ScrapeWebsiteTool,
    WaitTool,
)

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following built-in tools from crewai_tools:
- Web search and scraping tools
- File and directory operations
- WaitTool for pausing between steps (stdlib only, no API key)
- Integration with external APIs

This example demonstrates the variety of built-in tools available in CrewAI
and how to use them effectively in certain tasks.

For more details, visit:
https://docs.crewai.com/en/concepts/tools#available-crewai-tools
-------------------------------------------------------
"""
# --- 1. Create agent with the built-in tools ---
multi_tool_agent = Agent(
    role="All-in-One Specialist",
    goal="Utilize all available tools to accomplish diverse tasks efficiently",
    backstory=(
        "You are a versatile agent equipped with web, file, and code tools. "
        "You can research, scrape websites, analyze files, and execute code as needed."
    ),
    tools=(
        WebsiteSearchTool(),
        FileReadTool(),
        DirectoryReadTool(directory="."),
        ScrapeWebsiteTool(),
        WaitTool(),
    ),
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
)

# --- 2. Define a simple web scraping task ---
simple_scrape_task = Task(
    description=(
        "Scrape the official CrewAI website (https://crewai.com) and "
        "provide a summary of its main features and offerings."
    ),
    expected_output=(
        "A concise summary in bullet points of CrewAI's main features and offerings "
        "as found on the official website."
    ),
    agent=multi_tool_agent,
)

# --- 3. Create a crew with one agent ---
crew = Crew(agents=[multi_tool_agent], tasks=[simple_scrape_task])

# --- 4. Run the crew ---
result = crew.kickoff()
# no need to print, as verbose=True will show the output in the terminal
