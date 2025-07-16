# Reddit Persona Builder 🧠

A comprehensive AI-powered system that analyzes Reddit users' public activity to generate detailed user personas. This project uses multi-agent architecture with LangChain and Groq API to scrape, clean, and analyze Reddit data.

## 🚀 Features

- **Multi-Agent Architecture**: Modular design with specialized agents for scraping, cleaning, drafting, and persona building
- **Reddit Data Scraping**: Extracts posts and comments from any public Reddit profile
- **AI-Powered Analysis**: Uses multiple LLM models via Groq API for comprehensive persona generation
- **Structured Output**: Generates detailed personas with citations and sources
- **Caching System**: Avoids redundant API calls by caching scraped data
- **Multiple Interfaces**: Command-line, LangChain pipeline, and Streamlit web app
- **Citation Support**: Each persona trait includes specific source citations

## 📋 Project Structure

```
reddit-persona-builder/
├── agents/
│   ├── scraping_agent.py                         # Orchestrates data scraping
│   ├── cleaning_agent.py                         # Cleans and structures raw data
│   ├── draft_persona_agent.py                    # Generates initial persona draft
│   ├──  persona_building_agent.py                # Creates final structured persona
|   └── test_agents.py                            # Sequential agent testing
├── scrapers/
│   ├── reddit_comment_scraper.py                 # Scrapes user comments
│   └── reddit_post_scraper.py                    # Scrapes user posts
├── tools/
│   ├── scrape_comments_tool.py                   # LangChain tool for comments
│   └── scrape_posts_tool.py                      # LangChain tool for posts
├── data/
│   ├── scrapings/                                # Raw scraped data
│   ├── cleaned/                                  # Cleaned JSON data
│   ├── drafts/                                   # Draft personas
│   └── persona/                                  # Final personas
|-- app/
|   └── streamlit-app.py                          # Web interface
├── main.py                                       # LangChain pipeline interface
├── .env.example                                  # Environment variables template
|-- .gitignore                                    # Git ignore file
|-- Generative_AI_Internship_Assignment.pdf       # Project definition
|-- personaExample.webp                           # Example persona image
└── README.md                                     # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Reddit API credentials
- Groq API key

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/gupta-v/reddit-persona-builder
   cd reddit-persona-builder
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   Activate Virtual Environment
   # venv/Scripts/activate on windows
   # source venv/bin/activate on Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Reddit API credentials**

   - Visit [Reddit Apps](https://www.reddit.com/prefs/apps/)
   - Click "Create App" or "Create Another App"
   - Fill in the details:
     - **Name**: `persona_generator` (or any name)
     - **App type**: `script`
     - **Redirect URI**: `http://localhost:8080`
   - Click "Create App"
   - Note down the **Client ID** (under the app name) and **Client Secret**

