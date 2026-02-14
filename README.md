# BingusSpoingus

AI-powered podcast generation from user text. The podcast output is downloaded locally and cleared when the user closes the window.

## Project Steps

1. ✅ **Web source compilation** - Implemented using blaxel-search MCP server (Exa AI powered) to find relevant sources from user input
2. Create RAG from compiled sources  
3. Create a podcast script from the RAG
4. Generate mp3 from ElevenLabs
5. Create frontend that takes user input and has the embedded audio

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BingusSpoingus.git
cd BingusSpoingus
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment (optional):
```bash
cp .env.example .env
# Edit .env if you need to add any API keys later
```

## Usage

### Web Search (Step 1)

The web search module uses the blaxel-search MCP server endpoint to find relevant sources directly from user input.

```python
from src.web_search import WebSearchManager, search_for_links

# Context manager usage (recommended)
with WebSearchManager() as search_manager:
    results = search_manager.search_for_topic(
        "artificial intelligence machine learning applications", 
        max_results=10
    )
    
    for result in results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Description: {result.description}")
        print()

# Simple function usage
results = search_for_links("climate change renewable energy", max_results=8)
for result in results:
    print(f"{result.title} - {result.url}")
```

### Running the Example

```bash
python examples/web_search_example.py
```

## Features of Web Search

- **MCP Server Integration**: Uses blaxel-search MCP server endpoint at `https://mcp-blaxel-search-vzjx7r.bl.run/mcp`
- **Exa AI Powered**: Leverages Exa AI's advanced web search capabilities for high-quality results
- **Multiple Search Tools Available**: 
  - `web_search_exa`: General web search
  - `research_paper_search`: Academic papers
  - `company_research`: Company information
  - `wikipedia_search_exa`: Wikipedia articles
  - `github_search`: GitHub repositories
- **JSON-RPC 2.0 Protocol**: Standard MCP protocol over HTTP
- **Structured results**: Returns clean SearchResult objects with title, URL, description, and text content
- **Authentication**: Uses Bearer token authentication (required)

### Authentication Setup

The blaxel-search MCP endpoint requires authentication:

1. Add your authentication token to `.env` file:
```
BLAXEL_AUTH_TOKEN=your-blaxel-auth-token
```

2. The web search will automatically use this token from the environment.

### Available Search Tools

The MCP server provides several specialized search tools:
- **Web Search**: General web content search
- **Research Papers**: Academic papers and research
- **Company Research**: Detailed company information
- **Wikipedia**: Wikipedia article search
- **GitHub**: Repository and code search
- **LinkedIn**: Company pages on LinkedIn

## Next Steps

- [ ] Implement Step 2: RAG creation from compiled sources
- [ ] Implement Step 3: Podcast script generation  
- [ ] Implement Step 4: Audio generation with ElevenLabs
- [ ] Implement Step 5: Frontend interface