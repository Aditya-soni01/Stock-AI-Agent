from openai import OpenAI
from typing import Dict, Optional, List
import re
from app.config.settings import OPENAI_API_KEY, MODEL_NAME
from app.utils.nlp_parser import parse_question
from app.tools.market_data import fetch_price
from app.agents.indicator_agent import IndicatorAgent
from app.agents.market_agent import MarketAgent

# Reuse OpenAI client configuration (OpenRouter)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY
)


class StockQAAgent:
    """AI agent for answering stock-related questions with auto-fetching"""
    
    def __init__(self):
        self.client = client
        self.model = MODEL_NAME
        self.market_agent = MarketAgent()
        self.indicator_agent = IndicatorAgent()
    
    def _fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Auto-fetch stock price and indicators for a symbol.
        Returns: {
            'price': float,
            'indicators': {'rsi': float, 'sma_20': float, ...},
            'available': bool
        }
        """
        try:
            # Fetch market data
            data = self.market_agent.analyze(symbol)
            if data is None or data.empty:
                return {'available': False, 'price': None, 'indicators': None}
            
            # Get latest price
            latest_price = float(data["Close"].iloc[-1])
            
            # Calculate indicators
            indicators = self.indicator_agent.analyze(data)
            
            return {
                'available': True,
                'price': latest_price,
                'indicators': indicators
            }
        except Exception as e:
            print(f"[StockQAAgent] Error fetching data for {symbol}: {e}")
            return {'available': False, 'price': None, 'indicators': None}
    
    def _calculate_confidence(self, intent: Dict, stock_data: Optional[Dict], question: str) -> str:
        """
        Calculate confidence level based on data availability and question clarity.
        Rules:
        - Future date + no live data → Medium
        - Symbol + indicators available → High
        - Vague or generic question → Low
        """
        # Future date reference with no live data
        if intent.get('has_time_reference') and not (stock_data and stock_data.get('available')):
            return "Medium"
        
        # Symbol detected with available data
        if intent['type'] == 'stock_specific' and stock_data and stock_data.get('available'):
            return "High"
        
        # Vague or generic question
        vague_keywords = ['what', 'how', 'why', 'explain', 'tell me about']
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in vague_keywords) and len(question.split()) < 5:
            return "Low"
        
        # Default to Medium
        return "Medium"
    
    def _get_intent_guidance(self, intent: Dict) -> str:
        """
        Get intent-specific guidance for the AI prompt.
        """
        intent_type = intent.get('type', 'general')
        time_ref = intent.get('time_reference', '')
        
        guidance_map = {
            'stock_specific': "Focus on trend analysis, momentum indicators, and price action. Provide specific technical insights.",
            'market_wide': "Focus on macro factors, sector rotation, FII/DII flows, and overall market sentiment. Consider NIFTY/SENSEX context.",
            'general': "Provide balanced market education and guidance. Cover both technical and fundamental perspectives."
        }
        
        base_guidance = guidance_map.get(intent_type, guidance_map['general'])
        
        # Add time-specific guidance
        if 'intraday' in time_ref.lower() or 'today' in time_ref.lower():
            base_guidance += " Emphasize volatility, risk management, and short-term price movements."
        elif 'long' in time_ref.lower() or 'month' in time_ref.lower() or 'year' in time_ref.lower():
            base_guidance += " Focus on fundamentals, earnings trajectory, and long-term value."
        
        return base_guidance
    
    def _build_prompt(
        self,
        question: str,
        intent: Dict,
        stock_data: Optional[Dict] = None
    ) -> tuple[str, str]:
        """
        Build system and user messages for the AI based on intent and available data.
        Returns: (system_message, user_message)
        """
        # Confident, mentor-like system prompt
        system_message = """You are a confident Indian stock market mentor with years of experience. You provide clear, actionable guidance without being apologetic.

Communication Style:
- Use probabilistic language: "Based on typical market behavior...", "Historically, markets tend to...", "If current conditions persist..."
- Never say "I can't", "I don't have access", or "I'm unable to"
- State assumptions clearly without apologizing
- Be direct and actionable, not defensive

Response Requirements:
1. Summary: Plain text only (NO markdown). 2-3 sentences maximum. Clear, confident answer.
2. Reasoning: 3-5 distinct points. Each point must add new information. No repetition.
3. Market Bias: One of: Bullish, Bearish, Sideways, Cautious, Mixed
4. What to Watch: 3-5 actionable items. For Indian markets, prioritize:
   - FII/DII activity and flows
   - US market performance and global cues
   - Earnings announcements and results
   - RBI commentary and policy decisions
   - USD/INR and crude oil trends
   - Sector-specific catalysts
