from openai import OpenAI
from utilities import logger

default_image_prompt = "Analyse the image and provide an in-depth description of everything it contains"

call_gpt_vision_function_definition = {
    "type": "function",
    "function": {
        "name": "call_gpt_vision",
        "description": "When the user provides an image file (e.g., PNG, GIF, JPG), call the GPT Vision API to analyse an image and understand its contents. Take note of the parameters - when calling this tool, you need to provide both the url of the image and the users original prompt. Providing both is crucial.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Location of the file to be analyzed"
                },
                "prompt": {
                    "type": "string",
                    "description": "The user's original prompt"                    
                }
            },
            "required": ["url"]
        }
    }
}

def call_gpt_vision(url, prompt=default_image_prompt):
    logger.info(f"Analysing image: {url}")
    logger.info(f"With prompt: {prompt}")
    """
    Continuously checks the status of a run and logs the status.

    :param client: The AssistantClient instance.
    :param thread_id: The thread ID of the run.
    :param run_id: The run ID to be checked.
    """
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
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
    except Exception as e:
        logger.error(f"Error in calling the Vision API: {e}")
        raise
        
