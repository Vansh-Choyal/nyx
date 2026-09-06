from openai import OpenAI
from dotenv import load_dotenv
from context_manager import context_manager
import os
from core import config
from tools.terminal import run_command
import json

load_dotenv()
client = OpenAI(
    base_url="https://api.deepinfra.com/v1/openai", 
    api_key=os.getenv("DEEPINFRA_API_TOKEN"))

context_manager.add_user_message("What project are we working on? Can you find any bugs? Do NOT change anything, just tell me.")
# print(config['model'])

# print(context_manager.context)

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
    }
]

while True:
    resp = client.chat.completions.create(
        model=config['model'],
        messages=context_manager.context,
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
                print(f"Running command: {tool.function.arguments}")

    # print()

    # ---------------------------------------------------------
    # IMPORTANT:
    # Save the ASSISTANT message before saving tool responses.
    # ---------------------------------------------------------

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

        context_manager.context.append({
            "role": "assistant",
            "content": generated_content or None,
            "tool_calls": assistant_tool_calls
        })

        # Now execute tools and add their results
        for queue in tools_queue.values():
            result = globals()[queue["name"]](
                **json.loads(queue["arguments"])
            )

            context_manager.add_tool_response(
                queue["id"],
                result
            )

        # Continue to next model generation
        continue

    # No tool call => model is finished
    print("Stopping the task")
    break

print('---'*5)
print(context_manager.context)
# print(resp.choices[0])
# print(resp.choices[0].message.reasoning_content)
# print("---")
# print(resp.choices[0].message.content)