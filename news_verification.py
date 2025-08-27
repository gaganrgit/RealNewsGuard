import requests
from bs4 import BeautifulSoup
import logging

# --- Web Scraper Configuration ---
# Using a common User-Agent helps avoid being blocked by websites.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
TIMEOUT = 10 # seconds

def _check_fact_check_site(url_template: str, query: str, parser_func) -> dict:
    """
    A generic helper function to query a fact-checking site and parse the results.
    NOTE: Web scraping is fragile and can break if a website's HTML structure changes.
    """
    search_query = "+".join(query.split())
    url = url_template.format(search_query=search_query)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        return parser_func(soup)

    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., connection timeout, DNS error).
        logging.error(f"Error accessing {url}: {e}")
        return {"found": False, "error": f"Network error: {str(e)}"}
    except Exception as e:
        # Handle errors during the HTML parsing phase.
        logging.error(f"Error parsing results from {url}: {e}", exc_info=True)
        return {"found": False, "error": f"Parsing failed: {str(e)}"}

def _parse_snopes(soup: BeautifulSoup) -> dict:
    """Parser specifically for Snopes search results page."""
    articles = soup.find_all('article', class_='list-group-item')
    if not articles:
        return {"found": False, "message": "No results on Snopes."}
    
    results = []
    for article in articles[:3]: # Limit to top 3 results for brevity.
        title_elem = article.find('h2', class_='title')
        rating_elem = article.find('span', class_='rating-name')
        link_elem = article.find('a', href=True)
        if title_elem and link_elem:
            results.append({
                "title": title_elem.text.strip(),
                "url": link_elem['href'],
                "rating": rating_elem.text.strip() if rating_elem else "Unknown"
            })
    return {"found": True, "results": results}

def _parse_politifact(soup: BeautifulSoup) -> dict:
    """Parser specifically for PolitiFact search results page."""
    articles = soup.find_all('li', class_='o-listicle__item')
    if not articles:
        return {"found": False, "message": "No results on PolitiFact."}

    results = []
    for article in articles[:3]:
        title_elem = article.find('div', class_='m-statement__quote')
        link_elem = title_elem.find('a') if title_elem else None
        rating_img_elem = article.find('img', class_='c-image__original')
        if title_elem and link_elem and rating_img_elem:
            results.append({
                "title": title_elem.text.strip(),
                "url": f"https://www.politifact.com{link_elem['href']}",
                "rating": rating_img_elem['alt'].strip()
            })
    return {"found": True, "results": results}


def verify_news(headline: str) -> dict:
    """
    Verifies a news headline by checking against major fact-checking websites.
    """
    logging.info(f"Verifying headline: '{headline[:50]}...'")
    results = {
        "snopes": _check_fact_check_site("https://www.snopes.com/?s={search_query}", headline, _parse_snopes),
        "politifact": _check_fact_check_site("https://www.politifact.com/search/?q={search_query}", headline, _parse_politifact),
    }
    return results