
import os
import litellm
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return
    
    # LiteLLM doesn't have a direct "list models" for Gemini that is easy to call without an SDK
    # but we can try to call a known one or use the google-generativeai sdk if installed.
    # Let's try to check what LiteLLM thinks are valid Gemini models.
    # print(f"LiteLLM version: {litellm.__version__}")
    
    # Try a simple call with a different naming convention
    models_to_try = [
        "gemini/gemini-1.5-flash",
        "gemini/gemini-1.5-flash-latest",
        "google/gemini-1.5-flash"
    ]
    
    for model in models_to_try:
        print(f"\nTrying model: {model}")
        try:
            resp = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=10
            )
            print(f"Success with {model}!")
            print(resp["choices"][0]["message"]["content"])
            break
        except Exception as e:
            print(f"Failed with {model}: {e}")

if __name__ == "__main__":
    list_models()
