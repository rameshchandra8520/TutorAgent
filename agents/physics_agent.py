import google.generativeai as genai
from tools.constants import get_constant
from tools.gemini_utils import call_gemini_with_retry
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhysicsAgent:
    def __init__(self, api_key):
        logger.info("Initializing Physics Agent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def handle_query(self, query):
        logger.info("Processing physics query")
        # Check if the query asks for a constant
        constant_keywords = ["speed of light", "gravitational constant", "planck constant"]
        query_lower = query.lower()
        
        for constant in constant_keywords:
            if constant in query_lower:
                logger.info(f"Found physics constant request for: {constant}")
                result = get_constant(constant)
                if isinstance(result, str) and result.startswith("Error"):
                    logger.error(f"Error getting constant: {result}")
                    return result
                # Ask Gemini for an explanation
                prompt = f"Explain the significance of the {constant} in physics. Concisely."
                explanation = call_gemini_with_retry(self.model, prompt)
                print(f"AI called for Physics Constant Explanation")
                return f"Value: {result['value']} {result['unit']}\nExplanation: {explanation}"
        
        # No constant found, use Gemini for general physics query
        logger.info("Processing general physics query")
        response = call_gemini_with_retry(self.model, query)
        print(f"AI called for Physics General Query")
        return response