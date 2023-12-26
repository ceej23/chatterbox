from openai import OpenAI
from utilities import logger

function_definition = {
    "type": "function",
    "function": {
        "name": "vision.call_gpt_vision",
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
        max_tokens=300
    )

    return response.choices[0]
