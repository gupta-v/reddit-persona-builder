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
    user_agent=os.getenv("REDDIT_USER_AGENT")
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

    match = re.search(r'reddit\.com/user/([^/]+)/?', url)
    if not match:
        raise ValueError("Invalid Reddit profile URL")
    return match.group(1)

# ──────────────── Fetch user comments ────────────────


def fetch_user_comments(username: str, limit: int = 30):
    '''
    Fetches the comments of a Reddit user.

    Args:
        username (str): The Reddit username to fetch the comments of.
        limit (int): The maximum number of comments to fetch.

    Returns:
        list: A list of comments.
    '''

    user = reddit.redditor(username)
    return list(user.comments.new(limit=limit))

# ──────────────── Group comments by post ────────────────


def group_comments_by_post(comments: list):
    '''
    Groups comments by post.

    Args:
        comments (list): A list of comments.

    Returns:
        dict: A dictionary of comments grouped by post.
    '''

    grouped = {}
    for comment in comments:
        post = comment.submission
        post_id = post.id
        if post_id not in grouped:
            grouped[post_id] = {
                "title": post.title,
                "subreddit": str(post.subreddit),
                "permalink": f"https://reddit.com{post.permalink}",
                "body": post.selftext if post.is_self else "",
                "comments": []
            }

        is_reply = not comment.is_root
        parent_text = None
        parent_author = "unknown"

        if is_reply:
            try:
                parent = comment.parent()
                if isinstance(parent, praw.models.Comment):
                    parent_text = parent.body.strip()
                    parent_author = (
                        str(parent.author) if parent.author else "deleted"
                    )
            except Exception:
                parent_text = "[Could not fetch parent comment]"
                parent_author = "unknown"

        grouped[post_id]["comments"].append({
            "score": comment.score,
            "text": comment.body.strip(),
            "is_reply": is_reply,
            "context": parent_text,
            "context_author": parent_author if is_reply else None,
            "timestamp": datetime.fromtimestamp(
                comment.created_utc, tz=timezone.utc
            ).isoformat()
        })
    return grouped

# ──────────────── Format grouped data ────────────────


def format_grouped_data(username: str, grouped_data: dict) -> str:
    '''
    Formats grouped data into a string.

    Args:
        username (str): The username of the Reddit user.
        grouped_data (dict): A dictionary of comments grouped by post.

    Returns:
        str: A string of formatted data.
    '''

    lines = []
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    lines.append(f"Reddit User: {username}")
    lines.append(f"Fetched on: {timestamp}\n")

    for i, (post_id, post_data) in enumerate(grouped_data.items(), 1):
        lines.append(f"Post {i}:")
        lines.append(f"Title: \"{post_data['title']}\"")
        lines.append(f"Subreddit: r/{post_data['subreddit']}")
        lines.append(f"Permalink: {post_data['permalink']}")
        if post_data["body"]:
            body = post_data["body"]
            lines.append("Body:")
            lines.append(
                body if len(body) <= 600 else body[:600] + "..."
            )
        lines.append("")

        for j, comment in enumerate(post_data["comments"], 1):
            if comment["is_reply"]:
                lines.append(
                    f"→ {username} replied to u/{comment['context_author']} "
                    f"({comment['timestamp']})"
                )
                lines.append(
                    f"Quoted comment: \"{comment['context'].strip()}\""
                )
                lines.append("Reply: " + comment["text"])
            else:
                lines.append(
                    f"→ {username} commented on post "
                    f"({comment['timestamp']})"
                )
                lines.append(comment["text"])
            lines.append("")

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
        username (str): The username of the Reddit user.
        output_dir (str): The directory to save the file to.

    Returns:
        str: The path to the saved file.
    '''

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(output_dir, f"{username}_comments.txt")
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
        comments = fetch_user_comments(username)
        grouped = group_comments_by_post(comments)
        formatted = format_grouped_data(username, grouped)
        save_path = os.path.join(SCRAPING_DIR, f"{username}")
        save_to_txt(formatted, username, save_path)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
