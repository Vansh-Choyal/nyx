from core import config

class ContextManager():
    def __init__(self, system_prompt = ""):
        self.system_prompt = system_prompt
        self.context = []

        self.construct_master_prompt()

    def construct_master_prompt(self):
        master_prompt = f"""You are {config['model_name']}, a coding agent. You would be given with a task and have to complete the task from start to finish.
        Start with exploring the relevant part of the repository using `grep` command before touching anything. Before starting, respond with what you are going to do first."""
        self.context.append({"role":'system', 'content': master_prompt})

        return master_prompt

    def add_user_message(self, message):
        self.context.append({'role':'user', "content": message})

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

context_manager = ContextManager()