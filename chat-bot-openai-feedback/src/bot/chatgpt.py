from openai import OpenAI


SYSTEM_PROMPT = """
You are a helpful assisant.
"""


class ChatGPT:
    def __init__(self):
        self.client = OpenAI()

    def ask(
        self,
        user_message: str,
        system_message: str = None,
        history: list = [],
        model: str = "gpt-4o-mini",
    ):
        if system_message is None:
            system_message = SYSTEM_PROMPT

        history += [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": system_message},
        ]

        response = self.client.responses.create(model=model, input=history)
        return response.output_text
