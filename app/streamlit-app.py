import sys
import os
from pathlib import Path
import streamlit as st

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from agents.scraping_agent import run_scraping_agent  # noqa: E402
from agents.cleaning_agent import run_cleaning_agent  # noqa: E402
from agents.draft_persona_agent import run_drafting_agent  # noqa: E402
from agents.persona_building_agent import run_persona_building_agent  # noqa: E402


def main():
    st.set_page_config(
        page_title="Reddit Persona Builder",
        page_icon="👤",
        layout="wide"
    )

    st.title("Reddit Persona Builder 👤")
    st.write(
        "Generate a structured persona from a Reddit user's public posts and comments."
    )

    # User input
    user_url = st.text_input(
        "Reddit User URL",
        placeholder="https://www.reddit.com/user/username/",
        help="Enter the full Reddit profile URL"
    )

    if st.button("Generate Persona", type="primary"):
        if user_url:
            try:
                with st.spinner("Initializing pipeline..."):
                    # Setup UI
                    progress_text = st.empty()
                    progress_bar = st.progress(0)

                    # Step 1: Scraping
                    progress_text.text("Step 1/4: Scraping user data...")
                    scraped_data = run_scraping_agent(user_url)
                    progress_bar.progress(25)

                    # Step 2: Cleaning
                    progress_text.text("Step 2/4: Cleaning scraped data...")
                    cleaned_data = run_cleaning_agent(scraped_data)
                    progress_bar.progress(50)

                    # Step 3: Drafting
                    progress_text.text("Step 3/4: Generating draft persona...")
                    draft_text = run_drafting_agent(cleaned_data)
                    progress_bar.progress(75)

                    # Step 4: Final Persona
                    progress_text.text("Step 4/4: Structuring final persona...")
                    persona = run_persona_building_agent(
                        username=cleaned_data["username"],
                        user_url=user_url,
                        draft_text=draft_text
                    )
                    progress_bar.progress(100)

                # Display result
                st.success("Persona generated successfully!")
                st.subheader("🧠 Final Persona")
                st.markdown(persona)

                # Download button
                st.download_button(
                    label="📥 Download Persona as .txt",
                    data=persona,
                    file_name=f"{cleaned_data['username']}_persona.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
        else:
            st.warning("⚠️ Please enter a valid Reddit user URL")

    # Sidebar info
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This app analyzes a Reddit user's public activity
        to generate a structured persona using AI agents.

        It includes:
        - Post & comment scraping
        - Text cleaning & chunking
        - Draft persona analysis (LLM-powered)
        - Structured persona synthesis
        """)


if __name__ == "__main__":
    main()
