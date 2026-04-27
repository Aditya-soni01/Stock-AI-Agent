from dotenv import load_dotenv
import os

# Load .env first so getenv() sees the values
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b:free")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Upstox (API Key & Secret used only in backend)
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/upstox/callback")
UPSTOX_TOKEN_FILE = os.getenv("UPSTOX_TOKEN_FILE", "upstox_token.json")
UPSTOX_FRONTEND_REDIRECT_URI = os.getenv("UPSTOX_FRONTEND_REDIRECT_URI", "http://localhost:5173")


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b:free")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
    UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
    UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/upstox/callback")
    UPSTOX_TOKEN_FILE = os.getenv("UPSTOX_TOKEN_FILE", "upstox_token.json")
    UPSTOX_FRONTEND_REDIRECT_URI = os.getenv("UPSTOX_FRONTEND_REDIRECT_URI", "http://localhost:5173")


settings = Settings()
