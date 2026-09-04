from openai import OpenAI
from dotenv import load_dotenv
from context_manager import context_manager
import os
from core import config
from context_manager import context_manager

load_dotenv()
client = OpenAI(
    base_url="https://api.deepinfra.com/v1/openai", 
    api_key=os.getenv("DEEPINFRA_API_TOKEN"))

context_manager.add_user_message("Change the _+ new project_ -> create new project on the /projects page")
print(config['model'])

print(context_manager.context)
resp = client.chat.completions.create(
    model=config['model'],
    messages=context_manager.context,
    reasoning_effort="xhigh",
    stream=True
)


_generated_once = False
for chunk in resp:
    if not chunk.choices:
        break

    delta = chunk.choices[0].delta

    if delta.reasoning_content is not None:
        print(delta.reasoning_content, flush=True, end="")

    if not _generated_once:
        print()
        _generated_once = True
    if delta.content is not None:
        print(delta.content, flush=True, end="")
# print(resp.choices[0])
# print(resp.choices[0].message.reasoning_content)
# print("---")
# print(resp.choices[0].message.content)