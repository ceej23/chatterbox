from utilities import check_run, logger
from colorama import Fore, Style
import pprint

def chat_loop(client):
    """
    The main chat loop for interacting with the user.

    :param client: The AssistantClient instance for handling operations.
    """
    logger.info("Starting chat loop")
    user_options = ("Options: [1] Get help [2] Exit [3] Upload a file ... "
                    "or just ask a question!")
    user_instructions_request = "How can I help:"
    file_upload_instructions = "What is the path to the file (local or remote):"
    file_upload_successful = "File upload successful: "
    user_file_analysis_request = ("What would you like to know about the file? "
                                  "([Enter] to provide basic insights):")
    default_file_prompt = ("Generate insights based on the provided file. "
                           "Provide these in dot points and include no more than 3.")

    while True:
        print(user_options)
        input_type = "text"
        user_input = input(f"{Fore.CYAN} {user_instructions_request} {Style.RESET_ALL}")

        if user_input == "1":
            print(user_options)
            continue
        elif user_input == "2" or user_input.lower() == "exit":
            break
        elif user_input == "3" or user_input.lower() == "file":
            input_type = "file"
            file_path = input(f"{Fore.CYAN} {file_upload_instructions} {Style.RESET_ALL}")

        try:
            if input_type == "file":
                file_id = client.upload_file(file_path)
                logger.info(file_upload_successful + file_id)
                user_input = input(f"{Fore.CYAN} {user_file_analysis_request} {Style.RESET_ALL}")
                user_input = default_file_prompt if user_input == "" else user_input

            client.send_message(user_input, input_type)
            run_id = client.create_run()  # Capture the run ID
            check_run(client, client.thread.id, run_id)  # Wait for the run to complete

            messages = client.get_messages().data

            # Filter objects to isolate messages from current run
            filtered_messages = [obj for obj in messages if obj.run_id == run_id]

            for message in reversed(filtered_messages):
                if message.role == "assistant":
                    print(f"{Fore.BLUE} Assistant: {message.content[0].text.value} {Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            break
