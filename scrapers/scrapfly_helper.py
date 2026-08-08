import requests
from bs4 import BeautifulSoup
import sys
import os
import logging
import time

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Set up logging
logger = logging.getLogger(__name__)

def scrapfly_get(url, timeout=15, headers=None):
    """
    Make a request using Scrapfly API with anti-scraping protection.
    Returns a response-like object with .content attribute.
    """
    if not config.SCRAPFLY_API_KEY:
        raise requests.exceptions.RequestException("Scrapfly API key not configured")
    
    try:
        params = {
            'key': config.SCRAPFLY_API_KEY,
            'url': url,
            'asp': 'true'
        }
        
        response = requests.get(config.SCRAPFLY_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # Create a response-like object
        class ScrapflyResponse:
            def __init__(self, content):
                self.content = content.encode('utf-8')
                self.text = content
                self.status_code = 200
                
            def raise_for_status(self):
                pass
        
        return ScrapflyResponse(data['result']['content'])
        
    except Exception as e:
        logger.error(f"Scrapfly error for {url}: {e}")
        raise requests.exceptions.RequestException(f"Scrapfly failed: {e}")

def get_with_fallback(url, timeout=15, headers=None):
    """
    Smart fallback system: tries regular requests first, then Scrapfly on 403 errors.
    """
    # Use default headers if none provided
    if headers is None:
        headers = config.get_default_headers()
    
    try:
        # First try regular requests
        logger.debug(f"Attempting regular request to {url}")
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        logger.debug(f"Regular request successful for {url}")
        return response
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.info(f"403 error detected for {url}, trying Scrapfly...")
            try:
                time.sleep(config.REQUEST_DELAY)  # Rate limiting
                return scrapfly_get(url, timeout, headers)
            except Exception as scrapfly_error:
                logger.error(f"Scrapfly also failed for {url}: {scrapfly_error}")
                raise e  # Re-raise original error
        else:
            logger.error(f"HTTP error for {url}: {e}")
            raise e
    except Exception as e:
        logger.error(f"Request error for {url}: {e}")
        raise e 