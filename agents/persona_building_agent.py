"""Module for building structured personas from draft personas."""

import re
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Use a single LLM for summarization
llm = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0.5)


def remove_think_blocks(text: str) -> str:
    """
    Remove the think blocks from the text.

    Args:
        text: The text to remove the think blocks from.

    Returns:
        A string of the text without the think blocks.
    """
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def build_structured_persona_prompt(
    draft_text: str,
    user_url: str,
    username: str
) -> str:
    """
    Build the prompt for the persona building agent.

    Args:
        draft_text: The draft text.
        user_url: The URL of the user's profile.
        username: The username of the user.

    Returns:
        A string of the prompt.
    """
    return (
        "You are a professional persona analysis agent. Your task is to create "
        "a concise, structured persona for a Reddit user based on their data. "
        "Follow these strict rules:\n\n"
        "1. DO NOT include any meta-commentary or thinking process\n"
        "2. DO NOT use any <think> blocks or similar markup\n"
        "3. For each trait/point, cite a SPECIFIC post or comment that shows it\n"
        "4. Citations: [Source: r/subreddit - Post/Comment description]\n"
        "5. Keep bullet points concise but informative\n"
        "6. Add 4-5 bullet points for each section\n\n"
        "Use this exact format:\n\n"
        f"# Persona: {username}\n\n{user_url}\n"
        "## Basic Info\n"
        "- Username: [username]\n"
        "- Age: [estimate or Unknown]\n"
        "- Occupation: [estimate or Unknown]\n"
        "- Status: [estimate or Unknown]\n"
        "- Location: [estimate or Unknown]\n"
        "- Tier: [estimate or Unknown]\n"
        "- Archetype: [primary user type]\n\n"
        "## Personality\n"
        "[4-5 bullet points with specific citations]\n\n"
        "## Motivations\n"
        "[4-5 bullet points with specific citations]\n\n"
        "## Behaviour & Habits\n"
        "[4-5 bullet points with specific citations]\n\n"
        "## Frustrations\n"
        "[4-5 bullet points with specific citations]\n\n"
        "## Goals & Needs\n"
        "[4-5 bullet points with specific citations]\n\n"
        "## Representative Quote\n"
        "[A meaningful quote with context and citation]\n\n"
        "Here is the draft persona to analyze:\n\n"
        f"{draft_text}\n"
    )


def run_persona_building_agent(username: str, user_url: str, draft_text: str) -> str:
    """
    Run the persona building agent.

    Args:
        username: The username of the user.
        user_url: The URL of the user's profile.
        draft_text: The draft text.

    Returns:
        A string of the concise persona.
    """
    prompt = build_structured_persona_prompt(draft_text, user_url, username)
    response = llm.invoke([HumanMessage(content=prompt)])
    concise_persona = remove_think_blocks(response.content)

    # Save to data/persona/username.txt
    persona_dir = Path("data/persona")
    persona_dir.mkdir(parents=True, exist_ok=True)
    persona_file = persona_dir / f"{username}.txt"
    with open(persona_file, "w", encoding="utf-8") as f:
        f.write(concise_persona)

    print(f"Concise persona for {username} saved to {persona_file}")
    return concise_persona


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agents/persona_building_agent.py <username>")
    else:
        run_persona_building_agent(sys.argv[1])
