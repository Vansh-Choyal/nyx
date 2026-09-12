from core import startup
from core import agents

print(agents.agents)

explorer_agent = agents.agents["main-agent"]
explorer_agent.start_iteration("Hello")

