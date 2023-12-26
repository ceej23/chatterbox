import logging
from assistant_client import AssistantClient
from chat_loop import chat_loop
from utilities import setup_logging

def initialize_client():
    """
    Initializes the AssistantClient and returns the client instance.
    """
    client = AssistantClient()
    client.initialize_assistant()
    return client

def main():
    """
    Main function to set up logging, initialize the assistant client, and start the chat loop.
    """
    setup_logging(level=logging.INFO)
    client = initialize_client()
    chat_loop(client)

if __name__ == "__main__":
    main()
