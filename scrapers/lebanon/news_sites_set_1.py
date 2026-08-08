import requests
from bs4 import BeautifulSoup
import re

# --- Helper Functions ---

def _get_article_text(article_url):
    """Helper function to fetch and parse the text from an Addiyar article page."""
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.find("div", class_="article-content")
        if not content_div:
            return "Article content not found."
            
        paragraphs = content_div.find_all("p")
        article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        return article_text
        
    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def _get_annahar_article_text(article_url):
    """Helper function to fetch and parse the text from an Annahar article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.find("div", class_="bodyContentMainParent")
        if not content_div:
            return "Article content not found."
            
        paragraphs = content_div.find_all("p")
        article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        return article_text
        
    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def _get_aljoumhouria_article_text(article_url):
    """Helper function to fetch and parse the text from an Al-Joumhouria article page."""
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.find("div", class_="description direction-rtl")
        if not content_div:
            return "Article content not found."
            
        paragraphs = content_div.find_all("p")
        article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        return article_text
        
    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

# --- Scraper Functions ---

def scrape_addiyar():
    """
    Scrapes featured articles from addiyar.com.
    """
    URL = "https://www.addiyar.com/"
    BASE_URL = "https://www.addiyar.com"
    scraped_data = []

    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the main URL %s: %s" % (URL, e))
        return []

    soup = BeautifulSoup(response.content, "lxml")

    featured_articles_div = soup.find("div", class_="featured-articles")
    if not featured_articles_div:
        return []

    articles = featured_articles_div.find_all("article")

    for article in articles:
        header_tag = article.find("h2")
        figure_tag = article.find("figure")
        link_tag = article.find("a")

        if not header_tag or not figure_tag or not link_tag or not link_tag.has_attr("href"):
            continue

        headline = header_tag.get_text(separator=" ", strip=True)
        article_url = BASE_URL + link_tag["href"]

        style_attr = figure_tag.get("style", "")
        match = re.search(r"url\('([^']+)'\)", style_attr)
        image_url = match.group(1) if match else ""

        if headline and image_url and article_url:
            article_text = _get_article_text(article_url)
            scraped_data.append({
                "headline": headline,
                "image_url": image_url,
                "article_url": article_url,
                "article_text": article_text
            })

    return scraped_data

def scrape_annahar():
    """
    Scrapes featured articles from an-nahar.com.
    """
    URL = "https://www.annahar.com/"
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

    featured_articles = soup.select("div.listingItemDIV.featured")

    for article in featured_articles:
        title_div = article.find("div", class_="listingTitle")
        image_div = article.find("div", class_="listingImage")

        if not title_div or not image_div:
            continue
        
        link_tag = title_div.find("a")
        img_tag = image_div.find("img")

        if not link_tag or not img_tag or not link_tag.has_attr("href"):
            continue

        headline = link_tag.get_text(strip=True)
        article_url = link_tag["href"]
        image_url = img_tag.get("data-src", "")

        if headline and image_url and article_url:
            article_text = _get_annahar_article_text(article_url)
            scraped_data.append({
                "headline": headline,
                "image_url": image_url,
                "article_url": article_url,
                "article_text": article_text
            })

    return scraped_data

def scrape_aljoumhouria():
    """
    Scrapes the main featured article from aljoumhouria.com.
    """
    URL = "https://www.aljoumhouria.com/ar"
    BASE_URL = "https://www.aljoumhouria.com"
    scraped_data = []

    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching the main URL %s: %s" % (URL, e))
        return []

    soup = BeautifulSoup(response.content, "lxml")

    big_news_div = soup.find("div", class_="big-block-news")
    if not big_news_div:
        return []

    link_tag = big_news_div.find("a")
    if not link_tag or not link_tag.has_attr("href"):
        return []

    article_url = link_tag["href"]
    # Ensure the URL is absolute
    if not article_url.startswith('http'):
        article_url = BASE_URL + article_url


    img_tag = link_tag.find("img", class_="big-news-img")
    headline_div = link_tag.find("div", class_="description")

    if not img_tag or not headline_div:
        return []
    
    image_url = img_tag.get("src", "")
    headline = headline_div.get_text(strip=True)

    if headline and image_url and article_url:
        article_text = _get_aljoumhouria_article_text(article_url)
        scraped_data.append({
            "headline": headline,
            "image_url": image_url,
            "article_url": article_url,
            "article_text": article_text
        })

    return scraped_data 