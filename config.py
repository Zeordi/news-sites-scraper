import os
from typing import Optional

class Config:
    """Configuration management for the news scraper application."""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables."""
        # Scrapfly API configuration
        self.SCRAPFLY_API_KEY: Optional[str] = os.getenv('SCRAPFLY_API_KEY')
        self.SCRAPFLY_API_URL: str = "https://api.scrapfly.io/scrape"
        
        # Request configuration
        self.DEFAULT_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '15'))
        self.REQUEST_DELAY: float = float(os.getenv('REQUEST_DELAY', '1.0'))
        
        # User agent strings for rotation
        self.USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        if not self.SCRAPFLY_API_KEY:
            print("⚠️  Warning: SCRAPFLY_API_KEY not found in environment variables.")
            print("   Set it with: export SCRAPFLY_API_KEY='your-api-key-here'")
            return False
        return True
    
    def get_default_headers(self) -> dict:
        """Get default headers for requests."""
        return {
            'User-Agent': self.USER_AGENTS[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

# Global configuration instance
config = Config() 