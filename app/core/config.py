from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # News API
    NEWS_API_KEY: str

    # Upstox (optional)
    UPSTOX_API_KEY: Optional[str] = None
    UPSTOX_API_SECRET: Optional[str] = None
    UPSTOX_REDIRECT_URI: Optional[str] = "http://localhost:8000/upstox/callback"
    UPSTOX_TOKEN_FILE: Optional[str] = "upstox_token.json"
    UPSTOX_FRONTEND_REDIRECT_URI: Optional[str] = "http://localhost:5173"

    # Execution mode (paper by default for safety)
    EXECUTION_MODE: str = "paper"
    PAPER_LEDGER_PATH: str = "data/paper_trades.json"
    PAPER_INITIAL_CAPITAL: float = 1_000_000.0
    PAPER_DEFAULT_QTY: int = 1

    # OANDA (optional)
    OANDA_API_KEY: Optional[str] = None
    OANDA_ACCOUNT_ID: Optional[str] = None
    OANDA_ENV: str = "practice"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Backward-compatible module-level aliases used by existing services.
OPENAI_API_KEY = settings.OPENAI_API_KEY
NEWS_API_KEY = settings.NEWS_API_KEY
UPSTOX_API_KEY = settings.UPSTOX_API_KEY
UPSTOX_API_SECRET = settings.UPSTOX_API_SECRET
UPSTOX_REDIRECT_URI = settings.UPSTOX_REDIRECT_URI
UPSTOX_TOKEN_FILE = settings.UPSTOX_TOKEN_FILE
UPSTOX_FRONTEND_REDIRECT_URI = settings.UPSTOX_FRONTEND_REDIRECT_URI
OANDA_API_KEY = settings.OANDA_API_KEY
OANDA_ACCOUNT_ID = settings.OANDA_ACCOUNT_ID
OANDA_ENV = settings.OANDA_ENV
EXECUTION_MODE = settings.EXECUTION_MODE
PAPER_LEDGER_PATH = settings.PAPER_LEDGER_PATH
PAPER_INITIAL_CAPITAL = settings.PAPER_INITIAL_CAPITAL
PAPER_DEFAULT_QTY = settings.PAPER_DEFAULT_QTY
