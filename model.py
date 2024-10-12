from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()

# Retrieve the API keys
groq_api_key = os.getenv('GROQ_API_KEY')
langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
langchain_endpoint = os.getenv('LANGCHAIN_ENDPOINT')
langchain_project = os.getenv('LANGCHAIN_PROJECT')
langchain_tracing = os.getenv('LANGCHAIN_TRACING_V2')


# Check if the keys are loaded
if groq_api_key is None:
    raise EnvironmentError("GROQ_API_KEY is not set in the environment.")


if langchain_api_key is None:
    raise EnvironmentError("LANGSMITH_API_KEY is not set in the environment.")


# Initialize the ChatGroq models
llm = ChatGroq(
    groq_api_key=groq_api_key,
    temperature=0.7,
    model_name="llama-3.1-8b-instant"
)

"""        print(f"GROQ API Key: {groq_api_key}")
print(f"LangChain API Key: {langchain_api_key}")
print(f"LangChain Endpoint: {langchain_endpoint}")
print(f"LangChain Project: {langchain_project}")
print(f"LangChain Tracing: {langchain_tracing}")         """