import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
import logging
import time

logger = logging.getLogger(__name__)


def search_company(company_name):
    
    results = []

    with DDGS() as ddgs:
        query = f"{company_name} company business model competitors"
        
        try:
            for r in ddgs.text(query, max_results=5):
                results.append(r.get('href'))
        except Exception as e:
            logger.exception("DDGS search failed for '%s'", company_name)
            return []

    return results


def scrape_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BusinessAgent/1.0)"
    }

    for attempt in range(1, 4):
        try:
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            paragraphs = soup.find_all("p")

            content = " ".join([p.get_text() for p in paragraphs])

            return content[:3000]  # limit size

        except Exception as e:
            logger.warning("Attempt %d: Failed to scrape %s — %s", attempt, url, str(e))
            time.sleep(attempt)  # simple backoff

    logger.exception("Failed to scrape website after retries: %s", url)
    return ""