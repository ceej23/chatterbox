import os
import openai
import vision
from dotenv import load_dotenv
from utilities import logger


function_definition = {
    "type": "function",
    "function": {
        "name": "call_gpt_vision",
        "description": "Call the GPT Vision API to analyse an image and understand its contents",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Location of the file to be analyzed"
                }
            },
            "required": ["url"]
        }
    }
}
class AssistantClient:
    def __init__(self):
        """
        Initializes the AssistantClient with API key and sets up the OpenAI client.
        """
        load_dotenv(override=True)
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.client = openai.Client()
        self.assistant = None
        self.thread = None

    def initialize_assistant(self):
        """
        Creates an assistant and initializes a new thread.
        Logs error and re-raises in case of an exception.
        """
        try:
            self.assistant = self.client.beta.assistants.create(
                name="Personal assistant",
                instructions="You are a personal assistant. Your job is to be as helpful as you can to the user and to answer all questions as accurately and succinctly as you can.",
                tools=[
                    {"type": "code_interpreter"},
                    function_definition
                ],
                model="gpt-4-1106-preview"
            )
            self.thread = self.client.beta.threads.create()
        except Exception as e:
            logger.error(f"Error in initializing assistant: {e}")
            raise

    def upload_file(self, file_path):
        """
        Uploads a file to the assistant and associates it with the assistant.
        Returns the file ID.
        """
        try:
            with open(file_path, "rb") as file:
                file_id = self.client.files.create(file=file, purpose='assistants').id
            self.client.beta.assistants.files.create(assistant_id=self.assistant.id, file_id=file_id)
            return file_id
        except Exception as e:
            logger.error(f"Error in uploading file: {e}")
            raise

    def send_message(self, user_input, input_type="text"):
        """
        Sends a message to the thread and returns the message object.
        """
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
        """
        Creates a run on the thread and returns the run ID.
        """
        try:
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id
            )
            return run.id  # Return the ID of the run
        except Exception as e:
            logger.error(f"Error in creating run: {e}")
            raise

    def retrieve_run(self, run_id):
        """
        Retrieves a run on the thread and run ID.
        """
        try:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_id
            )
            return run  # Return run
        except Exception as e:
            logger.error(f"Error in creating run: {e}")
            raise
        
    def get_messages(self):
        """
        Retrieves all messages from the thread and returns them.
        """
        try:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            return messages
        except Exception as e:
            logger.error(f"Error in getting messages: {e}")
            raise

    def get_run_status(self, thread_id, run_id):
        """
        Retrieves the status of a specific run and returns it.
        """
        try:
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            return run
        except Exception as e:
            logger.error(f"Error in getting run status: {e}")
            raise
