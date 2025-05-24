import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_gemini_with_retry(model, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.info(f"Making Gemini API call - Attempt {attempt + 1}/{max_retries}")
            response = model.generate_content(prompt).text
            logger.info("Gemini API call successful")
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Gemini API call failed (Attempt {attempt + 1}). Error: {str(e)}. Retrying...")
                time.sleep(2)  # Wait before retrying
                continue
            logger.error(f"All Gemini API attempts failed. Final error: {str(e)}")
            return f"Error: {str(e)}" 