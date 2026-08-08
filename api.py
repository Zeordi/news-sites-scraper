from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scrapers import (
    scrape_addiyar, 
    scrape_annahar, 
    scrape_aljoumhouria, 
    scrape_al_akhbar,
    scrape_nidaalwatan,
    scrape_aliwaa,
    scrape_elsharkonline,
    scrape_mtv,
    scrape_aljadeed,
    scrape_sawtbeirut,
    scrape_lebanondebate,
    scrape_lebanese_forces,
    scrape_lbcgroup,
    scrape_almarkazia
) 

app = FastAPI(
    title="Lebanese News Scraper API",
    description="API for scraping Lebanese news sites with anti-blocking capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map site names to their scraper functions
SCRAPER_MAPPING = {
    "addiyar": scrape_addiyar,
    "annahar": scrape_annahar,
    "aljoumhouria": scrape_aljoumhouria,
    "alakhbar": scrape_al_akhbar,
    "nidaalwatan": scrape_nidaalwatan,
    "aliwaa": scrape_aliwaa,
    "elsharkonline": scrape_elsharkonline,
    "mtv": scrape_mtv,
    "aljadeed": scrape_aljadeed,
    "sawtbeirut": scrape_sawtbeirut,
    "lebanondebate": scrape_lebanondebate,
    "lebaneseforces": scrape_lebanese_forces,
    "lbcgroup": scrape_lbcgroup,
    "almarkazia": scrape_almarkazia,
}

@app.get("/")
async def root():
    """
    API root endpoint with basic information.
    """
    return {
        "message": "Lebanese News Scraper API",
        "version": "1.0.0",
        "available_sites": list(SCRAPER_MAPPING.keys()),
        "endpoints": {
            "scrape_site": "/scrape/{site_name}",
            "scrape_all": "/scrape-all",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "message": "API is running"}

@app.get("/scrape/{site_name}")
async def scrape_site_by_name(site_name: str):
    """
    Scrapes a specific news site by its name.
    
    Available sites: addiyar, annahar, aljoumhouria, alakhbar, nidaalwatan, 
    aliwaa, elsharkonline, mtv, aljadeed, sawtbeirut, lebanondebate, 
    lebaneseforces, lbcgroup, almarkazia
    """
    scraper_function = SCRAPER_MAPPING.get(site_name.lower())
    
    if not scraper_function:
        available_sites = ", ".join(SCRAPER_MAPPING.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Site '{site_name}' not found. Available sites: {available_sites}"
        )
        
    try:
        scraped_data = scraper_function()
        if not scraped_data:
            raise HTTPException(status_code=404, detail=f"No articles found for {site_name}.")
            
        return {
            "site": site_name,
            "articles_count": len(scraped_data),
            "articles": scraped_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while scraping {site_name}: {str(e)}")

@app.get("/scrape-all")
async def scrape_all_sites():
    """
    Scrapes all available news sites.
    """
    results = {}
    total_articles = 0
    
    for site_name, scraper_function in SCRAPER_MAPPING.items():
        try:
            scraped_data = scraper_function()
            results[site_name] = {
                "status": "success",
                "articles_count": len(scraped_data) if scraped_data else 0,
                "articles": scraped_data or []
            }
            total_articles += len(scraped_data) if scraped_data else 0
        except Exception as e:
            results[site_name] = {
                "status": "error",
                "error": str(e),
                "articles_count": 0,
                "articles": []
            }
    
    return {
        "total_sites": len(SCRAPER_MAPPING),
        "total_articles": total_articles,
        "results": results
    } 