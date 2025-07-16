import os
import sys
from pathlib import Path
from langchain_core.tools import Tool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.reddit_post_scraper import (
    extract_username_from_url,
    fetch_user_posts,
    format_posts,
)

SCRAPING_DIR = "data\\scrapings"


def scrape_user_posts(url: str) -> dict:
    """
    Scrapes Reddit posts (submissions) for a given profile URL.

    Args:
        url (str): The URL of the Reddit profile to scrape posts from.

    Returns:
        dict: A dictionary containing the username, posts, and source.
    """
    username = extract_username_from_url(url)
    save_path = os.path.join(SCRAPING_DIR, f"{username}\\{username}_posts.txt")
    
    Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)

    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            return {
                "username": username,
                "posts": f.read(),
                "source": f"cached from {save_path}",
            }

    posts = fetch_user_posts(username)
    formatted = format_posts(username, posts)

    Path(SCRAPING_DIR).mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(formatted)

    print(f"\n[✓] Scraped posts data saved to {save_path}")

    return {
        "username": username,
        "posts": formatted,
        "source": "scraped",
    }


# ──────────────── LangChain Tool Definition ────────────────

scrape_posts_tool = Tool(
    name="scrape_posts",
    func=scrape_user_posts,
    description=(
        "Scrapes Reddit posts (submissions) for a given profile URL. "
        "Use when you need a user's original Reddit posts. "
        "Input must be a full profile URL. "
        "Example: https://www.reddit.com/user/example_user/"
    ),
)


def main():
    url = "https://www.reddit.com/user/ExtensionClimate2045/"
    result = scrape_posts_tool.invoke(url)
    print(result)


if __name__ == "__main__":
    main()
