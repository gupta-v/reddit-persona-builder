import os
import re
from pathlib import Path
from datetime import datetime, timezone
import praw
from dotenv import load_dotenv

SCRAPING_DIR = "data\\scrapings"

# ──────────────── Load credentials ────────────────
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)
# ──────────────── Extract username from URL ────────────────


def extract_username_from_url(url: str) -> str:
    '''
    Extracts the username from a Reddit profile URL.

    Args:
        url (str): The Reddit profile URL to extract the username from.

    Returns:
        str: The username extracted from the URL.
    '''

    match = re.search(r"reddit\.com/user/([^/]+)/?", url)
    username = match.group(1)
    if not match:
        raise ValueError("Invalid Reddit profile URL")
    return username


# ──────────────── Fetch user posts ────────────────


def fetch_user_posts(username: str, max_limit: int = 20):
    '''
    Fetches the posts of a Reddit user.

    Args:
        username (str): The Reddit username of user to fetch the posts of.
        max_limit (int): The maximum number of posts to fetch.

    Returns:
        list: A list of posts.
    '''

    user = reddit.redditor(username)
    posts = list(user.submissions.new(limit=max_limit))
    return posts


# ──────────────── Format posts into readable text ────────────────


def format_posts(username: str, posts: list) -> str:
    '''
    Formats the posts into a readable text.

    Args:
        username (str): The Reddit username of user to fetch the posts of.
        posts (list): A list of posts.

    Returns:
        str: A string of formatted posts.
    '''

    lines = []
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    lines.append(f"Reddit User: {username}")
    lines.append(f"Fetched on: {timestamp}\n")

    if not posts:
        lines.append("No posts found.")
        return "\n".join(lines)

    for i, post in enumerate(posts, 1):
        post_type = (
            "text"
            if post.is_self
            else (
                "image"
                if post.url.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
                else "link"
            )
        )
        lines.append(f"[Post {i}]")
        lines.append(f"Title: {post.title.strip()}")
        lines.append(f"Subreddit: r/{post.subreddit}")
        lines.append(f"Permalink: https://reddit.com{post.permalink}")
        lines.append(f"Type: {post_type}")
        post_time = datetime.fromtimestamp(
            post.created_utc, tz=timezone.utc
        ).isoformat()
        lines.append(f"Posted on: {post_time}")
        lines.append(f"Upvotes: {post.score}")

        if post_type == "text" and post.selftext:
            content = post.selftext.strip()
            lines.append("Content:")
            lines.append(content if len(content) <=
                         800 else content[:800] + "...")
        elif post_type in ("image", "link"):
            lines.append(f"External Link: {post.url}")

        lines.append("─" * 72)

    return "\n".join(lines)


# ──────────────── Save to .txt ────────────────

def save_to_txt(content: str,
                username: str,
                output_dir: str):
    '''
    Saves the formatted data to a .txt file.

    Args:
        content (str): The formatted data to save.
        username (str): The Reddit username of user to fetch the posts of.
        output_dir (str): The directory to save the file to.

    Returns:
        str: The path to the saved file.
    '''

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(output_dir, f"{username}_posts.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✓] Saved data to {filepath}")
    return filepath


# ──────────────── Entry Point ────────────────


def main():
    url = input("Enter Reddit profile URL: ").strip()
    try:
        username = extract_username_from_url(url)
        print(f"[i] Extracted username: {username}")
        posts = fetch_user_posts(username)
        formatted = format_posts(username, posts)
        save_path = os.path.join(SCRAPING_DIR, f"{username}")
        save_to_txt(formatted, username, save_path)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
