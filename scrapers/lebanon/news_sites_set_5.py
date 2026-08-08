import requests
from bs4 import BeautifulSoup
import re
from ..scrapfly_helper import get_with_fallback

def scrape_site(url, site_name):
    """A generic template to scrape a news site."""
    print("Scraping %s (placeholder)..." % site_name)
    return []

def _get_lebanese_forces_article_text(article_url):
    """Helper function to fetch and parse article text from a lebanese-forces.com article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = get_with_fallback(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        # Look for article content in the main article body
        content_div = soup.select_one("div.entry-content")
        if not content_div:
            content_div = soup.select_one("article.mainpost div.entry-content")
        if not content_div:
            return "Article content not found."

        # Remove any ads, scripts, and unwanted elements
        for element in content_div.select("div[id*='gpt'], div[id*='div-gpt'], script, .advertisement, .addthis_sharing_toolbox"):
            element.decompose()
            
        # Extract text from paragraphs
        paragraphs = content_div.find_all("p")
        if paragraphs:
            article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            # Fallback to general text extraction
            article_text = content_div.get_text(separator="\n", strip=True)
        
        # Clean up extra whitespace and empty lines
        lines = [line.strip() for line in article_text.split('\n') if line.strip()]
        article_text = "\n".join(lines)
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_lebanese_forces():
    """
    Scrapes featured articles from lebanese-forces.com.
    """
    URL = "https://www.lebanese-forces.com"
    scraped_data = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = get_with_fallback(URL, timeout=15, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the main URL %s: %s" % (URL, e))
        return []

    soup = BeautifulSoup(response.content, "lxml")
    
    # Look for carousel items directly (they exist before JS loads owl-item wrappers)
    carousel_items = soup.select("div.item")
    
    if not carousel_items:
        print("Could not find any articles on Lebanese Forces.")
        return []
    
    for item in carousel_items:
        # Find the article link
        article_link = item.select_one("a")
        if not article_link:
            continue
            
        article_url = article_link.get("href")
        if not article_url:
            continue
            
        # Extract image URL
        img_tag = item.select_one("div.slide-img img")
        image_url = img_tag.get("src") if img_tag else None
        
        # Extract headline
        headline_h1 = item.select_one("div.post-content h1")
        if not headline_h1:
            continue
            
        headline = headline_h1.get_text(strip=True)

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url
            
        # Build full image URL if relative
        if image_url and not image_url.startswith('http'):
            image_url = URL + image_url

        article_text = _get_lebanese_forces_article_text(article_url)
        
        scraped_data.append({
            "headline": headline,
            "image_url": image_url,
            "article_url": article_url,
            "article_text": article_text
        })
        
        # Process up to 3 articles
        if len(scraped_data) >= 3:
            break

    if not scraped_data:
        print("Could not scrape any articles from Lebanese Forces.")
        
    return scraped_data

def scrape_almarkazia():
    return scrape_site("https://www.almarkazia.com", "Almarkazia")

def _get_lbcgroup_article_text(article_url):
    """Helper function to fetch and parse article text from a lbcgroup.tv article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        # Look for article content in the main article body
        content_div = soup.select_one("div.LongDesc")
        if not content_div:
            content_div = soup.select_one("div.article_details_body")
        
        if not content_div:
            return "Article content not found."

        # Remove any ads, scripts, and unwanted elements
        for element in content_div.select("bannerinjection, controlinjection, script, style, div[id*='gpt'], iframe, .article-ad"):
            element.decompose()
            
        # Extract text from paragraphs and divs
        text_content = content_div.get_text(separator="\n", strip=True)
        
        # Clean up extra whitespace and empty lines
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        article_text = "\n".join(lines)
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_lbcgroup():
    """
    Scrapes featured articles from lbcgroup.tv.
    """
    URL = "https://www.lbcgroup.tv"
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
    
    # First, try to get the main highlighted story
    highlighted_story = soup.select_one("div.highlighted-history-container")
    if highlighted_story:
        # Extract main article details
        main_link = highlighted_story.select_one("a.u-imgLink")
        main_title = highlighted_story.select_one("div.card-module-title h2 a")
        main_image = highlighted_story.select_one("img.highlighted-history-image")
        main_category = highlighted_story.select_one("div.card-module-category-container a")
        main_time = highlighted_story.select_one("div.card-module-date-container div.u-direction-RTL")
        
        if main_link and main_title:
            article_url = main_link.get("href")
            headline = main_title.get_text(strip=True)
            image_url = main_image.get("src") if main_image else None
            category = main_category.get_text(strip=True) if main_category else ""
            time = main_time.get_text(strip=True) if main_time else ""
            
            # Build full URL if relative
            if article_url and not article_url.startswith('http'):
                article_url = URL + article_url
                
            # Build full image URL if relative
            if image_url and not image_url.startswith('http'):
                image_url = URL + image_url

            if headline and article_url:
                article_text = _get_lbcgroup_article_text(article_url)
                
                scraped_data.append({
                    "headline": headline,
                    "image_url": image_url,
                    "article_url": article_url,
                    "article_text": article_text
                })
    
    # Then get latest news articles
    latest_news_articles = soup.select("div.latestnews_article")
    
    for article_item in latest_news_articles[:4]:  # Limit to first 4 articles
        # Skip if we already have articles from highlighted story
        if len(scraped_data) >= 1:
            break
            
        link_tag = article_item.select_one("a.u-imgLink")
        title_tag = article_item.select_one("div.card-module-title h2 a")
        category_tag = article_item.select_one("div.card-module-category-container a")
        time_tag = article_item.select_one("div.card-module-date-container div.u-direction-RTL")
        
        if not (link_tag and title_tag):
            continue
            
        article_url = link_tag.get("href")
        headline = title_tag.get_text(strip=True)
        category = category_tag.get_text(strip=True) if category_tag else ""
        time = time_tag.get_text(strip=True) if time_tag else ""

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url

        article_text = _get_lbcgroup_article_text(article_url)
        
        scraped_data.append({
            "headline": headline,
            "image_url": None,  # Latest news articles don't have images in the list
            "article_url": article_url,
            "article_text": article_text
        })
        
        # To avoid being blocked, we only process the first article for now
        if scraped_data:
            break

    if not scraped_data:
        print("Could not scrape any articles from LBC Group.")
        
    return scraped_data 