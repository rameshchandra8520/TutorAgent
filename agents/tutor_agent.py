import google.generativeai as genai
from agents.math_agent import MathAgent
from agents.physics_agent import PhysicsAgent
from agents.chemistry_agent import ChemistryAgent
from agents.history_agent import HistoryAgent
from tools.gemini_utils import call_gemini_with_retry
from tools.conversation_manager import ConversationManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TutorAgent:
    def __init__(self, api_key):
        logger.info("Initializing Tutor Agent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Initialize conversation manager
        self.conversation_manager = ConversationManager()

        # Initialize sub-agents
        logger.info("Initializing sub-agents")
        self.math_agent = MathAgent(api_key)
        self.physics_agent = PhysicsAgent(api_key)
        self.chemistry_agent = ChemistryAgent(api_key)
        self.history_agent = HistoryAgent(api_key)

    def create_conversation(self, user_id=None):
        """Create a new conversation and return its ID"""
        return self.conversation_manager.create_conversation(user_id)

    def classify_query(self, query, conversation_id=None):
        logger.info("Classifying query type")
        
        # Get conversation history if conversation_id is provided
        history_text = ""
        if conversation_id:
            history_text = self.conversation_manager.get_formatted_history(conversation_id, limit=3)

        query_lower = query.lower()
        
        # Math keywords
        math_keywords = ["solve", "calculate", "equation", "x =", "math", "algebra", "arithmetic", "+", "-", "*", "/", "derivative", "integral", "matrix", "geometry"]
        
        # Physics keywords
        physics_keywords = ["newton", "force", "speed of light", "gravity", "physics", "velocity", "acceleration", "energy", "momentum", "wave", "quantum", "relativity"]
        
        # Chemistry keywords
        chemistry_keywords = ["chemistry", "chemical", "molecule", "atom", "element", "compound", "reaction", "periodic table", "bond", "ph", "acid", "base", "solution", "catalyst", "equilibrium"]
        
        # History keywords
        history_keywords = ["history", "historical", "war", "battle", "empire", "revolution", "ancient", "medieval", "renaissance", "century", "civilization", "king", "queen", "president", "napoleon", "caesar"]
        
        # Check for keyword matches
        if any(keyword in query_lower for keyword in math_keywords):
            logger.info("Query classified as math based on keywords")
            return "math"
        elif any(keyword in query_lower for keyword in physics_keywords):
            logger.info("Query classified as physics based on keywords")
            return "physics"
        elif any(keyword in query_lower for keyword in chemistry_keywords):
            logger.info("Query classified as chemistry based on keywords")
            return "chemistry"
        elif any(keyword in query_lower for keyword in history_keywords):
            logger.info("Query classified as history based on keywords")
            return "history"
        else:
            # Fallback: Use Gemini API for intent recognition
            logger.info("Using AI to classify query")
            context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
            prompt = f"{context}Classify this query into one of these categories: 'math', 'physics', 'chemistry', 'history', or 'unknown': {query}"

            response = call_gemini_with_retry(self.model, prompt)
            classification = response.strip().lower()
            print(f"AI called for Sub-Agent Selection")
            logger.info(f"AI classified query as: {classification}")
            return classification

    def handle_query(self, query, conversation_id=None, preferred_agent=None):
        """Handle a query with optional conversation context and preferred agent"""
        
        # If no conversation_id provided, create a new conversation
        if conversation_id is None:
            conversation_id = self.create_conversation()
            logger.info(f"Created new conversation: {conversation_id}")
        
        # Validate conversation exists
        if not self.conversation_manager.conversation_exists(conversation_id):
            logger.error(f"Conversation {conversation_id} not found")
            return "Error: Invalid conversation ID", None, None
        
        # Determine agent type - use preferred if specified, otherwise classify
        if preferred_agent and preferred_agent != 'auto':
            agent_type = preferred_agent
            logger.info(f"Using preferred agent: {agent_type}")
        else:
            agent_type = self.classify_query(query, conversation_id)
        
        # Get conversation history for the specific conversation
        conversation_history = self.conversation_manager.get_conversation_history(conversation_id, limit=5)
        
        if agent_type == "math":
            logger.info("Routing query to Math Agent")
            response = self.math_agent.handle_query(query, conversation_history)
        elif agent_type == "physics":
            logger.info("Routing query to Physics Agent")
            response = self.physics_agent.handle_query(query, conversation_history)
        elif agent_type == "chemistry":
            logger.info("Routing query to Chemistry Agent")
            response = self.chemistry_agent.handle_query(query, conversation_history)
        elif agent_type == "history":
            logger.info("Routing query to History Agent")
            response = self.history_agent.handle_query(query, conversation_history)
        else:
            logger.warning("Could not classify query, providing general response")
            history_text = self.conversation_manager.get_formatted_history(conversation_id, limit=3)
            context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
            prompt = f"{context}You are a helpful tutor. Please answer this question or reply with a general response based on the previous conversation: {query}"
            response = call_gemini_with_retry(self.model, prompt)
            agent_type = "general"

        # Add the interaction to conversation history
        self.conversation_manager.add_interaction(conversation_id, query, response, agent_type)
        
        return response, conversation_id, agent_type

    def get_conversation_history(self, conversation_id, limit=None):
        """Get the history for a specific conversation"""
        return self.conversation_manager.get_conversation_history(conversation_id, limit)

    def list_conversations(self, user_id=None):
        """List all conversations"""
        return self.conversation_manager.list_conversations(user_id)

    def delete_conversation(self, conversation_id):
        """Delete a specific conversation"""
        return self.conversation_manager.delete_conversation(conversation_id)

    def get_conversation_info(self, conversation_id):
        """Get information about a specific conversation"""
        return self.conversation_manager.get_conversation_info(conversation_id)