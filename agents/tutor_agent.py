import google.generativeai as genai
from agents.math_agent import MathAgent
from agents.physics_agent import PhysicsAgent
from tools.gemini_utils import call_gemini_with_retry
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TutorAgent:
    def __init__(self, api_key):
        logger.info("Initializing Tutor Agent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Initialize sub-agents
        logger.info("Initializing sub-agents")
        self.math_agent = MathAgent(api_key)
        self.physics_agent = PhysicsAgent(api_key)

    def classify_query(self, query):
        logger.info("Classifying query type")
        # Simple keyword matching for intent recognition
        query = query.lower()
        math_keywords = ["solve", "calculate", "equation", "x =", "math"]
        physics_keywords = ["newton", "force", "speed of light", "gravity", "physics"]
        
        if any(keyword in query for keyword in math_keywords):
            logger.info("Query classified as math based on keywords")
            return "math"
        elif any(keyword in query for keyword in physics_keywords):
            logger.info("Query classified as physics based on keywords")
            return "physics"
        else:
            # Fallback: Use Gemini API for intent recognition
            logger.info("Using AI to classify query")
            prompt = f"Classify this query as 'math' or 'physics': {query}"
            response = call_gemini_with_retry(self.model, prompt)
            classification = response.strip().lower()
            print(f"AI called for Sub-Agent Selection")
            logger.info(f"AI classified query as: {classification}")
            return classification

    def handle_query(self, query):
        agent_type = self.classify_query(query)
        
        if agent_type == "math":
            logger.info("Routing query to Math Agent")
            return self.math_agent.handle_query(query)
        elif agent_type == "physics":
            logger.info("Routing query to Physics Agent")
            return self.physics_agent.handle_query(query)
        else:
            logger.warning("Could not classify query")
            return "Sorry, I couldn't classify your query. Please specify if it's a math or physics question."