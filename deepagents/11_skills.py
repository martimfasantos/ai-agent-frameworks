from dotenv import load_dotenv

from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Skills: reusable, on-demand capabilities described in SKILL.md files
- Progressive disclosure (the agent reads a skill only when relevant)
- Seeding skill files into the virtual filesystem (StateBackend)

A skill is a folder containing a SKILL.md file with YAML frontmatter
(name + description). The agent sees each skill's name and description at
startup, but only reads the full instructions with read_file when a task
matches. Here we define a "haiku-writer" skill whose instructions require
ending every haiku with the marker "(fin)" — a distinctive fingerprint
that proves the skill was actually loaded and followed.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/skills
-----------------------------------------------------------------------
"""

# --- 1. Author a skill as a SKILL.md file (frontmatter + instructions) ---
SKILL_MD = """---
name: haiku-writer
description: Use when the user asks for a haiku. Writes a strict 5-7-5 syllable haiku.
---
# Haiku Writer Skill
When invoked, produce exactly three lines following 5-7-5 syllables.
Always end the haiku with the marker (fin).
"""

# --- 2. Create the agent, pointing skills= at the skills directory ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    skills=["/skills/"],
    # 0.7.0 trimmed the default prompt, so spell out the progressive-disclosure
    # step instead of relying on the model to take the initiative
    system_prompt=(
        "You are a helpful assistant. Before answering, check the available "
        "skills; if one matches, read its SKILL.md with read_file and follow "
        "those instructions exactly."
    ),
)

# --- 3. Seed the skill file into the virtual filesystem (StateBackend) ---
seed_files = {"/skills/haiku-writer/SKILL.md": create_file_data(SKILL_MD)}

# --- 4. Ask for something that matches the skill's description ---
print("=== Deep Agents Skills ===")
question = "Please write a haiku about the ocean."
result = agent.invoke(
    {"messages": [{"role": "user", "content": question}], "files": seed_files}
)

# --- 5. Show that the agent read the skill before answering ---
read_skill = False
for msg in result["messages"]:
    if msg.type == "ai" and msg.tool_calls:
        for tc in msg.tool_calls:
            if tc["name"] == "read_file" and "SKILL.md" in str(tc["args"]):
                read_skill = True
                print(f"\n[agent read the skill] {tc['args']['file_path']}")

print(f"\nUser: {question}")
print(f"Agent:\n{result['messages'][-1].text}")

# --- 6. The '(fin)' marker only appears if the skill instructions were followed ---
followed = "(fin)" in result["messages"][-1].text
print(f"\nSkill discovered & read: {read_skill}")
print(f"Skill instructions followed (ends with '(fin)'): {followed}")
