
import os

from dotenv import load_dotenv
from litellm import completion

load_dotenv()


def test_llm():
    model = os.getenv("LLM_CHAT_MODEL", "gemini/gemini-2.0-flash")
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"Testing model: {model}")
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": "Diga 'Olá, Meridiano!'"}],
            api_key=api_key
        )
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_llm()
