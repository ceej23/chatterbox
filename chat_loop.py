import os
import subprocess
from utilities import check_run, logger, download_file
from colorama import Fore, Back, Style

def chat_loop(client):
    """
    The main chat loop for interacting with the user.

    :param client: The AssistantClient instance for handling operations.
    """
    logger.info("Starting chat loop")
    user_options = ("Options: [1] Get help [2] Exit [3] Upload a local file [4] Reference an internet file... or just ask a question!")
    user_instructions_request = "How can I help:"
    file_upload_instructions = "Enter the path to the file:"
    internet_file_instructions = "Enter the URL of the file:"
    user_file_analysis_request = ("What would you like to know about the file? ([Enter] to provide basic insights):")
    default_file_prompt = ("Generate insights based on the provided file. Provide these in dot points and include no more than 3.")
    file_directory = "files"  # Local directory to save downloaded files

    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

    while True:
        print(f"{Fore.GREEN}{Back.BLACK}{user_options}{Style.RESET_ALL}")
        user_input = input(f"{Fore.CYAN} {user_instructions_request} {Style.RESET_ALL}")

        input_type = "text"

        if user_input == "1":
            continue
        elif user_input == "2" or user_input.lower() == "exit":
            break
        elif user_input == "3" or user_input.lower() == "file":
            input_type = "file"
            
            file_path = input(f"{Fore.CYAN} {file_upload_instructions} {Style.RESET_ALL}")
        elif user_input == "4":
            input_type = "file"
            
            file_url = input(f"{Fore.CYAN} {internet_file_instructions} {Style.RESET_ALL}")
            file_name = file_url.split('/')[-1]
            local_file_path = os.path.join(file_directory, file_name)
            
            try:
                file_path = download_file(file_url, local_file_path)
            except Exception as e:
                logger.error(f"Error downloading file: {e}")
                continue

        try:
            if input_type == "file":
                file_id = client.upload_file(file_path)
                logger.info(f"File upload successful: {file_id}")
                user_input = input(f"{Fore.CYAN} {user_file_analysis_request} {Style.RESET_ALL}")
                user_input = default_file_prompt if user_input == "" else user_input

            client.send_message(user_input, input_type)
            run_id = client.create_run()  # Capture the run ID
            run_status = check_run(client, client.thread.id, run_id)  # Wait for the run to complete

            if run_status == "completed":
                show_messages(client, run_id)
            elif run_status == "requires_action":
                client.process_action(run_id)

                run_status = check_run(client, client.thread.id, run_id)  # Wait for the run to complete

                if run_status == "completed":
                    show_messages(client, run_id)

                else:
                    print(f"{Fore.RED} Assistant: Something went wrong. {Style.RESET_ALL}")
            else:
                print(f"{Fore.RED} Assistant: Something went wrong. {Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            break

def show_messages(client, run_id):
    try:
        messages = client.get_messages().data
        # Filter objects to isolate messages from current run
        filtered_messages = [obj for obj in messages if obj.run_id == run_id]

        for message in reversed(filtered_messages):
            if message.role == "assistant":
                if message.content[0].type == "text":
                    print(f"{Fore.BLUE} Assistant: {message.content[0].text.value} {Style.RESET_ALL}")
                    if message.content[0].text.annotations:
                        for annotation in message.content[0].text.annotations:
                            file_id = annotation.file_path.file_id
                            download_and_open_image(client, file_id)
                elif message.content[0].type == "image_file":
                    file_id = message.content[0].image_file.file_id
                    download_and_open_image(client, file_id)
    except Exception as e:
        logger.error(f"Error showing messages: {e}")

                
def download_and_open_image(client, file_id):
    try:
        local_file_path = client.download_image_file(file_id)
        subprocess.run(["open", local_file_path])
    except Exception as e:
        logger.error(f"Error downloading and opening an image: {e}")
    
    
