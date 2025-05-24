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

    def handle_query(self, query):
        logger.info("Processing math query")
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
            # Ask Gemini for an explanation
            prompt = f"Explain how to solve the arithmetic expression {expression}."
            explanation = call_gemini_with_retry(self.model, prompt)
            print(f"AI called for Math Explanation")
            return f"Result: {result}\nExplanation: {explanation}"
        else:
            # No arithmetic expression, use Gemini for general math query
            logger.info("Processing general math query")
            response = call_gemini_with_retry(self.model, query)
            print(f"AI called for Math General Query")
            return response