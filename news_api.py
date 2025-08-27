import os
import logging
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- NewsAPI Client Initialization ---
# It's crucial to have NEWS_API_KEY in your .env file.
API_KEY = os.getenv("NEWS_API_KEY")

# Gracefully handle the case where the API key is missing.
if not API_KEY:
    logging.warning("NEWS_API_KEY not found in environment variables. Related news feature will be disabled.")
    newsapi = None
else:
    newsapi = NewsApiClient(api_key=API_KEY)


def get_related_news(query: str, max_results: int = 5) -> dict:
    """
    Fetches related news articles from NewsAPI based on a query.

    Args:
        query (str): The search query (typically the news headline).
        max_results (int): The maximum number of articles to return.

    Returns:
        dict: A dictionary containing the status and a list of articles,
              or an error message if the API call fails.
    """
    if not newsapi:
        return {"status": "error", "message": "NewsAPI client is not initialized. Check API key."}

    try:
        # Call the NewsAPI to get relevant articles.
        response = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=max_results
        )
        
        # Process the API response.
        if response.get('status') == 'ok':
            articles = []
            for article in response.get('articles', []):
                articles.append({
                    'title': article.get('title', 'No Title'),
                    'source': article.get('source', {}).get('name', 'Unknown Source'),
                    'url': article.get('url'),
                    'published_at': article.get('publishedAt'),
                    'description': article.get('description')
                })
            return {"status": "ok", "articles": articles}
        else:
            # Handle API-level errors (e.g., invalid key, bad request).
            error_message = response.get('message', 'Unknown error from NewsAPI')
            logging.error(f"NewsAPI error: {error_message}")
            return {"status": "error", "message": error_message}
            
    except Exception as e:
        # Handle network errors or other exceptions during the API call.
        logging.error(f"An exception occurred while fetching related news: {e}", exc_info=True)
        return {"status": "error", "message": f"Failed to fetch related news: {str(e)}"}