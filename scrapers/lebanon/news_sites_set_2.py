def scrape_site(url, site_name):
    """A generic template to scrape a news site."""
    print("Scraping %s (placeholder)..." % site_name)
    return []

import requests
from bs4 import BeautifulSoup
import json
import re
from ..scrapfly_helper import get_with_fallback

def _get_alakhbar_article_text(article_url):
    """Helper function to fetch and parse the text from an Al-Akhbar article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = get_with_fallback(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Look for the main content container that Scrapfly returns
        content_container = soup.select_one("main.container")
        if not content_container:
            # Fallback to other possible containers
            content_container = soup.select_one("main")
            if not content_container:
                content_container = soup.select_one("div.gap-4.sm\\:flex")
                if not content_container:
                    return "Article content not found."

        # Look for paragraphs with substantial Arabic content
        paragraphs = content_container.find_all('p')
        article_text_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filter out navigation/menu items and keep only substantial Arabic content
            if (text and len(text) > 20 and 
                any('\u0600' <= char <= '\u06FF' for char in text) and
                not any(skip_word in text for skip_word in ['الأخبار', 'تموز 2025', 'EN']) and
                len(text.split()) > 3):  # More than 3 words
                # Skip very short category labels but keep article content
                if not (len(text) < 50 and any(category in text for category in ['لبنان|سياسة', 'فلسطين', 'سوريا', 'عرب وعالم'])):
                    article_text_parts.append(text)

        article_text = "\n".join(article_text_parts)

        return article_text if article_text else "Article content not found."
        
    except (requests.exceptions.RequestException, AttributeError) as e:
        print("Error processing article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_al_akhbar():
    """
    Scrapes the main featured articles from al-akhbar.com.
    """
    URL = "https://www.al-akhbar.com/"
    BASE_URL = "https://www.al-akhbar.com"
    scraped_data = []

    try:
        response = get_with_fallback(URL, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the main URL %s: %s" % (URL, e))
        return []

    soup = BeautifulSoup(response.content, "lxml")

    # The main articles are located in a grid. We find all of them.
    # The selector targets the container for each article in the main grid.
    articles = soup.select("div.grid.md\\:grid-cols-2 > div.group")

    if not articles:
        print("Could not find any article containers on the main page.")
        return []

    for article_container in articles:
        link_tag = article_container.find("a", href=True)
        headline_tag = article_container.find("h3")
        img_tag = article_container.find("img")

        if not (link_tag and headline_tag and img_tag):
            continue

        headline = headline_tag.get_text(strip=True)
        article_url = link_tag.get("href")
        
        image_url = img_tag.get('src')
        if not image_url:
            srcset = img_tag.get('srcset')
            if srcset:
                # Take the first URL from srcset, which is usually the smallest/default
                image_url = srcset.split(',')[0].strip().split(' ')[0]

        if not (headline and article_url and image_url):
            continue

        if not article_url.startswith('http'):
            article_url = BASE_URL + article_url
        
        # To avoid being blocked, we only fetch the text for the first article
        if len(scraped_data) == 0:
            article_text = _get_alakhbar_article_text(article_url)
        else:
            article_text = "Not fetched to avoid excessive requests."
            
        scraped_data.append({
            "headline": headline,
            "image_url": image_url,
            "article_url": article_url,
            "article_text": article_text
        })

    if not scraped_data:
        print("Could not scrape any articles from Al-Akhbar.")

    return scraped_data

def _get_nidaalwatan_article_text(article_url):
    """Helper function to fetch and parse article text from a nidaalwatan.com article page."""
    try:
        response = get_with_fallback(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.select_one("div.article-content")
        if not content_div:
            return "Article content not found."

        # Remove related articles and other clutter before extracting text
        for element in content_div.select("div.relatedArticles, ul.keywords, div.mpu"):
            element.decompose()
            
        paragraphs = content_div.find_all("p")
        article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_nidaalwatan():
    """
    Scrapes featured articles from nidaalwatan.com.
    """
    URL = "https://www.nidaalwatan.com"
    scraped_data = []

    try:
        response = get_with_fallback(URL, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the main URL %s: %s" % (URL, e))
        return []

    soup = BeautifulSoup(response.content, "lxml")
    
    # Select all featured articles from the carousel
    articles = soup.select("div.featured_articles div.carousel-component > a")

    if not articles:
        print("Could not find any featured articles on Nidaalwatan.")
        return []
    
    for article_link in articles:
        headline_tag = article_link.select_one("div.info > p")
        figure_tag = article_link.find("figure")

        if not (headline_tag and figure_tag):
            continue
            
        headline = headline_tag.get_text(strip=True)
        article_url = article_link.get("href")
        
        # Extract image URL from inline style attribute
        style = figure_tag.get("style", "")
        match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
        image_url = match.group(1) if match else None

        if not (headline and article_url and image_url):
            continue

        if not article_url.startswith('http'):
            article_url = URL + article_url

        article_text = _get_nidaalwatan_article_text(article_url)
        
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
        print("Could not scrape any articles from Nidaalwatan.")
        
    return scraped_data

def _get_aliwaa_article_text(article_url):
    """Helper function to fetch and parse article text from an aliwaa.com.lb article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.select_one("div.content-container")
        if not content_div:
            return "Article content not found."

        # Remove any ads or unwanted elements
        for element in content_div.select("div[id*='gpt'], iframe, .advertisement"):
            element.decompose()
            
        # Extract text from divs (aliwaa uses divs instead of paragraphs)
        content_divs = content_div.find_all("div", recursive=False)
        article_text_parts = []
        
        for div in content_divs:
            text = div.get_text(strip=True)
            if text and len(text) > 10:  # Skip empty or very short divs
                article_text_parts.append(text)
        
        article_text = "\n".join(article_text_parts)
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_aliwaa():
    """
    Scrapes featured articles from aliwaa.com.lb.
    """
    URL = "https://aliwaa.com.lb"
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
    
    # Select all news carousel items
    articles = soup.select("div.news-carousel-item")

    if not articles:
        print("Could not find any news carousel items on Aliwaa.")
        return []
    
    for article_item in articles:
        link_tag = article_item.find("a", href=True)
        if not link_tag:
            continue
            
        # Extract headline from the span.title content
        title_span = link_tag.select_one("span.title > span:last-child")
        if not title_span:
            continue
            
        headline = title_span.get_text(strip=True)
        article_url = link_tag.get("href")
        
        # Extract image URL from img tag, handling lazy loading
        img_tag = link_tag.find("img")
        image_url = None
        if img_tag:
            # Check data-src first (for lazy loading), then src
            image_url = img_tag.get("data-src") or img_tag.get("src")
            
            # Skip placeholder images
            if image_url and "placeholder" in image_url:
                image_url = img_tag.get("data-src")  # Try to get the real URL from data-src
            
            # Build complete URL if it's relative
            if image_url and not image_url.startswith('http'):
                image_url = URL + image_url

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url

        article_text = _get_aliwaa_article_text(article_url)
        
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
        print("Could not scrape any articles from Aliwaa.")
        
    return scraped_data

def scrape_al_binaa():
    #not working
    return scrape_site("https://www.al-binaa.com", "Al-Binaa") 