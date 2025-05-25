import logging
from tools.gemini_utils import call_gemini_with_retry
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_simple_scenario(scenario_description: str) -> str:
    """
    Simulate a simple physics scenario and describe the outcome using AI.
    
    Args:
        scenario_description (str): Description of the physics scenario to simulate
    
    Returns:
        str: Simple description of the scenario outcome with basic explanations
    """
    try:
        logger.info(f"Simulating physics scenario: {scenario_description}")
        
        # Configure Gemini for physics simulation
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
You are a physics tutor helping students understand simple physics scenarios. 

Scenario: {scenario_description}

Please provide a simple, educational response that includes:
1. What type of physics situation this is
2. What would happen in this scenario
3. Basic explanation of the physics principles involved
4. Keep it simple and easy to understand

Format your response in a clear, educational way suitable for students.
"""
        
        response = call_gemini_with_retry(model, prompt)
        print(f"AI called for Physics Scenario Simulation")
        return response
        
    except Exception as e:
        logger.error(f"Error simulating scenario: {str(e)}")
        return f"Error: Could not simulate scenario '{scenario_description}'. {str(e)}" 