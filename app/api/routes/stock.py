from fastapi import APIRouter, HTTPException
from app.agents.orchestrator import StockOrchestrator
from app.agents.stock_qa_agent import StockQAAgent
from app.models.stock_qa import StockQuestionRequest, StockQuestionResponse

router = APIRouter()
orchestrator = StockOrchestrator()
qa_agent = StockQAAgent()

@router.post("/analyze")
def analyze_stock(payload: dict):
    """
    payload example:
    {
      "query": "Analyze RELIANCE for intraday"
    }
    """

    query = payload.get("query", "")

    # very simple symbol extraction (can improve later)
    words = query.upper().split()
    symbol = next((w for w in words if w.isalpha()), None)

    if not symbol:
        return {
            "message": "Please provide a valid stock symbol",
            "confidence": 0
        }

    result = orchestrator.run(symbol)

    if result is None:
        return {
            "message": "Unable to fetch data for this stock",
            "confidence": 0
        }

    return {
        "message": result["explanation"],
        "confidence": int(result["decision"].get("confidence", 80)),
        "decision": result["decision"],
        "price": result["price"],
        "indicators": result["indicators"],
        "news_sentiment": result["news_sentiment"]
    }


@router.post("/ask", response_model=StockQuestionResponse)
async def ask_stock_question(request: StockQuestionRequest):
    """
    Ask a natural language question about stocks or market.
    Backend automatically detects symbols, fetches data, and handles intent.
    
    Request body (minimal):
    {
      "question": "What will the market be like on Tuesday?"
    }
    
    The backend will:
    - Parse the question to detect stock symbols
    - Auto-fetch price and indicators if symbol detected
    - Handle market-wide vs stock-specific questions
    - Return structured answer with intent and reasoning
    """
    try:
        # Validate question exists
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question is required and cannot be empty"
            )
        
        question = request.question.strip()
        
        # Get AI answer (agent handles everything: parsing, fetching, prompting)
        answer_data = qa_agent.ask(question)
        
        # Build response with new format
        from app.models.stock_qa import StockAnswer
        answer = StockAnswer(**{
            k: v for k, v in answer_data.items() 
            if k in ['summary', 'reasoning', 'market_bias', 'what_to_watch', 'confidence_level', 'risk_note']
        })
        
        return StockQuestionResponse(
            question=question,
            understood_intent=answer_data.get('understood_intent', 'General stock market guidance'),
            answer=answer
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Never throw errors for vague questions - return a helpful response instead
        from app.models.stock_qa import StockAnswer
        return StockQuestionResponse(
            question=request.question.strip() if request.question else "Unknown question",
            understood_intent="General stock market guidance",
            answer=StockAnswer(
                summary="Based on typical market patterns, this question requires more specific context. Consider rephrasing with a stock symbol or time frame.",
                reasoning=["Question needs clarification"],
                market_bias="Cautious",
                what_to_watch=["Market volatility", "Global economic indicators"],
                confidence_level="Low",
                risk_note="Market conditions are dynamic. Conduct your own research before making investment decisions."
            )
        )
