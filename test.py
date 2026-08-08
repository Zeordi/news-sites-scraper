#!/usr/bin/env python3
"""
Lebanese News Scraper
A professional news scraping application for Lebanese news websites.
"""

import json
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Callable

from config import config
from scrapers import (
    scrape_addiyar, scrape_annahar, scrape_aljoumhouria, scrape_al_akhbar,
    scrape_nidaalwatan, scrape_aliwaa, scrape_elsharkonline, scrape_mtv,
    scrape_aljadeed, scrape_sawtbeirut, scrape_lebanondebate,
    scrape_lebanese_forces, scrape_lbcgroup
)

# Configure logging (console only)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NewsScraper:
    """Main news scraper class that coordinates all scraping operations."""
    
    def __init__(self):
        self.scrapers = {
            'addiyar': scrape_addiyar,
            'annahar': scrape_annahar,
            'aljoumhouria': scrape_aljoumhouria,
            'al_akhbar': scrape_al_akhbar,
            'nidaalwatan': scrape_nidaalwatan,
            'aliwaa': scrape_aliwaa,
            'elsharkonline': scrape_elsharkonline,
            'mtv': scrape_mtv,
            'aljadeed': scrape_aljadeed,
            'sawtbeirut': scrape_sawtbeirut,
            'lebanondebate': scrape_lebanondebate,
            'lebanese_forces': scrape_lebanese_forces,
            'lbcgroup': scrape_lbcgroup
        }
        
        # Sites that typically require Scrapfly
        self.scrapfly_sites = {
            'nidaalwatan', 'elsharkonline', 'sawtbeirut', 'lebanese_forces'
        }
    
    def scrape_site(self, site_name: str) -> Dict[str, Any]:
        """Scrape a single news site and return structured results."""
        scraper_func = self.scrapers.get(site_name)
        if not scraper_func:
            return {
                'site': site_name,
                'status': 'error',
                'error': f'Unknown site: {site_name}',
                'articles': [],
                'count': 0
            }
        
        logger.info(f"Scraping {site_name}...")
        
        try:
            articles = scraper_func()
            
            if articles:
                logger.info(f"SUCCESS {site_name}: Successfully scraped {len(articles)} articles")
                return {
                    'site': site_name,
                    'status': 'success',
                    'articles': articles,
                    'count': len(articles),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"WARNING {site_name}: No articles found")
                return {
                    'site': site_name,
                    'status': 'no_content',
                    'articles': [],
                    'count': 0,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"ERROR {site_name}: Scraping failed - {e}")
            return {
                'site': site_name,
                'status': 'error',
                'error': str(e),
                'articles': [],
                'count': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def scrape_all(self) -> Dict[str, Any]:
        """Scrape all configured news sites."""
        logger.info("Starting comprehensive news scraping...")
        
        results = {}
        total_articles = 0
        successful_sites = 0
        
        for site_name in self.scrapers.keys():
            result = self.scrape_site(site_name)
            results[site_name] = result
            
            if result['status'] == 'success':
                successful_sites += 1
                total_articles += result['count']
        
        # Generate summary
        summary = {
            'total_sites': len(self.scrapers),
            'successful_sites': successful_sites,
            'total_articles': total_articles,
            'success_rate': f"{(successful_sites / len(self.scrapers)) * 100:.1f}%",
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"SUMMARY Scraping completed: {successful_sites}/{len(self.scrapers)} sites successful")
        logger.info(f"SUMMARY Total articles scraped: {total_articles}")
        
        return {
            'summary': summary,
            'results': results
        }
    
    def print_results(self, results: Dict[str, Any], detailed: bool = False):
        """Print scraping results in a formatted way."""
        print("\n" + "="*60)
        print("🗞️  LEBANESE NEWS SCRAPER RESULTS")
        print("="*60)
        
        summary = results['summary']
        print(f"📊 Summary:")
        print(f"   • Total Sites: {summary['total_sites']}")
        print(f"   • Successful: {summary['successful_sites']}")
        print(f"   • Success Rate: {summary['success_rate']}")
        print(f"   • Total Articles: {summary['total_articles']}")
        print(f"   • Timestamp: {summary['timestamp']}")
        
        if detailed:
            print(f"\n📰 Detailed Results:")
            for site_name, result in results['results'].items():
                status_emoji = "✅" if result['status'] == 'success' else "❌"
                print(f"   {status_emoji} {site_name.title()}: {result['count']} articles")
                
                if result['status'] == 'error':
                    print(f"      Error: {result['error']}")
        
        print("="*60)

def main():
    """Main application entry point."""
    print("🚀 Lebanese News Scraper v2.0")
    print("Professional news scraping with Scrapfly integration")
    
    # Validate configuration
    if not config.validate_config():
        print("\n⚠️  Configuration Warning:")
        print("Some sites may be blocked without Scrapfly API key.")
        print("Set SCRAPFLY_API_KEY environment variable for full functionality.")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting. Please configure your API key and try again.")
            sys.exit(1)
    
    # Initialize scraper
    scraper = NewsScraper()
    
    # Run scraping
    try:
        results = scraper.scrape_all()
        scraper.print_results(results, detailed=True)
        
        # Save results to file
        output_file = f"scraping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()