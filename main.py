from openai import OpenAI
from dotenv import load_dotenv
from context_manager import context_manager
import os
from core import config
from context_manager import context_manager
from tools.terminal import run_command
import json

load_dotenv()
client = OpenAI(
    base_url="https://api.deepinfra.com/v1/openai", 
    api_key=os.getenv("DEEPINFRA_API_TOKEN"))

context_manager.add_user_message("What project are we working on?")
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
        reasoning_effort="xhigh",
        stream=True,
        tools=tools
    )


    _generated_once = False

    tools_queue = {}

    for chunk in resp:
        if not chunk.choices:
            break

        delta = chunk.choices[0].delta

        if delta.reasoning_content is not None:
            GREY = "\033[90m"
            RESET = "\033[0m"

            print(f"{GREY}{delta.reasoning_content}{RESET}", flush=True, end="")
            
        if not _generated_once:
            print()
            _generated_once = True
        
        if delta.content is not None:
            print(delta.content, flush=True, end="")

        if delta.tool_calls:
            tool = delta.tool_calls[0]
            if tool.function.name or tool.function.arguments:
                # print(tool)
                tool_index = str(tool.index)
                if tool_index not in tools_queue:
                    tools_queue[tool_index] = {'id':'', 'arguments':'', 'name':''}
                    tools_queue[tool_index]['id'] = tool.id

                if tool_index in tools_queue:
                    if not tools_queue[tool_index]['arguments'] and tool.function.arguments:
                        tools_queue[tool_index]['arguments'] = tool.function.arguments

                    if not tools_queue[tool_index]['name'] and tool.function.name:
                        tools_queue[tool_index]['name'] = tool.function.name

                # for tool in tools_queue:
                #     if tool tool['id']
                # if tool.function.name:

                for queue in list(tools_queue):
                    current_queue = tools_queue[queue]
                    if current_queue['arguments'] and current_queue['name']:
                        print(f"Calling {current_queue['name']} with arguments: {current_queue['arguments']}.")

                        result = globals()[current_queue['name']](**json.loads(current_queue['arguments']))
                        context_manager.add_custom_response(
                            {
                                "role": "assistant",
                                "content": None,
                                "tool_calls":[
                                        {
                                            "id": current_queue['id'],
                                            "type": "function",
                                            "function": {
                                                "name": current_queue['name'],
                                                "arguments": json.loads(current_queue['arguments'])
                                            }
                                        }
                                    ]
                            }
                        )
                        context_manager.add_tool_response(current_queue['id'], result)
                        del tools_queue[queue]


                #     tool_queue_name = tool.function.name

                # if tool_queue_name and tool.function.arguments:
                #     print(f"Calling {tool_queue_name} with arguments: {tool.function.arguments}.")
                #     result = globals()[tool_queue_name](**json.loads(tool.function.arguments))

                #     print(result)

                #     tool_queue_name = ""

    if context_manager.context[-1]['role'] != 'tool':
        print("Stopping the task")
        break

print('---'*5)
print(context_manager.context)
# print(resp.choices[0])
# print(resp.choices[0].message.reasoning_content)
# print("---")
# print(resp.choices[0].message.content)