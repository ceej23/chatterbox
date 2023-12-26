from utilities import check_run, logger
from colorama import Fore, Style

def chat_loop(client):
    logger.info("Starting chat loop")
    user_options = "Options: [1] Ask a question [2] Get help [3] Exit"

    while True:
        print(user_options)  # Display user options
        user_input = input(f"{Fore.CYAN} How can I help: {Style.RESET_ALL}")

        if user_input == "3" or user_input.lower() == "exit":  # Exit condition
            break
        elif user_input == "2":  # Example help command
            print("You can ask any question or type 'exit' to leave.")
            continue

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
