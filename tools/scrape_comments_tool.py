import os
import sys
from pathlib import Path
from langchain_core.tools import Tool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.reddit_comment_scraper import (
    extract_username_from_url,
    fetch_user_comments,
    group_comments_by_post,
    format_grouped_data,
)


SCRAPING_DIR = "data\\scrapings"


def scrape_user_comments(url: str) -> dict:
    """
    Scrapes Reddit comments for a given profile URL.

    Args:
        url (str): The URL of the Reddit profile to scrape comments from.

    Returns:
        dict: A dictionary containing the username, comments, and source.
    """

    username = extract_username_from_url(url)
    save_path = os.path.join(SCRAPING_DIR, f"{username}\\{username}_comments.txt")

    Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)

    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            return {"username": username,
                    "comments": f.read(), 
                    "source": f"cached from {save_path}"}

    comments = fetch_user_comments(username)
    grouped = group_comments_by_post(comments)
    formatted = format_grouped_data(username, grouped)

    Path(SCRAPING_DIR).mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(formatted)

    print(f"\n[✓] Scraped comments data saved to {save_path}")
    return {"username": username, "comments": formatted, "source": "scraped"}


# ──────────────── LangChain Tool Definition ────────────────

scrape_comments_tool = Tool(
    name="scrape_comments",
    func=scrape_user_comments,
    description=(
        "Scrapes Reddit comments for a given profile URL. "
        "Use when you need a user's Reddit comment history. "
        "Input must be a full profile URL."
        "For Example: https://www.reddit.com/user/example_user/"
    ),
)


def main():
    print(
        scrape_comments_tool.invoke(
            "https://www.reddit.com/user/ExtensionClimate2045/")
    )


if __name__ == "__main__":
    main()
