import json
from pathlib import Path
from core import agents
from core.context_manager import context_manager

agents_raw = []

# Define the directory path
directory_path = Path("agents/")

# Loop over everything inside the directory



for item in directory_path.iterdir():
    if item.is_file():
        print(f"File: {item.name} | Full Path: {item}")
        with open(item, 'r') as f:
            agents_raw.append(json.load(f))
    elif item.is_dir():
        print(f"Folder: {item.name}")

for agent in agents_raw:
    print(f"{type(agent["system_prompt"])} is System prompt of {len(agent["system_prompt"])} lines.")
    agent['system_prompt'] = "\n".join(agent["system_prompt"])
    print(f"After merging, the prompt length is {len(agent['system_prompt'])}")

# print(agents_raw)
print(f"Creating {len(agents_raw)} agent{"s" if len(agents_raw)>1 else''}")

for agent in agents_raw:
    agents.agents[agent["agent_name"]] = agents.Agent(agent["agent_name"], agent["model"], agent["system_prompt"], agent["tools_available"], agent["agents_available"])
    print(f"Created {agent["agent_name"]}.")


print(context_manager.contexts)