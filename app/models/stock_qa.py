from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class IndicatorContext(BaseModel):
    """Technical indicator context"""
    rsi: Optional[float] = Field(None, description="Relative Strength Index")
    macd: Optional[str] = Field(None, description="MACD signal (bullish/bearish/neutral)")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-day Simple Moving Average")
    # Allow additional indicators
    extra: Optional[Dict[str, Any]] = Field(None, description="Additional indicators")


class StockContext(BaseModel):
    """Stock context information"""
    price: float = Field(..., description="Current stock price")
    indicators: IndicatorContext = Field(..., description="Technical indicators")


class StockQuestionRequest(BaseModel):
    """Request model for stock Q&A endpoint - minimal, natural language only"""
    question: str = Field(..., min_length=1, description="Natural language question about stocks or market")


class StockAnswer(BaseModel):
    """AI-generated answer structure - strict schema"""
    summary: str = Field(..., description="Plain text only, no markdown. 2-3 sentences max.")
    reasoning: List[str] = Field(default_factory=list, description="Clear, non-repetitive points. Each adds new information.")
    market_bias: str = Field(..., description="Market bias: Bullish, Bearish, Sideways, Cautious, or Mixed")
    what_to_watch: List[str] = Field(default_factory=list, description="Actionable items to monitor (earnings, FII/DII, RBI, etc.)")
    confidence_level: str = Field(..., description="Confidence: Low, Medium, or High")
    risk_note: str = Field(..., description="Short, responsible disclaimer without apologetic language")


class StockQuestionResponse(BaseModel):
    """Response model for stock Q&A endpoint - new format"""
    question: str = Field(..., description="User's question")
    understood_intent: str = Field(..., description="Detected intent: stock-specific, market-wide, or general")
    answer: StockAnswer = Field(..., description="AI-generated answer")
