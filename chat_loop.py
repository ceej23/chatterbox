import os
import requests
import pprint
import json
from openai import OpenAI
from utilities import check_run, logger
from colorama import Fore, Style

def download_file(url, local_filename):
    """
    Downloads a file from a given URL to a specified local file path.

    :param url: URL of the file to download.
    :param local_filename: Local path to save the downloaded file.
    :return: Path to the downloaded file.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def chat_loop(client):
    """
    The main chat loop for interacting with the user.

    :param client: The AssistantClient instance for handling operations.
    """
    logger.info("Starting chat loop")
    user_options = ("Options: [1] Get help [2] Exit [3] Upload a local file "
                    "[4] Reference an internet file... or just ask a question!")
    user_instructions_request = "How can I help:"
    file_upload_instructions = "Enter the path to the file:"
    internet_file_instructions = "Enter the URL of the file:"
    user_file_analysis_request = ("What would you like to know about the file? "
                                  "([Enter] to provide basic insights):")

    default_file_prompt = ("Generate insights based on the provided file. "
                           "Provide these in dot points and include no more than 3.")
    file_directory = "files"  # Local directory to save downloaded files

    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

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
                messages = client.get_messages().data

                # Filter objects to isolate messages from current run
                filtered_messages = [obj for obj in messages if obj.run_id == run_id]

                for message in reversed(filtered_messages):
                    if message.role == "assistant":
                        print(f"{Fore.BLUE} Assistant: {message.content[0].text.value} {Style.RESET_ALL}")
            elif run_status == "requires_action":
                print(f"{Fore.BLUE} Assistant: I've identified an action to complete {Style.RESET_ALL}")
                print("\n\n")
                pprint.pprint(client.retrieve_run(run_id))
                run = client.retrieve_run(run_id)
                tool_call_id = run.required_action.submit_tool_outputs.tool_calls[0]
                function_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
                function_arguments = json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                
                function_response = globals()[function_name](function_arguments["url"])
                
                print("\n--------\nHere's the function response")
                pprint.pprint(function_response)
                print("\n--------\n\n")
                
                run = client.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=client.thread.id,
                    run_id=run_id,
                    tool_outputs=[
                        {
                            "tool_call_id": tool_call_id.id,
                            "output": function_response,
                        }
                    ],
                )
                run_status = check_run(client, client.thread.id, run_id)  # Wait for the run to complete

                if run_status == "completed":
                    messages = client.get_messages().data

                    # Filter objects to isolate messages from current run
                    filtered_messages = [obj for obj in messages if obj.run_id == run_id]

                    for message in reversed(filtered_messages):
                        if message.role == "assistant":
                            print(f"{Fore.BLUE} Assistant: {message.content[0].text.value} {Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED} Assistant: Something went wrong. {Style.RESET_ALL}")
            else:
                print(f"{Fore.RED} Assistant: Something went wrong. {Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            break

def call_gpt_vision(url):
    logger.info("Analysing image")

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe in detail what's contained within this image"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": url}
                    }
                ]
            }
        ],
        max_tokens=3000
    )

    return response.choices[0].message.content