5. **Get Groq API key**

   - Visit [Groq Console](https://console.groq.com/keys)
   - Create a new API key

6. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=persona_generator by u/yourusername
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 📖 Usage

### Method 1: Command Line Interface (Recommended for testing Agents)

```bash
python test_agents.py
```

When prompted, enter a Reddit profile URL:

```
Enter the url of user: https://www.reddit.com/user/kojied/
```

### Method 2: LangChain Pipeline

```bash
python main.py
```

This uses LangChain's LCEL (LangChain Expression Language) for a more structured pipeline.

### Method 3: Streamlit Web Interface

```bash
streamlit run streamlit-app.py
```

Access the web interface at `http://localhost:8501`

## 🔧 How It Works

### 1. Scraping Agent

- Extracts username from Reddit URL
- Fetches recent posts and comments using Reddit API
- Caches data to avoid redundant API calls
- Handles rate limiting and error recovery

### 2. Cleaning Agent

- Parses raw text data into structured JSON
- Extracts metadata (titles, subreddits, timestamps, upvotes)
- Organizes comments by posts they belong to
- Handles replies and quoted comments

### 3. Draft Persona Agent

- Splits large text into manageable chunks
- Uses multiple LLM models in round-robin fashion
- Generates detailed analysis with citations
- Processes data in epochs for comprehensive coverage

### 4. Persona Building Agent

- Synthesizes draft analysis into structured persona
- Removes meta-commentary and thinking blocks
- Formats output according to persona template
- Ensures all traits have proper citations

## 🧠 Methodology & Design Decisions

### Chunked Input for LLM Efficiency

To process long Reddit histories efficiently, the system splits posts and comments into manageable chunks using `RecursiveCharacterTextSplitter`. Each chunk pair is analyzed independently using a round-robin allocation of multiple Groq-hosted LLMs (Meta Llama and DeepSeek). This approach:

- Reduces token overload risk
- Maximizes context utilization per call
- Enables parallel persona drafting across epochs

### Two-Shot Mechanism

We employ a two-stage "two-shot" mechanism:

1. **Drafting Phase**  
   The system generates partial persona insights across text chunks, each tied to specific citations.

2. **Structuring Phase**  
   A separate summarization LLM restructures and condenses the traits into clean persona categories, preserving source traceability.

This layered approach increases interpretability and citation clarity.

### Why No Data Reduction?

While NLP techniques like clustering or TF-IDF could reduce content, we prioritized full data preservation due to:

- The 48-hour deadline
- Importance of nuanced tone/context in personality traits
- LLMs’ ability to handle raw expressive content when chunked properly

### LangGraph Consideration

Although not implemented due to time limits, this system was originally scoped to be built with **LangGraph**, allowing for:

- Explicit control over data flow
- Easier multi-agent orchestration
- Retry logic and conditional branches

Having used LangGraph in prior projects, I plan to integrate it in future iterations.

## 📊 Output Format

The generated persona includes:

- **Basic Info**: Username, estimated age, occupation, location, etc.
- **Personality**: Communication style, humor, behavioral patterns
- **Motivations**: What drives the user's online activity
- **Behaviour & Habits**: Posting patterns, community participation
- **Frustrations**: Pain points and complaints
- **Goals & Needs**: What the user seeks from Reddit
- **Representative Quote**: Characteristic statement with context

Each section includes 4-5 bullet points with specific citations in the format:
`[Source: r/subreddit - Post/Comment description]`

## 🔍 Sample Input/Output

### Input

```
https://www.reddit.com/user/kojied/
```

### Output Structure

```markdown
# Persona: OakleyTheReader

https://www.reddit.com/user/OakleyTheReader/

## Basic Info

- Username: OakleyTheReader
- Age: Young adult (late teens to early twenties)
- Occupation: Unknown
- Status: Active Reddit user
- Location: Possibly Eastern Europe
- Tier: Likely a regular Reddit user
- Archetype: Gamer and curious learner

## Personality

- Curious and analytical, often seeking help from communities. [Source: r/subreddit - "I've been looking for like an hour now and still haven't found anything decent."]
- Polite and appreciative, thanking others for their explanations. [Source: r/subreddit - "Thank you for the detailed explanation!"]
- Shows a dry sense of humor and occasional sarcasm. [Source: r/subreddit - "real unfortunately"]
- Admits mistakes and is willing to learn from them. [Source: r/subreddit - "It gathers into stockpile? Damn that sucks..."]
- Engages in creative problem-solving, especially in gaming. [Source: r/subreddit - "Using oil barrels and speed potions to defeat a Minotaur."]
  ...
```

## 🛡️ Privacy & Ethics

- Only analyzes **public** Reddit data
- Respects Reddit's API terms of service
- Includes rate limiting to avoid overloading servers
- No personal data storage beyond session
- Generated personas are for analysis purposes only

## 🚨 Limitations

- Limited to public Reddit activity
- Analysis quality depends on user's posting history
- May not capture complete personality picture
- Subject to Reddit API rate limits
- Requires active internet connection

## 🔧 Dependencies

```python
# Core dependencies
praw>=7.0.0              # Reddit API wrapper
python-dotenv>=0.19.0    # Environment variables
langchain-groq>=0.1.0    # Groq LLM integration
langchain-core>=0.1.0    # LangChain core functionality
streamlit>=1.28.0        # Web interface

# Text processing
langchain-text-splitters>=0.0.1

# Utilities
pathlib                  # File system operations
json                     # JSON handling
re                       # Regular expressions
```

## 🐛 Troubleshooting

### Common Issues

1. **Reddit API Authentication Error**

   - Verify your `.env` file has correct credentials
   - Ensure Reddit app is configured as "script" type
   - Check if API credentials are active

2. **Groq API Rate Limits**

   - The system uses multiple models to distribute load
   - Add delays between requests if needed
   - Check your Groq API quota

3. **Empty or Minimal Personas**

   - User might have limited public activity
   - Try users with more posts/comments
   - Check if user account is active

4. **File Permission Errors**
   - Ensure write permissions for `data/` directory
   - Run with appropriate user permissions

## 📝 Development

### Adding New Features

1. **New Analysis Types**: Extend `draft_persona_agent.py` with additional analysis categories
2. **Additional Data Sources**: Create new scrapers in `scrapers/` directory
3. **Custom Output Formats**: Modify `persona_building_agent.py` template
4. **New LLM Models**: Add models to `llm_models` list in draft agent

### Testing

```bash
# Test individual components
python agents/scraping_agent.py
python agents/cleaning_agent.py
python agents/draft_persona_agent.py
python agents/persona_building_agent.py

# Test complete agent pipeline
python test_agents.py
```

## 🕒 Time-Bound Scope

This project was developed as part of a 48-hour technical assignment. Given the time constraint, I prioritized:

- Maintaining raw data fidelity over aggressive reduction
- Clarity and citation in persona traits
- A robust, working multi-agent pipeline over LangGraph orchestration (planned for future versions)

Despite the deadline, all core requirements were implemented, and modular structure ensures it's ready for future expansion or deployment.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Reddit API for providing access to public data
- Groq for fast LLM inference
- LangChain for agent orchestration framework
- PRAW (Python Reddit API Wrapper) for Reddit integration

## 📞 Support

For questions or issues:

1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed description
4. Contact the development team

---

**Note**: This tool is for educational and research purposes. Please use responsibly and respect user privacy.
