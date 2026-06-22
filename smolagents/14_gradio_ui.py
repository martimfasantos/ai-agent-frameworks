from dotenv import load_dotenv

from smolagents import CodeAgent, GradioUI, OpenAIModel

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore smolagents with the following features:
- GradioUI for interactive agent chat interfaces
- One-line web UI deployment for any agent
- File upload support in agent conversations
- Reset memory between conversations

GradioUI (stable in v1.26+) wraps any smolagent in an interactive
web chat interface. It provides a ready-made UI for testing,
demos, and lightweight deployments without writing frontend code.

To run: uv run python 14_gradio_ui.py
Then open http://localhost:7860 in your browser.

For more details, visit:
https://huggingface.co/docs/smolagents/reference/agents#smolagents.GradioUI
-------------------------------------------------------
"""


def main():
    # --- Create an agent ---
    model = OpenAIModel(
        model_id=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    agent = CodeAgent(
        tools=[],
        model=model,
        max_steps=3,
    )

    # --- Launch the Gradio UI ---
    print("=== Launching Gradio UI ===")
    print("Open http://localhost:7860 in your browser")
    print("Press Ctrl+C to stop\n")

    ui = GradioUI(
        agent=agent,
        file_upload_folder="./uploads",  # Enable file uploads
        reset_agent_memory=True,         # Clear memory between chats
    )
    ui.launch(
        server_name="127.0.0.1",
        server_port=7860,
    )


if __name__ == "__main__":
    main()
