"""Module for generating draft personas from Reddit user data."""

from typing import Dict, List
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

llm_models = [
    ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0.7),
    ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7),
    ChatGroq(model="llama3-70b-8192", temperature=0.7),
    ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.7
    ),
    ChatGroq(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.7
    ),
]


def split_text(
    text: str,
    chunk_size: int = 2000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    Split the text into chunks of a given size and overlap.

    Uses the RecursiveCharacterTextSplitter from langchain_text_splitters.

    Args:
        text: The text to split.
        chunk_size: The size of each chunk.
        chunk_overlap: The overlap between chunks.

    Returns:
        A list of chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)


def build_persona_prompt(
    username: str,
    user_url: str,
    comments_chunk: str,
    posts_chunk: str,
    epoch: int
) -> str:
    """
    Build the prompt for the persona agent.

    Args:
        username: The username of the user.
        user_url: The URL of the user's profile.
        comments_chunk: The comments chunk.
        posts_chunk: The posts chunk.
        epoch: The epoch number.

    Returns:
        A string of the prompt.
    """
    return f"""
[Epoch {epoch}]

You are a professional persona analysis agent.

Analyze the following Reddit user's data to extract key traits.
For each trait, cite the source in format:
[Source: r/subreddit - Post/Comment description]

## Username:
{username}

## User URL:
{user_url}

## Posts (chunked):
{posts_chunk}

## Comments (chunked):
{comments_chunk}

## Task:
Extract key inferences about:
- Age indicators
- Tone and communication style
- Topics of interest
- Language patterns
- Opinions and viewpoints
- Community participation
- Behavioral patterns
- Political/social views
- Humor/sarcasm usage
- Technical knowledge

Respond with bullet points - focus on traits from this epoch.
Each bullet point MUST include a specific citation.
"""


def run_drafting_agent(cleaned_data: Dict) -> Dict:
    """
    Run the drafting agent.

    Args:
        cleaned_data: The cleaned data.

    Returns:
        A dictionary containing the username and the final persona.
    """
    username = cleaned_data.get("username", "UnknownUser")
    user_url = cleaned_data.get("user_url", "UnknownURL")
    comments = cleaned_data.get("comments", "")
    posts = cleaned_data.get("posts", "")

    # If comments/posts are lists, join them into strings
    if isinstance(comments, list):
        comments = "\n".join(
            c["text"] if isinstance(c, dict) and "text" in c else str(c)
            for c in comments
        )
    if isinstance(posts, list):
        posts = "\n".join(
            p["content"] if isinstance(p, dict) and "content" in p else str(p)
            for p in posts
        )

    comment_chunks = split_text(comments)
    post_chunks = split_text(posts)

    num_epochs = max(len(comment_chunks), len(post_chunks))
    persona_parts = []

    for i in range(num_epochs):
        comment_part = comment_chunks[i] if i < len(comment_chunks) else ""
        post_part = post_chunks[i] if i < len(post_chunks) else ""

        prompt = build_persona_prompt(
            username,
            user_url,
            comment_part,
            post_part,
            i + 1
        )
        llm = llm_models[i % len(llm_models)]  # Round-robin assignment
        response = llm.invoke([HumanMessage(content=prompt)])

        persona_parts.append(response.content.strip())

    # Combine all epoch results into a final persona text
    final_persona = f"🧠 Persona for {username}:\n\n"
    final_persona += "\n\n---\n\n".join(persona_parts)

    # Save persona to data/drafts/username.txt
    persona_dir = Path("data/drafts")
    persona_dir.mkdir(parents=True, exist_ok=True)
    persona_file = persona_dir / f"{username}.txt"
    with open(persona_file, "w", encoding="utf-8") as f:
        f.write(final_persona)

    return {
        "username": username,
        "user_url": user_url,
        "persona": final_persona
    }
