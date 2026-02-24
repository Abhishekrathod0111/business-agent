from scraper import search_company, scrape_website
import logging

logger = logging.getLogger(__name__)


def research(company):
    try:
        urls = search_company(company)
    except Exception:
        logger.exception("search_company failed for %s", company)
        return ""

    if not urls:
        logger.warning("No search results found for %s", company)
        return ""

    combined_content = ""

    for url in urls[:3]:
        try:
            content = scrape_website(url)
            if content:
                combined_content += content
        except Exception:
            logger.exception("Failed scraping URL for %s: %s", company, url)

    return combined_content