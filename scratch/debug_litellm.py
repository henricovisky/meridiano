
import litellm
from dotenv import load_dotenv

load_dotenv()


def test_debug():
    litellm.set_verbose = True
    try:
        resp = litellm.completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=10
        )
        print("Success!")
        print(resp)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_debug()
