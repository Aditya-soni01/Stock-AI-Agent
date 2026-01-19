from app.agents.market_agent import MarketAgent
from app.agents.trend_agent import TrendAgent
from app.agents.risk_agent import RiskAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.indicator_agent import IndicatorAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.portfolio_agent import PortfolioAgent
from app.models.portfolio import Portfolio
from app.data.portfolio_data import USER_PORTFOLIO
from app.agents.backtest_agent import BacktestAgent
from app.agents.trade_stats_agent import TradeStatsAgent
from app.agents.news_sentiment_agent import NewsSentimentAgent



class StockOrchestrator:
    def run(self, symbol: str):
        market_agent = MarketAgent()
        indicator_agent = IndicatorAgent()
        decision_agent = DecisionAgent()
        explanation_agent = ExplanationAgent()
        portfolio_agent = PortfolioAgent()
        backtest_agent = BacktestAgent()
        news_agent = NewsSentimentAgent()
        news_sentiment = news_agent.analyze(symbol)


        portfolio = Portfolio(USER_PORTFOLIO)

        data = market_agent.analyze(symbol)
        if data is None:
            return None

        indicators = indicator_agent.analyze(data)
        latest_price = float(data["Close"].iloc[-1])
        
        portfolio_info = portfolio_agent.analyze(symbol, portfolio)
        
       

        decision = decision_agent.decide(
            price=latest_price,
            sma=indicators["sma_20"],
            rsi=indicators["rsi"],
            news=news_sentiment
        )
        
        explanation = explanation_agent.explain(
            symbol,
            latest_price,
            indicators,
            decision
        )
        
        backtest = backtest_agent.run(
            data,
            indicator_agent.indicator_fn,
            decision_agent.decide
        )
        
        stats_agent = TradeStatsAgent()
        trade_statistics = stats_agent.calculate(backtest["trades"])

        return {
            "symbol": symbol,
            "price": latest_price,
            "portfolio": portfolio_info,
            "indicators": indicators,
            "decision": decision,
            "backtest": backtest,
            "trade_statistics": trade_statistics,
            "explanation": explanation,
            "news_sentiment": news_sentiment,
        }

