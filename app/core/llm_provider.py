import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

OPENAI_API_BASE=os.environ.get("OPENAI_API_BASE")
LLAMA_API_KEY=os.environ.get("LLAMA_API_KEY")
MODEL_NAME=os.environ.get("MODEL_NAME")
llm_params = {
                "model": "gpt-4o-az",
                "openai_api_base": OPENAI_API_BASE,
                "api_key": LLAMA_API_KEY,
                # "streaming": False,
                "temperature": 0.0
            }

# print(llm_params)

# Initialize the LLM model
llm = ChatOpenAI(**llm_params)




