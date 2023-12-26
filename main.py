from assistant_client import AssistantClient
from chat_loop import chat_loop
from utilities import setup_logging

def main():
    setup_logging()
    client = AssistantClient()
    client.initialize_assistant()
    chat_loop(client)

if __name__ == "__main__":
    main()
