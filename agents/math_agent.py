import google.generativeai as genai
from tools.calculator import calculate
from tools.equation_solver import solve_equation
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

        # Check for equation solving patterns
        equation_patterns = [
            r"solve.*=",  # "solve x^2 + 3x + 2 = 0"
            r"\w+\s*[\^²³⁴⁵⁶⁷⁸⁹⁰]\s*\d*.*=",  # equations with exponents
            r"\w+\s*\*{2}\s*\d+.*=",  # equations with ** for exponents
            r"x\s*=|y\s*=|z\s*=",  # explicit variable assignments
            r"\w+\s*[+\-]\s*\w+\s*=",  # linear equations
        ]
        
        query_lower = query.lower()
        has_equation = any(re.search(pattern, query_lower) for pattern in equation_patterns)
        
        if has_equation or any(keyword in query_lower for keyword in ['solve', 'equation', 'find x', 'find y', 'find z']):
            logger.info("Detected equation to solve")
            result = solve_equation(query)
            if not result.startswith("Error"):
                context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
                prompt = f"{context}Explain how to solve this equation step by step: {query}. Be clear and educational."
                explanation = call_gemini_with_retry(self.model, prompt)
                print(f"AI called for Equation Explanation")
                return f"{result}\n\nStep-by-step explanation: {explanation}"
            else:
                logger.error(f"Error solving equation: {result}")
                return result
        
        # Check if the query contains a simple arithmetic expression
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
            # No arithmetic expression or equation, use Gemini for general math query
            logger.info("Processing general math query")
            context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
            prompt = f"{context}You are a math tutor. Please answer this math question: {query}"
            response = call_gemini_with_retry(self.model, prompt)
            print(f"AI called for Math General Query")
            return response