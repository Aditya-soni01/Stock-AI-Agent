from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Replace Upstox credentials with OANDA
    OANDA_API_KEY: str
    OANDA_ACCOUNT_ID: str
    OANDA_ENV: str = "practice"  # or "live"
    
    class Config:
        env_file = ".env"

settings = Settings()




# import os
# from dotenv import load_dotenv

# load_dotenv()

# UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
# UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
# UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")
# UPSTOX_TOKEN_FILE = os.getenv("UPSTOX_TOKEN_FILE")
