import re
from typing import Optional, Dict, List


def extract_symbol(question: str) -> Optional[str]:
    """
    Extract stock symbol from natural language question.
    Looks for uppercase letter sequences (2-6 chars) that might be stock symbols.
    """
    # Common stock symbols pattern (2-6 uppercase letters)
    # Also handle .NS suffix for Indian stocks
    patterns = [
        r'\b([A-Z]{2,6})(?:\.NS)?\b',  # Standard symbols like AAPL, RELIANCE.NS
        r'\$([A-Z]{2,6})\b',  # $AAPL format
    ]
    
    question_upper = question.upper()
    
    for pattern in patterns:
        matches = re.findall(pattern, question_upper)
        if matches:
            # Return first match, remove .NS if present
            symbol = matches[0].replace('.NS', '')
            # Filter out common words that match pattern
            common_words = {'THE', 'AND', 'FOR', 'ARE', 'YOU', 'WILL', 'THIS', 'THAT', 'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW'}
            if symbol not in common_words and len(symbol) >= 2:
                return symbol
    
    return None


def detect_intent(question: str, symbol: Optional[str] = None) -> Dict[str, any]:
    """
    Detect the intent of the question.
    Returns: {
        'type': 'stock_specific' | 'market_wide' | 'general',
        'has_time_reference': bool,
        'time_reference': Optional[str],
        'symbol': Optional[str]
    }
    """
    question_lower = question.lower()
    
    # Time reference detection
    time_keywords = {
        'today', 'tomorrow', 'tuesday', 'wednesday', 'thursday', 'friday', 
        'monday', 'saturday', 'sunday', 'next week', 'this week', 'next month',
        'this month', 'next year', 'upcoming', 'future', 'later'
    }
    
    has_time_reference = any(keyword in question_lower for keyword in time_keywords)
    time_reference = None
    
    if has_time_reference:
        for keyword in time_keywords:
            if keyword in question_lower:
                time_reference = keyword
                break
    
    # Market-wide indicators
    market_wide_keywords = {
        'market', 'markets', 'nifty', 'sensex', 'dow', 'sp500', 's&p',
        'overall', 'general', 'broad', 'sector', 'economy', 'economic'
    }
    
    is_market_wide = any(keyword in question_lower for keyword in market_wide_keywords)
    
    # Determine intent type
    if symbol:
        intent_type = 'stock_specific'
    elif is_market_wide:
        intent_type = 'market_wide'
    else:
        intent_type = 'general'
    
    return {
        'type': intent_type,
        'has_time_reference': has_time_reference,
        'time_reference': time_reference,
        'symbol': symbol
    }


def parse_question(question: str) -> Dict[str, any]:
    """
    Main parser that extracts all information from a question.
    Returns intent dict with symbol extracted.
    """
    symbol = extract_symbol(question)
    intent = detect_intent(question, symbol)
    return intent
