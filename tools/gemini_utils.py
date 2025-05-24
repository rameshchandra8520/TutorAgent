import time
import logging
import hashlib
from .cache_utils import Cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize cache with 1-hour TTL
gemini_cache = Cache(ttl_seconds=3600)

def generate_cache_key(model_name: str, prompt: str) -> str:
    """Generate a unique cache key based on model name and prompt."""
    # Create a unique key combining model name and prompt
    combined = f"{model_name}:{prompt}"
    # Use MD5 for a fixed-length key that's deterministic
    return hashlib.md5(combined.encode()).hexdigest()

def call_gemini_with_retry(model, prompt, max_retries=3):
    # Generate cache key based on model name and prompt
    cache_key = generate_cache_key(model.model_name, prompt)
    
    # Check cache first
    cached_response = gemini_cache.get(cache_key)
    if cached_response is not None:
        logger.info("Using cached response")
        return cached_response

    # If not in cache, make API call
    for attempt in range(max_retries):
        try:
            logger.info(f"Making Gemini API call - Attempt {attempt + 1}/{max_retries}")
            response = model.generate_content(prompt).text
            logger.info("Gemini API call successful")
            
            # Cache the successful response
            gemini_cache.set(cache_key, response)
            
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Gemini API call failed (Attempt {attempt + 1}). Error: {str(e)}. Retrying...")
                time.sleep(2)  # Wait before retrying
                continue
            logger.error(f"All Gemini API attempts failed. Final error: {str(e)}")
            return f"Error: {str(e)}"

def clear_gemini_cache():
    """Clear the entire Gemini response cache."""
    gemini_cache.clear()

def remove_expired_cache_entries():
    """Remove expired entries from the cache."""
    gemini_cache.remove_expired()

def get_cache_size():
    """Get the current number of entries in the cache."""
    return gemini_cache.get_cache_size() 