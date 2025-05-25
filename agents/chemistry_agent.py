import google.generativeai as genai
from tools.gemini_utils import call_gemini_with_retry
from tools.constants import CHEMISTRY_CONSTANTS
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChemistryAgent:
    def __init__(self, api_key):
        logger.info("Initializing Chemistry Agent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def handle_query(self, query, history):
        logger.info("Processing chemistry query")
        
        # Format conversation history
        history_text = ""
        if history:
            history_items = []
            for h in history[-3:]:  # Last 3 interactions
                if isinstance(h, dict) and 'query' in h and 'response' in h:
                    history_items.append(f"Q: {h['query']}")
                    history_items.append(f"A: {h['response']}")
            history_text = "\n".join(history_items)

        # Check for specific chemistry patterns
        query_lower = query.lower()
        
        # Chemical formula pattern (e.g., H2O, NaCl, CH4)
        formula_pattern = r"\b[A-Z][a-z]?(?:\d+)?(?:[A-Z][a-z]?(?:\d+)?)*\b"
        formulas = re.findall(formula_pattern, query)
        
        # Chemical equation pattern (e.g., reactions with ->)
        equation_pattern = r"[A-Za-z0-9\+\s]+\s*[-=]>\s*[A-Za-z0-9\+\s]+"
        has_equation = re.search(equation_pattern, query)
        
        # Determine chemistry topic
        context = f"Previous conversation:\n{history_text}\n\n" if history_text else ""
        
        if has_equation:
            logger.info("Detected chemical equation")
            prompt = f"""{context}You are an expert chemistry tutor. The user has asked about a chemical equation or reaction. 
            Please provide a detailed explanation including:
            1. The type of reaction
            2. How to balance the equation (if needed)
            3. Products and reactants
            4. Any relevant chemical principles
            
            Question: {query}"""
            
        elif formulas:
            logger.info(f"Detected chemical formulas: {formulas}")
            prompt = f"""{context}You are an expert chemistry tutor. The user has asked about chemical compounds or formulas.
            Please provide information about:
            1. The chemical name and formula
            2. Molecular structure and properties
            3. Common uses or occurrence
            4. Any relevant chemical concepts
            
            Question: {query}"""
            
        elif any(keyword in query_lower for keyword in [
            'periodic table', 'element', 'atom', 'electron', 'proton', 'neutron', 
            'orbital', 'bond', 'ionic', 'covalent', 'molecular', 'valence',
            'ph', 'acid', 'base', 'solution', 'concentration', 'molarity',
            'reaction', 'catalyst', 'equilibrium', 'thermodynamics'
        ]):
            logger.info("Detected general chemistry concepts")
            prompt = f"""{context}You are an expert chemistry tutor. Please explain the chemistry concepts in this question clearly and thoroughly.
            Include examples, relevant formulas, and step-by-step explanations where appropriate.
            
            Question: {query}"""
            
        else:
            logger.info("Processing general chemistry query")
            prompt = f"""{context}You are an expert chemistry tutor. Please answer this chemistry-related question with clear explanations,
            examples, and any relevant chemical principles or formulas.
            
            Question: {query}"""

        response = call_gemini_with_retry(self.model, prompt)
        print(f"AI called for Chemistry Query")
        logger.info("Chemistry query processed successfully")
        return response

    def get_element_info(self, element_symbol):
        """Get information about a specific chemical element"""
        prompt = f"""Provide detailed information about the chemical element with symbol '{element_symbol}':
        - Full name
        - Atomic number
        - Atomic mass
        - Electron configuration
        - Common properties and uses
        - Position in periodic table"""
        
        return call_gemini_with_retry(self.model, prompt)

    def balance_equation(self, equation):
        """Help balance a chemical equation"""
        prompt = f"""Help balance this chemical equation and explain the process step by step: {equation}
        Show the balanced equation and explain the method used."""
        
        return call_gemini_with_retry(self.model, prompt) 