from app.agents.orchestrator import StockOrchestrator

def run_stock_workflow(symbol: str):
    return StockOrchestrator().run(symbol)
