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

    def handle_query(self, query, history):
        logger.info("Processing physics query")
        
        # Format conversation history
        history_text = ""
        if history:
            history_items = []
            for h in history[-3:]:  # Last 3 interactions
                if isinstance(h, dict) and 'query' in h and 'response' in h:
                    history_items.append(f"Q: {h['query']}")
                    history_items.append(f"A: {h['response']}")
            history_text = "\n".join(history_items)
        
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
                # Ask Gemini for an explanation with context
                context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
                prompt = f"{context}Explain the significance of the {constant} in physics. Be concise but informative."
                explanation = call_gemini_with_retry(self.model, prompt)
                print(f"AI called for Physics Constant Explanation")
                return f"Value: {result['value']} {result['unit']}\nExplanation: {explanation}"
        
        # No constant found, use Gemini for general physics query
        logger.info("Processing general physics query")
        context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
        prompt = f"{context}You are a physics tutor. Please answer this physics question: {query}"
        response = call_gemini_with_retry(self.model, prompt)
        print(f"AI called for Physics General Query")
        return response