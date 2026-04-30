
import os

from dotenv import load_dotenv
from litellm import embedding

load_dotenv()


def test_embedding():
    model = os.getenv("EMBEDDING_MODEL", "gemini/gemini-embedding-001")
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"Testing embedding model: {model}")
    try:
        response = embedding(
            model=model,
            input=["Teste de embedding"],
            api_key=api_key
        )
        print("Embedding generated successfully. Length:", len(response.data[0].embedding))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_embedding()
