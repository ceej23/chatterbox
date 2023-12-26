import os
import openai
from dotenv import load_dotenv
from utilities import logger

class AssistantClient:
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.client = openai.Client()
        self.assistant = None
        self.thread = None

    def initialize_assistant(self):
        try:
            self.assistant = self.client.beta.assistants.create(
                name="Personal assistant",
                instructions="You are a personal assistant...",
                tools=[{"type": "code_interpreter"}],
                model="gpt-4-1106-preview"
            )
            self.thread = self.client.beta.threads.create()
        except Exception as e:
            logger.error(f"Error in initializing assistant: {e}")
            raise

    def send_message(self, user_input):
        try:
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=user_input
            )
            return message
        except Exception as e:
            logger.error(f"Error in sending message: {e}")
            raise

    def create_run(self):
        try:
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
            return run.id  # Return the ID of the run
        except Exception as e:
            logger.error(f"Error in creating run: {e}")
            raise

    def get_messages(self):
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
            return messages
        except Exception as e:
            logger.error(f"Error in getting messages: {e}")
            raise

    def get_run_status(self, thread_id, run_id):
        try:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            return run
        except Exception as e:
            logger.error(f"Error in getting run status: {e}")
            raise