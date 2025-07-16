"""Module for cleaning and structuring scraped Reddit data."""

import re
import json
from pathlib import Path


def parse_posts(text):
    """
    Parse the posts from the text.

    Args:
        text: The text to parse.

    Returns:
        A list of posts.
    """
    posts = []
    post_blocks = re.split(r"\[Post \d+\]", text)
    for block in post_blocks[1:]:
        post = {}
        # Title
        m = re.search(r"Title: (.*)", block)
        if m:
            post["title"] = m.group(1).strip()
        # Subreddit
        m = re.search(r"Subreddit: r/(.*)", block)
        if m:
            post["subreddit"] = m.group(1).strip()
        # Permalink
        m = re.search(r"Permalink: (.*)", block)
        if m:
            post["permalink"] = m.group(1).strip()
        # Type
        m = re.search(r"Type: (.*)", block)
        if m:
            post["type"] = m.group(1).strip()
        # Posted on
        m = re.search(r"Posted on: (.*)", block)
        if m:
            post["posted_on"] = m.group(1).strip()
        # Upvotes
        m = re.search(r"Upvotes: (\d+)", block)
        if m:
            post["upvotes"] = int(m.group(1))
        # Content (for text posts)
        m = re.search(
            r"Content:\n([\s\S]*?)(?:\n\u2500|\nExternal Link:|$)",
            block
        )
        if m:
            post["content"] = m.group(1).strip()
        # External Link (for image/link posts)
        m = re.search(r"External Link: (.*)", block)
        if m:
            post["external_link"] = m.group(1).strip()
        posts.append(post)
    return posts


def parse_comments(text):
    """
    Parse the comments from the text.

    Args:
        text: The text to parse.

    Returns:
        A list of comments.
    """
    comments = []
    # Split by Post N:
    post_blocks = re.split(r"Post \d+:", text)
    for block in post_blocks[1:]:
        # Get post context
        m = re.search(r'Title: "(.*)"', block)
        if m:
            post_title = m.group(1).strip()
        else:
            post_title = None
        m = re.search(r'Subreddit: r/(.*)', block)
        if m:
            post_subreddit = m.group(1).strip()
        else:
            post_subreddit = None
        m = re.search(r'Permalink: (.*)', block)
        if m:
            post_permalink = m.group(1).strip()
        else:
            post_permalink = None
        # Find all comments/replies in this block
        comment_blocks = re.split(r'→ ', block)
        for cblock in comment_blocks[1:]:
            comment = {
                "post_title": post_title,
                "post_subreddit": post_subreddit,
                "post_permalink": post_permalink
            }
            # Commented or replied?
            if "replied to u/" in cblock:
                m = re.search(r'replied to u/(.*?) \((.*?)\)', cblock)
                if m:
                    comment["context_author"] = m.group(1).strip()
                    comment["timestamp"] = m.group(2).strip()
                m = re.search(
                    r'Quoted comment: "([\s\S]*?)"\nReply: ([\s\S]*?)(?:\n|$)',
                    cblock
                )
                if m:
                    comment["context"] = m.group(1).strip()
                    comment["text"] = m.group(2).strip()
                else:
                    # fallback: just get reply text
                    m = re.search(r'Reply: ([\s\S]*?)(?:\n|$)', cblock)
                    if m:
                        comment["text"] = m.group(1).strip()
            else:
                m = re.search(r'commented on post \((.*?)\)', cblock)
                if m:
                    comment["timestamp"] = m.group(1).strip()
                # The next line is the comment text
                m = re.search(
                    r'commented on post \(.*?\)\n([\s\S]*?)(?:\n|$)',
                    cblock
                )
                if m:
                    comment["text"] = m.group(1).strip()
            comments.append(comment)
    return comments


def save_file(username: str, data: str):
    """
    Save the cleaned data in a folder.

    Args:
        username: Username of the Reddit User.
        data: Cleaned Data

    Returns:
        None
    """
    cleaned_dir = Path("data/cleaned")
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    output_file = cleaned_dir / f"{username}_cleaned.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Cleaned data saved to {output_file}")


def run_cleaning_agent(scraped_data):
    """
    Clean and structure the scraped data into a JSON-serializable dict.

    Args:
        scraped_data (dict): Output from run_scraping_agent, containing
            'username', 'comments', and 'posts' as text.

    Returns:
        dict: {
            'username': str,
            'posts': list,
            'comments': list
        }
    """
    username = scraped_data.get('username', '')
    posts = parse_posts(scraped_data.get('posts', ''))
    comments = parse_comments(scraped_data.get('comments', ''))
    data = {
        'username': username,
        'user_url': f"https://www.reddit.com/user/{username}",
        'posts': posts,
        'comments': comments
    }
    save_file(username, data)
    return data
