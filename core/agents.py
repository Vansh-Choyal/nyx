import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os
from tools.terminal import run_command
from tools.read import read_file
from tools.grep import grep
from tools.patch import patch_file
from tools.write import write_file
from core.context_manager import context_manager

load_dotenv()
client = OpenAI(
    base_url="https://api.deepinfra.com/v1/openai", 
    api_key=os.getenv("DEEPINFRA_API_TOKEN"))

agents: dict[str, Agent] = {}

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command in the repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "The shell command to execute."
                    }
                },
                "required": ["cmd"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads a file from line x to line y. If end_line is 0, reads until the end of the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file you want to read."
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "The starting line number. Defaults to 1."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "The ending line number. Defaults to 0. If set to 0, reads the entire file from start_line to the end."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
    "type": "function",
        "function": {
            "name": "grep",
            "description": "Searches for a pattern in a file or directory using grep and returns matching lines with line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The text or pattern you want to search for."
                    },
                    "path": {
                        "type": "string",
                        "description": "The file or directory to search in."
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to search recursively through directories. Defaults to false."
                    }
                },
                "required": ["pattern", "path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "patch_file",
            "description": "Replaces an exact piece of text in a file with new text. The old text must match exactly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to modify."
                    },
                    "old_text": {
                        "type": "string",
                        "description": "The exact text in the file that should be replaced."
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The text that should replace old_text."
                    }
                },
                "required": ["file_path", "old_text", "new_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Creates a new file and writes content to it. If the file already exists, returns an error instructing the user to use patch_file instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to create."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write into the new file."
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    }
]

class Agent():
    def __init__(self, agent_name, model, system_prompt, tools_available, agents_allowed):
        self.agent_name = agent_name
        self.model = model
        self.system_prompt = system_prompt
        self.tools_available = tools_available
        self.agents_allowed = agents_allowed

        new_context = context_manager.create_context()
        new_context.add_system_prompt(system_prompt)

        self.context_id = new_context.context_id

    def _get_context(self):
        return context_manager.contexts[self.context_id]

    def start_iteration(self, message):

        self._get_context().add_user_message(message)

        print(f"Starting iteration for {self.agent_name} with Context ID {self.context_id}")

        while True:
            resp = client.chat.completions.create(
                model=self.model,
                messages=self._get_context().context,
                reasoning_effort="low",
                stream=True,
                tools=tools
            )

            tools_queue = {}
            generated_content = ""

            for chunk in resp:
                if not chunk.choices:
                    break

                delta = chunk.choices[0].delta

                if delta.reasoning_content is not None:
                    GREY = "\033[90m"
                    RESET = "\033[0m"
                    print(
                        f"{GREY}{delta.reasoning_content}{RESET}",
                        flush=True,
                        end=""
                    )

                if delta.content is not None:
                    generated_content += delta.content
                    print(delta.content, flush=True, end="")

                if delta.tool_calls:
                    tool = delta.tool_calls[0]
                    tool_index = str(tool.index)

                    if tool_index not in tools_queue:
                        tools_queue[tool_index] = {
                            "id": tool.id or "",
                            "name": "",
                            "arguments": ""
                        }

                    if tool.function.name:
                        tools_queue[tool_index]["name"] += tool.function.name

                    if tool.function.arguments:
                        tools_queue[tool_index]["arguments"] += tool.function.arguments

            # print()

            if tools_queue:
                assistant_tool_calls = []

                for queue in tools_queue.values():
                    assistant_tool_calls.append({
                        "id": queue["id"],
                        "type": "function",
                        "function": {
                            "name": queue["name"],
                            "arguments": queue["arguments"]
                        }
                    })

                self._get_context().add_assistant_message(
                    message=generated_content or None,
                    tool_calls=assistant_tool_calls
                )

                # context_manager.context.append({
                #     "role": "assistant",
                #     "content": generated_content or None,
                #     "tool_calls": assistant_tool_calls
                # })

                # Now execute tools and add their results
                for queue in tools_queue.values():
                    result = globals()[queue["name"]](
                        **json.loads(queue["arguments"])
                    )

                    self._get_context().add_tool_response(
                        queue["id"],
                        result
                    )

                # Continue to next model generation
                continue

            # No tool call => model is finished
            print("Stopping the task")
            break



