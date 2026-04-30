
import os
import litellm
from dotenv import load_dotenv

load_dotenv()

def test_pro():
    try:
        resp = litellm.completion(
            model="gemini/gemini-pro",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=10
        )
        print("Success with gemini-pro!")
        print(resp["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Error with gemini-pro: {e}")

if __name__ == "__main__":
    test_pro()
