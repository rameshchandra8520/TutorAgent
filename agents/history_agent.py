import google.generativeai as genai
from tools.gemini_utils import call_gemini_with_retry
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoryAgent:
    def __init__(self, api_key):
        logger.info("Initializing History Agent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def handle_query(self, query, history):
        logger.info("Processing history query")
        
        # Format conversation history
        history_text = ""
        if history:
            history_items = []
            for h in history[-3:]:  # Last 3 interactions
                if isinstance(h, dict) and 'query' in h and 'response' in h:
                    history_items.append(f"Q: {h['query']}")
                    history_items.append(f"A: {h['response']}")
            history_text = "\n".join(history_items)

        # Check for specific historical patterns
        query_lower = query.lower()
        
        # Date patterns (years, centuries, etc.)
        date_patterns = [
            r"\b\d{1,4}\s*(ad|ce|bc|bce)\b",  # Years with era
            r"\b\d{4}s?\b",  # Years like 1945, 1960s
            r"\b\d{1,2}(st|nd|rd|th)\s*century\b",  # Centuries
            r"\b(ancient|medieval|renaissance|modern|contemporary)\b"  # Historical periods
        ]
        
        has_dates = any(re.search(pattern, query_lower) for pattern in date_patterns)
        
        # Historical keywords
        historical_keywords = [
            'war', 'battle', 'empire', 'revolution', 'civilization', 'dynasty',
            'ancient', 'medieval', 'renaissance', 'industrial revolution',
            'world war', 'civil war', 'independence', 'conquest', 'discovery',
            'pharaoh', 'emperor', 'king', 'queen', 'president', 'dictator',
            'greek', 'roman', 'egyptian', 'persian', 'ottoman', 'british',
            'american', 'french', 'russian', 'chinese', 'japanese'
        ]
        
        # Famous historical figures
        historical_figures = [
            'caesar', 'napoleon', 'hitler', 'stalin', 'churchill', 'roosevelt',
            'washington', 'lincoln', 'kennedy', 'gandhi', 'mandela',
            'cleopatra', 'alexander', 'hannibal', 'marco polo', 'columbus'
        ]
        
        context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
        
        if has_dates:
            logger.info("Detected historical dates/periods")
            prompt = f"""{context}You are an expert history tutor. The user has asked about a specific historical time period or date.
            Please provide detailed information including:
            1. Key events that occurred during this time
            2. Important historical figures
            3. Social, political, and cultural context
            4. Significance and lasting impact
            
            Question: {query}"""
            
        elif any(keyword in query_lower for keyword in historical_keywords):
            logger.info("Detected historical keywords")
            prompt = f"""{context}You are an expert history tutor. Please provide comprehensive information about this historical topic.
            Include:
            1. Background and context
            2. Key events and timeline
            3. Important people involved
            4. Causes and consequences
            5. Historical significance
            
            Question: {query}"""
            
        elif any(figure in query_lower for figure in historical_figures):
            logger.info("Detected historical figure")
            prompt = f"""{context}You are an expert history tutor. The user is asking about a historical figure.
            Please provide detailed information including:
            1. Biographical information (birth, death, background)
            2. Major accomplishments and contributions
            3. Historical context and time period
            4. Legacy and impact on history
            5. Interesting facts or anecdotes
            
            Question: {query}"""
            
        elif any(geo_term in query_lower for geo_term in [
            'country', 'nation', 'territory', 'border', 'map', 'geography', 
            'capital', 'city', 'continent', 'region'
        ]):
            logger.info("Detected historical geography")
            prompt = f"""{context}You are an expert history tutor. The user is asking about historical geography or geopolitics.
            Please explain:
            1. Historical development of the region/territory
            2. Key events that shaped the geography
            3. Political changes over time
            4. Cultural and economic significance
            
            Question: {query}"""
            
        else:
            logger.info("Processing general history query")
            prompt = f"""{context}You are an expert history tutor. Please answer this historical question with:
            1. Clear, accurate historical information
            2. Proper historical context
            3. Multiple perspectives when appropriate
            4. Primary sources or evidence when relevant
            5. Connections to broader historical themes
            
            Question: {query}"""

        response = call_gemini_with_retry(self.model, prompt)
        print(f"AI called for History Query")
        logger.info("History query processed successfully")
        return response

    def get_timeline(self, topic, start_year=None, end_year=None):
        """Get a timeline for a specific historical topic"""
        time_range = ""
        if start_year and end_year:
            time_range = f" from {start_year} to {end_year}"
        elif start_year:
            time_range = f" starting from {start_year}"
        elif end_year:
            time_range = f" up to {end_year}"
            
        prompt = f"""Create a detailed timeline for {topic}{time_range}.
        Include major events, dates, and brief descriptions.
        Format as a chronological list."""
        
        return call_gemini_with_retry(self.model, prompt)

    def compare_periods(self, period1, period2):
        """Compare two historical periods"""
        prompt = f"""Compare and contrast {period1} with {period2}.
        Include:
        1. Key characteristics of each period
        2. Similarities and differences
        3. Political, social, and cultural aspects
        4. Technological and economic developments
        5. Lasting impacts"""
        
        return call_gemini_with_retry(self.model, prompt) 