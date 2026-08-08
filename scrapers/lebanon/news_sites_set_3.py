import requests
from bs4 import BeautifulSoup
import re
from ..scrapfly_helper import get_with_fallback

def scrape_site(url, site_name):
    """A generic template to scrape a news site."""
    print("Scraping %s (placeholder)..." % site_name)
    return []

def _get_elsharkonline_article_text(article_url):
    """Helper function to fetch and parse article text from an elsharkonline.com article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = get_with_fallback(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.select_one("div.entry-content.clearfix.single-post-content")
        if not content_div:
            return "Article content not found."

        # Remove any ads, share buttons or unwanted elements
        for element in content_div.select("div.post-share, div[id*='gpt'], iframe, .advertisement"):
            element.decompose()
            
        # Extract text from paragraphs
        paragraphs = content_div.find_all("p")
        article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_elsharkonline():
    """
    Scrapes featured articles from elsharkonline.com.
    """
    URL = "https://www.elsharkonline.com"
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
    
    # Select all articles from the main column
    articles = soup.select("div.column-1 > article")

    if not articles:
        print("Could not find any articles on Elsharkonline.")
        return []
    
    for article in articles:
        # Extract headline and URL
        title_link = article.select_one("h2.title > a")
        if not title_link:
            continue
            
        headline = title_link.get_text(strip=True)
        article_url = title_link.get("href")
        
        # Extract image URL from featured div background-image style
        featured_div = article.select_one("div.featured a")
        image_url = None
        if featured_div:
            style = featured_div.get("style", "")
            # Extract URL from background-image: url("...")
            match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
            image_url = match.group(1) if match else None

        # Extract summary text
        summary_div = article.select_one("div.post-summary")
        summary = summary_div.get_text(strip=True) if summary_div else ""

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url
            
        # Build full image URL if relative
        if image_url and not image_url.startswith('http'):
            image_url = URL + image_url

        article_text = _get_elsharkonline_article_text(article_url)
        
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
        print("Could not scrape any articles from Elsharkonline.")
        
    return scraped_data

def _get_mtv_article_text(article_url):
    """Helper function to fetch and parse article text from an mtv.com.lb article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.select_one("div.articles-report")
        if not content_div:
            return "Article content not found."

        # Remove any ads and unwanted elements
        for element in content_div.select("div[id*='gpt'], iframe, .article-ad, div[id*='google_ads']"):
            element.decompose()
            
        # Extract text from paragraphs and line breaks
        # MTV uses both <p> tags and <br> tags for content formatting
        text_content = content_div.get_text(separator="\n", strip=True)
        
        # Clean up extra whitespace and empty lines
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        article_text = "\n".join(lines)
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_mtv():
    """
    Scrapes quick news from mtv.com.lb.
    """
    URL = "https://www.mtv.com.lb"
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
    
    # Select all news items from the swiper
    news_items = soup.select("div.swiper-wrapper.news-wrapper > a.swiper-slide.news-item")

    if not news_items:
        print("Could not find any news items on MTV Lebanon.")
        return []
    
    for news_item in news_items:
        # Extract headline and URL
        news_title_div = news_item.select_one("div.news-title")
        if not news_title_div:
            continue
            
        # Extract time
        time_span = news_title_div.select_one("span.news-time")
        time = time_span.get_text(strip=True) if time_span else ""
        
        # Remove time span to get clean headline
        if time_span:
            time_span.decompose()
            
        headline = news_title_div.get_text(strip=True)
        article_url = news_item.get("href")

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url

        # Get article details including image and full text
        article_details = _get_mtv_article_details(article_url)
        
        scraped_data.append({
            "headline": headline,
            "image_url": article_details.get("image_url"),
            "article_url": article_url,
            "article_text": article_details.get("article_text", "")
        })
        
        # To avoid being blocked, we only process the first article for now
        if scraped_data:
            break

    if not scraped_data:
        print("Could not scrape any news items from MTV Lebanon.")
        
    return scraped_data

