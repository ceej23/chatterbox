from utilities import check_run, logger
from colorama import Fore, Style

def chat_loop(client):
    logger.info("Starting chat loop")
    while True:
        user_input = input(f"{Fore.CYAN} User: {Style.RESET_ALL}")
        if user_input == "quit":
            break
        try:
            client.send_message(user_input)
            run_id = client.create_run()  # Capture the run ID
            check_run(client, client.thread.id, run_id)  # Wait for the run to complete

            messages = client.get_messages().data
            # Find the latest assistant message
            assistant_message = next((msg for msg in reversed(messages) if msg.role == "assistant"), None)
            if assistant_message:
                response = assistant_message.content[0].text.value
                print(f"{Fore.BLUE} Assistant: {response} {Style.RESET_ALL}")
            else:
                logger.error("No assistant message found.")

        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            break