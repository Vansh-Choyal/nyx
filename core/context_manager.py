from core.core import config
import random

def _create_context_id():
    return f"CTX-{random.randint(1000000,9999999)}"

class Context():
    def __init__(self, context_id,  system_prompt = ""):
        self.system_prompt = system_prompt
        self.context = []
        self.context_id = context_id

    def add_user_message(self, message):
        self.context.append({'role':'user', "content": message})

    def add_assistant_message(self, message, tool_calls=[]):
        if tool_calls:
            self.context.append({'role':'assistant', "content": message, "tool_calls":tool_calls})
        else:
            self.context.append({'role':'assistant', "content": message})

    def add_system_prompt(self, content):
        self.context.append({'role':'system', "content": content})

    def add_tool_response(self, call_id, content):
        self.context.append({'role':'tool',
                            "tool_call_id": call_id,
                            "content": content
                            })

    def add_custom_response(self, response):
        self.context.append(response)
    # @property
    # def prompt(self):
    #     return 

class ContextManager():
    def __init__(self):
        self.contexts = {}

    def create_context(self):
        context_id = _create_context_id()
        new_context = Context(context_id=context_id)
        self.contexts[context_id] = new_context

        return new_context

context_manager = ContextManager()