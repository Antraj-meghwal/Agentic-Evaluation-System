# HTTP requests
import requests

# Environment variables
import os

# Base64 encoding
import base64

# Load .env
from dotenv import load_dotenv


# Load environment
load_dotenv()


# Hugging Face API token
HF_TOKEN = os.getenv("HF_TOKEN")


# Hugging Face model endpoint
API_URL = (
    "https://api-inference.huggingface.co/models/"
    "Qwen/Qwen2-VL-7B-Instruct"
)


# Auth headers
headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


# -----------------------------------
# Convert image to base64
# -----------------------------------
def encode_image(image_path: str):

    with open(image_path, "rb") as image_file:

        return base64.b64encode(

            image_file.read()

        ).decode("utf-8")


# -----------------------------------
# Grade answer sheet image
# -----------------------------------
def grade_answer_sheet(

    image_path: str,

    rubric: str
):

    # Encode image
    image_base64 = encode_image(
        image_path
    )

    # Prompt
    prompt = f"""

    You are an academic evaluator.

    Grade the student's handwritten
    answer sheet using the rubric.

    RUBRIC:
    {rubric}

    Return STRICT JSON:

    {{
      "score": number,
      "feedback": "short feedback",
      "confidence": number
    }}
    """

    # Request payload
    payload = {

        "inputs": {

            "image": image_base64,

            "text": prompt
        }
    }

    # API request
    response = requests.post(

        API_URL,

        headers=headers,

        json=payload
    )

    return response.json()