def _get_mtv_article_details(article_url):
    """Helper function to fetch article details including image and text from MTV article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    details = {"image_url": None, "article_text": ""}
    
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        # Extract image URL
        img_tag = soup.select_one("div.articles-header-image img")
        if img_tag:
            details["image_url"] = img_tag.get("src")
        
        # Extract article text
        content_div = soup.select_one("div.articles-report")
        if content_div:
            # Remove any ads and unwanted elements
            for element in content_div.select("div[id*='gpt'], iframe, .article-ad, div[id*='google_ads']"):
                element.decompose()
                
            # Extract text from paragraphs and line breaks
            text_content = content_div.get_text(separator="\n", strip=True)
            
            # Clean up extra whitespace and empty lines
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            details["article_text"] = "\n".join(lines)
        
    except requests.exceptions.RequestException as e:
        print("Error fetching article details %s: %s" % (article_url, e))
        details["article_text"] = "Failed to retrieve article text."
    
    return details

def _get_aljadeed_article_text(article_url):
    """Helper function to fetch and parse article text from an aljadeed.tv article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.select_one("div.LongDesc.text-title-9")
        if not content_div:
            return "Article content not found."

        # Remove any unwanted injection elements
        for element in content_div.select("controlinjection"):
            element.decompose()
            
        # Extract text while preserving some formatting
        # Al-Jadeed uses custom formatting with entity links
        text_content = content_div.get_text(separator=" ", strip=True)
        
        # Clean up extra whitespace
        article_text = re.sub(r'\s+', ' ', text_content).strip()
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_aljadeed():
    """
    Scrapes featured articles from aljadeed.tv.
    """
    URL = "https://www.aljadeed.tv"
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
    
    # Select slider images and info containers
    image_slides = soup.select("div.swiper-wrapper > div.swiper-slide.pres-swiper-slide")
    info_slides = soup.select("div.swiper-info-container div.swiper-wrapper > div.swiper-slide")

    if not image_slides or not info_slides:
        print("Could not find any articles on Al-Jadeed TV.")
        return []
    
    # Process slides (match images with info)
    for i, (image_slide, info_slide) in enumerate(zip(image_slides, info_slides)):
        # Extract image and URL from image slide
        link_tag = image_slide.select_one("a[href]")
        img_tag = image_slide.select_one("img.slider-presentation-img")
        
        if not (link_tag and img_tag):
            continue
            
        article_url = link_tag.get("href")
        image_url = img_tag.get("src")
        
        # Extract headline from info slide
        title_link = info_slide.select_one("div.slider-presentation-title h2 a span")
        if not title_link:
            continue
            
        headline = title_link.get_text(strip=True)
        
        # Extract category
        category_link = info_slide.select_one("div.card-category-inner .card-title h2 a")
        category = category_link.get_text(strip=True) if category_link else ""

        if not (headline and article_url and image_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url
            
        # Build full image URL if relative
        if not image_url.startswith('http'):
            image_url = URL + image_url

        article_text = _get_aljadeed_article_text(article_url)
        
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
        print("Could not scrape any articles from Al-Jadeed TV.")
        
    return scraped_data

def _get_sawtbeirut_article_text(article_url):
    """Helper function to fetch and parse article text from a sawtbeirut.com article page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = get_with_fallback(article_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        content_div = soup.select_one("div.single-description")
        if not content_div:
            return "Article content not found."

        # Remove any ads, share buttons or unwanted elements
        for element in content_div.select("div.heateor_sss_sharing_container, div[class*='code-block'], script, .ai-viewports"):
            element.decompose()
            
        # Extract text from paragraphs
        paragraphs = content_div.find_all("p")
        article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        return article_text if article_text else "Article text not found."

    except requests.exceptions.RequestException as e:
        print("Error fetching article %s: %s" % (article_url, e))
        return "Failed to retrieve article text."

def scrape_sawtbeirut():
    """
    Scrapes featured articles from sawtbeirut.com.
    """
    URL = "https://www.sawtbeirut.com"
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
    
    # Select the headlines section
    headlines_section = soup.select_one("section#headlines")
    if not headlines_section:
        print("Could not find headlines section on Sawt Beirut.")
        return []
    
    # Find both primary and secondary cards
    all_cards = headlines_section.select("div.card.headlines-primary, div.card.card-secondary")

    if not all_cards:
        print("Could not find any article cards on Sawt Beirut.")
        return []
    
    for card in all_cards:
        # Find the parent link element
        link_element = card.find_parent("a")
        if not link_element:
            continue
            
        article_url = link_element.get("href")
        if not article_url:
            continue
            
        # Extract headline
        title_element = card.select_one("h5.card-title")
        if not title_element:
            continue
            
        headline = title_element.get_text(strip=True)
        
        # Extract image URL
        img_tag = card.select_one("img")
        image_url = img_tag.get("src") if img_tag else None
        
        # Extract category
        category_span = card.select_one("span.cat")
        category = category_span.get_text(strip=True) if category_span else ""

        if not (headline and article_url):
            continue

        # Build full URL if relative
        if not article_url.startswith('http'):
            article_url = URL + article_url
            
        # Build full image URL if relative
        if image_url and not image_url.startswith('http'):
            image_url = URL + image_url

        article_text = _get_sawtbeirut_article_text(article_url)
        
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
        print("Could not scrape any articles from Sawt Beirut.")
        
    return scraped_data 