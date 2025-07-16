"""Module for testing the persona building pipeline."""

from scraping_agent import run_scraping_agent
from cleaning_agent import run_cleaning_agent
from agents.draft_persona_agent import run_drafting_agent
from agents.persona_building_agent import run_persona_building_agent


def main():
    """
    Run the persona building pipeline.

    Takes a user URL as input and runs the agents in sequence.
    Returns the final persona as output.
    """
    user_url = input(
        "Enter the url of user "
        "(e.g., https://www.reddit.com/user/OakleyTheReader/): "
    )
    if not user_url:
        user_url = "https://www.reddit.com/user/OakleyTheReader/"

    # Step 1: Run scraper agent
    print("[+] Scraping user data...")
    scraped_data = run_scraping_agent(user_url)
    username = scraped_data['username']
    print("[*] Finished Scraping")

    # Step 2: Run cleaner agent
    print("[+] Cleaning scraped data...")
    cleaned_output = run_cleaning_agent(scraped_data)
    username = cleaned_output['username']
    print(f"[*] Cleaned the scrapings for user: {username}")

    # Step 3: Draft persona generation
    print("[+] Generating draft persona...")
    draft_persona = run_drafting_agent(cleaned_output)
    print("[*] Draft generated")

    # Step 4: Concise persona generation
    print("[+] Structuring final persona...")
    concise_persona = run_persona_building_agent(
        username,
        user_url,
        draft_persona['persona']
    )
    print("[*] Structured persona ready")
    print(f"Concise persona for {username}:\n{concise_persona}")


if __name__ == "__main__":
    main()