5. Confidence Level: Low, Medium, or High
6. Risk Note: Short, professional disclaimer (1-2 sentences). No apologetic language.

CRITICAL: 
- Output ONLY plain text. NO markdown formatting (no **, ##, -, etc.) inside fields.
- Do NOT repeat section headers in the content.
- Each field has a single responsibility - do not mix concerns."""

        # Build context string based on intent and data
        context_str = ""
        data_available = False
        
        if intent['type'] == 'stock_specific' and stock_data and stock_data.get('available'):
            data_available = True
            symbol = intent['symbol']
            price = stock_data['price']
            indicators = stock_data['indicators']
            
            context_str = f"\nStock Symbol: {symbol}\n"
            context_str += f"Current Price: ₹{price:.2f}\n"
            context_str += "Technical Indicators (Live Data):\n"
            
            if indicators:
                if indicators.get('rsi') is not None:
                    context_str += f"- RSI: {indicators['rsi']:.2f}\n"
                if indicators.get('sma_20') is not None:
                    context_str += f"- 20-day SMA: ₹{indicators['sma_20']:.2f}\n"
        elif intent['type'] == 'stock_specific' and intent.get('symbol'):
            # Symbol detected but data fetch failed
            context_str = f"\nStock Symbol: {intent['symbol']}\n"
            context_str += "Note: Live data unavailable. Analysis based on typical market patterns and historical behavior.\n"
        elif intent['type'] == 'market_wide':
            context_str = "\nIntent: Overall market outlook\n"
            context_str += "Focus on macro factors, sector trends, and broad market sentiment.\n"
        else:
            context_str = "\nIntent: General stock market guidance\n"
        
        # Add time reference if detected
        if intent.get('has_time_reference') and intent.get('time_reference'):
            context_str += f"Time Reference: {intent['time_reference']}\n"
        
        # Get intent-specific guidance
        intent_guidance = self._get_intent_guidance(intent)
        
        user_message = f"""User Question: {question}
{context_str}

Intent Guidance: {intent_guidance}

Provide your response in this EXACT format (plain text only, no markdown):
Summary: [2-3 sentences, plain text, no formatting]
Reasoning: [Point 1]
Reasoning: [Point 2]
Reasoning: [Point 3]
Market Bias: [Bullish/Bearish/Sideways/Cautious/Mixed]
What to Watch: [Item 1]
What to Watch: [Item 2]
What to Watch: [Item 3]
Confidence Level: [Low/Medium/High]
Risk Note: [Short professional disclaimer, 1-2 sentences]

{"Use the live data provided above in your analysis." if data_available else "Base your analysis on typical market behavior and historical patterns. State assumptions clearly."}"""

        return system_message, user_message
    
    def _strip_markdown(self, text: str) -> str:
        """
        Remove markdown formatting from text.
        """
        if not text:
            return text
        
        # Remove markdown headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Remove list markers at start of lines
        text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
        # Remove numbered list markers
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _normalize_array(self, items: List[str]) -> List[str]:
        """
        Normalize array: remove duplicates, empty items, and trim whitespace.
        """
        if not items:
            return []
        
        normalized = []
        seen = set()
        
        for item in items:
            if not item:
                continue
            
            # Strip markdown and whitespace
            cleaned = self._strip_markdown(item.strip())
            
            if cleaned and cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                normalized.append(cleaned)
        
        return normalized[:5]  # Limit to 5 items
    
    def ask(self, question: str) -> Dict:
        """
        Ask a question about stocks/market and get an AI-generated answer.
        Auto-fetches data if stock symbol is detected.
        
        Args:
            question: Natural language question
        
        Returns:
            Dictionary with answer structure matching new format
        """
        # Parse question to extract intent and symbol
        intent = parse_question(question)
        
        # Auto-fetch stock data if symbol detected
        stock_data = None
        if intent['type'] == 'stock_specific' and intent.get('symbol'):
            stock_data = self._fetch_stock_data(intent['symbol'])
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, stock_data, question)
        
        # Build prompt
        system_msg, user_msg = self._build_prompt(question, intent, stock_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Parse the structured response
            parsed = self._parse_answer(answer_text, confidence)
            
            # Add intent information
            intent_label = {
                'stock_specific': 'Stock-specific analysis',
                'market_wide': 'Overall market outlook',
                'general': 'General stock market guidance'
            }.get(intent['type'], 'General stock market guidance')
            
            return {
                **parsed,
                'understood_intent': intent_label
            }
            
        except Exception as e:
            print(f"[StockQAAgent] Error: {e}")
            # Return a safe fallback response
            return {
                "summary": "Based on typical market patterns, this question requires more specific context. Consider rephrasing with a stock symbol or time frame.",
                "reasoning": ["Question needs clarification"],
                "market_bias": "Cautious",
                "what_to_watch": ["Market volatility", "Global economic indicators"],
                "confidence_level": "Low",
                "risk_note": "Market conditions are dynamic. Conduct your own research before making investment decisions.",
                "understood_intent": "General stock market guidance"
            }
    
    def _parse_answer(self, answer_text: str, default_confidence: str = "Medium") -> Dict:
        """
        Parse the AI response into structured format with strict schema.
        Handles both structured and unstructured responses.
        """
        summary = ""
        reasoning = []
        market_bias = "Cautious"
        what_to_watch = []
        confidence_level = default_confidence
        risk_note = ""
        
        lines = answer_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            line_stripped = line.strip()
            
            if line_lower.startswith('summary:'):
                summary = line.split(':', 1)[1].strip()
                current_section = None
            elif line_lower.startswith('reasoning:'):
                current_section = 'reasoning'
            elif line_lower.startswith('market bias:'):
                bias_text = line.split(':', 1)[1].strip().lower()
                if 'bullish' in bias_text:
                    market_bias = "Bullish"
                elif 'bearish' in bias_text:
                    market_bias = "Bearish"
                elif 'sideways' in bias_text or 'range' in bias_text:
                    market_bias = "Sideways"
                elif 'mixed' in bias_text:
                    market_bias = "Mixed"
                elif 'cautious' in bias_text or 'neutral' in bias_text:
                    market_bias = "Cautious"
                current_section = None
            elif line_lower.startswith('what to watch:'):
                current_section = 'what_to_watch'
            elif line_lower.startswith('confidence level:'):
                conf_text = line.split(':', 1)[1].strip().lower()
                if 'high' in conf_text:
                    confidence_level = "High"
                elif 'low' in conf_text:
                    confidence_level = "Low"
                else:
                    confidence_level = "Medium"
                current_section = None
            elif line_lower.startswith('risk note:'):
                risk_note = line.split(':', 1)[1].strip()
                current_section = None
            elif current_section == 'reasoning':
                # Extract reasoning point (remove markers)
                point = line_stripped.lstrip('- •*0123456789.').strip()
                if point:
                    reasoning.append(point)
            elif current_section == 'what_to_watch':
                # Extract watch item (remove markers)
                item = line_stripped.lstrip('- •*0123456789.').strip()
                if item:
                    what_to_watch.append(item)
            elif not summary and line_stripped and not line_lower.startswith(('summary', 'reasoning', 'market', 'what', 'confidence', 'risk')):
                # First non-header line might be summary
                summary = line_stripped
        
        # Strip markdown from all fields
        summary = self._strip_markdown(summary)
        reasoning = self._normalize_array(reasoning)
        what_to_watch = self._normalize_array(what_to_watch)
        risk_note = self._strip_markdown(risk_note)
        
        # Fallback: if parsing failed, extract from text
        if not summary:
            # Try to get first paragraph
            paragraphs = answer_text.split('\n\n')
            if paragraphs:
                summary = self._strip_markdown(paragraphs[0][:200])
            else:
                summary = self._strip_markdown(answer_text[:200])
        
        # Ensure we have reasoning
        if not reasoning:
            # Try to extract from text
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.lower().startswith(('summary', 'reasoning', 'market', 'what', 'confidence', 'risk')):
                    if len(stripped) > 20:
                        reasoning.append(self._strip_markdown(stripped))
                        if len(reasoning) >= 3:
                            break
        
        # Ensure we have what_to_watch
        if not what_to_watch:
            # Default Indian market watch items
            what_to_watch = [
                "FII/DII flows and activity",
                "US market performance and global cues",
                "RBI policy decisions and commentary"
            ]
        
        # Ensure we have risk note
        if not risk_note:
            risk_note = "Market conditions are dynamic. Conduct your own research and consider your risk tolerance before making investment decisions."
        
        # Limit summary length
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return {
            "summary": summary,
            "reasoning": reasoning[:5],  # Max 5 points
            "market_bias": market_bias,
            "what_to_watch": what_to_watch[:5],  # Max 5 items
            "confidence_level": confidence_level,
            "risk_note": risk_note
        }
