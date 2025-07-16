from langchain_core.runnables import RunnableLambda, RunnableMap
from agents.scraping_agent import run_scraping_agent
from agents.cleaning_agent import run_cleaning_agent
from agents.draft_persona_agent import run_drafting_agent
from agents.persona_building_agent import run_persona_building_agent


# ──────────────── Chain Definition ────────────────
def build_chain():
    """
    Creates a LangChain pipeline using LCEL (| chaining).
    Returns:
        Runnable: the full persona generation pipeline
    """
    return (
        RunnableLambda(lambda url: {"user_url": url})
        | RunnableMap({
            "scraped_data": lambda d: run_scraping_agent(d["user_url"]),
            "user_url": lambda d: d["user_url"],
        })
        | RunnableMap({
            "cleaned_data": lambda d: run_cleaning_agent(d["scraped_data"]),
            "username": lambda d: d["scraped_data"]["username"],
            "user_url": lambda d: d["user_url"],
        })
        | RunnableMap({
            "draft": lambda d: run_drafting_agent(d["cleaned_data"]),
            "username": lambda d: d["username"],
            "user_url": lambda d: d["user_url"],
        })
        | RunnableLambda(lambda d: run_persona_building_agent(
            username=d["username"],
            user_url=d["user_url"],
            draft_text=d["draft"]
        ))
    )

def run_chain(user_url: str) -> str:
    chain = build_chain()
    result = chain.invoke(user_url)
    return result


if __name__ == "__main__":
    user_url = input("Enter the Reddit profile URL: ").strip()
    if not user_url:
        user_url = "https://www.reddit.com/user/OakleyTheReader/"

    try:
        persona = run_chain(user_url)
        print(f"\n🧠 Generated Persona:\n\n{persona}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
