import requests
from bs4 import BeautifulSoup
import re

def scrape_site(url, site_name):
    """A generic template to scrape a news site."""
    print("Scraping %s (placeholder)..." % site_name)
    return []

def _get_lebanondebate_article_text(article_url):
    """Helper function to fetch and parse article text from a lebanondebate.com article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        # First try to get summary text
        summary_div = soup.select_one("div.summary-text.text")
        summary_text = ""
        if summary_div:
            summary_paragraphs = summary_div.find_all("p")
            summary_text = "\n".join(p.get_text(strip=True) for p in summary_paragraphs if p.get_text(strip=True))
        
        # Then get main article text
        content_div = soup.select_one("div.article-texts.text")
        if not content_div:
            return summary_text if summary_text else "Article content not found."

        # Remove any ads and unwanted elements
        for element in content_div.select("div[id*='gpt'], div.advertisement, iframe, script"):
            element.decompose()
            
        # Extract text from paragraphs
        paragraphs = content_div.find_all("p")
        article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        # Combine summary and article text
        full_text = ""
        if summary_text:
            full_text += summary_text + "\n\n"
        if article_text:
            full_text += article_text
            
        return full_text if full_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_nna_leb():
    return scrape_site("https://www.nna-leb.gov.lb", "NNA Lebanon")

def scrape_lebanondebate():
    """
    Scrapes featured articles from lebanondebate.com.
    """
    URL = "https://www.lebanondebate.com"
    scraped_data = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(URL, timeout=15, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the main URL %s: %s" % (URL, e))
        return []

    soup = BeautifulSoup(response.content, "lxml")
    
    # Select featured articles
    featured_articles = soup.select("a.featured-article")

    if not featured_articles:
        print("Could not find any featured articles on Lebanon Debate.")
        return []
    
    for article_link in featured_articles:
        article_url = article_link.get("href")
        if not article_url:
            continue
            
        # Extract image URL
        img_tag = article_link.select_one("img.article-image")
        image_url = img_tag.get("src") if img_tag else None
        
        # Extract article details
        details_div = article_link.select_one("div.article-details")
        if not details_div:
            continue
            
        # Extract headline
        headline_h3 = details_div.select_one("h3")
        if not headline_h3:
            continue
            
        headline = headline_h3.get_text(strip=True)
        
        # Extract category (first <p> tag)
        category_p = details_div.select_one("p")
        category = category_p.get_text(strip=True) if category_p else ""
        
        # Extract date
        date_tag = details_div.select_one("date")
        date = date_tag.get_text(strip=True) if date_tag else ""

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url
            
        # Build full image URL if relative
        if image_url and not image_url.startswith('http'):
            image_url = URL + image_url

        article_text = _get_lebanondebate_article_text(article_url)
        
        scraped_data.append({
            "headline": headline,
            "image_url": image_url,
            "article_url": article_url,
            "article_text": article_text
        })
        
        # To avoid being blocked, we only process the first article for now
        if scraped_data:
            break

    if not scraped_data:
        print("Could not scrape any articles from Lebanon Debate.")
        
    return scraped_data

def scrape_lebanonfiles():
    return scrape_site("https://www.lebanonfiles.com", "Lebanon Files")

def scrape_tayyar():
    return scrape_site("https://www.tayyar.org", "Tayyar") 