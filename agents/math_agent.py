import google.generativeai as genai
from tools.calculator import calculate
from tools.gemini_utils import call_gemini_with_retry
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MathAgent:
    def __init__(self, api_key):
        logger.info("Initializing Math Agent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def handle_query(self, query, history):
        logger.info("Processing math query")
        
        # Format conversation history
        history_text = ""
        if history:
            history_items = []
            for h in history[-3:]:  # Last 3 interactions
                if isinstance(h, dict) and 'query' in h and 'response' in h:
                    history_items.append(f"Q: {h['query']}")
                    history_items.append(f"A: {h['response']}")
            history_text = "\n".join(history_items)

        # Check if the query contains an arithmetic expression
        arithmetic_pattern = r"\d+\s*[\+\-\*/]\s*\d+"
        match = re.search(arithmetic_pattern, query)
        
        if match:
            expression = match.group(0)
            logger.info(f"Found arithmetic expression: {expression}")
            result = calculate(expression)
            if isinstance(result, str) and result.startswith("Error"):
                logger.error(f"Error calculating expression: {result}")
                return result
            # Ask Gemini for an explanation with context
            context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
            prompt = f"{context}Explain how to solve the arithmetic expression {expression}. Be clear and educational."
            explanation = call_gemini_with_retry(self.model, prompt)
            print(f"AI called for Math Explanation")
            return f"Result: {result}\nExplanation: {explanation}"
        else:
            # No arithmetic expression, use Gemini for general math query
            logger.info("Processing general math query")
            context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
            prompt = f"{context}You are a math tutor. Please answer this math question: {query}"
            response = call_gemini_with_retry(self.model, prompt)
            print(f"AI called for Math General Query")
            return response