"""Module for scraping Reddit user data."""

import os
import sys
from typing import Dict, Any

# Add parent directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.scrape_comments_tool import scrape_user_comments  # noqa: E402
from tools.scrape_posts_tool import scrape_user_posts  # noqa: E402


def run_scraping_agent(url: str) -> Dict[str, Any]:
    """
    Orchestrate scraping of Reddit comments and posts for a given profile URL.

    Args:
        url: Reddit profile URL

    Returns:
        dict: {
            "username": str,
            "comments": str,
            "posts": str,
            "sources": {
                "comments": "scraped"|"cached",
                "posts": "scraped"|"cached"
            }
        }
    """
    comment_data = scrape_user_comments(url)
    post_data = scrape_user_posts(url)

    return {
        "username": comment_data["username"],
        "comments": comment_data["comments"],
        "posts": post_data["posts"],
        "sources": {
            "comments": comment_data["source"],
            "posts": post_data["source"]
        }
    }


# Optional test runner
if __name__ == "__main__":
    sample_url = "https://www.reddit.com/user/r4kim/"
    result = run_scraping_agent(sample_url)
    print(f"\n🧠 Scraped user: {result['username']}")
    print(f"\n📄 Comments Source: {result['sources']['comments']}")
    print(result["comments"][:500])  # Preview
    print(f"\n📄 Posts Source: {result['sources']['posts']}")
    print(result["posts"][:500])  # Preview
