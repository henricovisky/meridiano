
import os
import sys
from dotenv import load_dotenv

# Add src to sys.path
sys.path.append(os.path.abspath("src"))

from meridiano import llm_manager
import logging

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

def test_rating():
    model = os.getenv("LLM_CHAT_MODEL", "gemini/gemini-1.5-flash")
    prompt = "Rate the impact of this news: 'World peace achieved today' on a scale of 1-10. Output ONLY the number."
    messages = [{"role": "user", "content": prompt}]
    
    print(f"Testing model: {model}")
    response = llm_manager.llm_completion(model=model, messages=messages)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_rating()
