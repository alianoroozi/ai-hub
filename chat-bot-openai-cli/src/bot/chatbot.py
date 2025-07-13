from datetime import datetime

from bot.chatgpt import ChatGPT
from db.mongodb_connection import mongodb_client


class ChatBotCli:
    def __init__(self, save_type="mongodb"):
        self.save_type = save_type

    def _save_interaction_file(
        self, user_message, response, feedback, feedback_file_path
    ):
        with open(feedback_file_path, "a") as f:
            time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"[{time_stamp}]\nPrompt: {user_message}\nResponse: {response}\nFeedback: {feedback}\n\n"
            )

    def _save_interaction_mongodb(self, user_message, response, feedback):
        try:
            interaction = {
                "timestamp": datetime.now(),
                "prompt": user_message,
                "response": response,
                "feedback": feedback,
            }
            mongodb_client.insert(interaction)

        except Exception as e:
            print(f"Error saving ineraction into mongodb: {str(e)}")

    def run(self):
        gpt = ChatGPT()

        print("Simple CLI Chat Tool (type 'quit' to exit)")

        chat_history = []
        response = None
        while True:
            user_input = input("User: ")

            if user_input.lower() in ["quit"]:
                print("Bye!")
                break

            if user_input.strip():
                response = gpt.ask(
                    user_message=user_input,
                    system_message=response,
                    history=chat_history,
                )

                print("Assisant: ", response)

                feedback = input("Feedback (y/n): ")
                if self.save_type == "mongodb":
                    self._save_interaction_mongodb(
                        user_input, response, feedback.lower()
                    )
                else:
                    FEEDBACK_FILE = "feedback_logs.txt"
                    self._save_interaction_file(
                        user_input, response, feedback.lower(), FEEDBACK_FILE
                    )


if __name__ == "__main__":
    chatbot = ChatBotCli()
    chatbot.run()
