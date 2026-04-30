import os

import litellm
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("LLM_CHAT_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing model: {model}")
try:
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        api_key=api_key
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
