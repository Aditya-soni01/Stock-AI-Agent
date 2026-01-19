# The line `from dotenv import load_dotenv` is importing the `load_dotenv` function from the `dotenv`
# module in Python. This function is used to load environment variables from a `.env` file into the
# current environment, making them accessible to your Python script.
from dotenv import load_dotenv
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b:free"

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "openai/gpt-oss-120b:free"

settings = Settings()
