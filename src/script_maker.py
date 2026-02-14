from mcp.server.fastmcp import FastMCP
import anthropic
import os
import httpx
from bs4 import BeautifulSoup
from typing import Dict
import asyncio

# Initialize FastMCP
mcp = FastMCP("web-to-podcast")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

async def fetch_webpage(url: str) -> Dict[str, str]:
    """Fetch and extract text content from a webpage."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as http_client:
            response = await http_client.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, nav, footer, header elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Get title
            title = soup.title.string if soup.title else "No title"
            
            return {
                "url": url,
                "title": title,
                "content": text[:15000],  # Limit content length
                "success": True,
                "error": None
            }
    except Exception as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def generate_podcast_script(
    urls: list[str],
    podcast_style: str = "solo_narrative",
    episode_length: str = "medium_15_25_min",
    tone: str = "casual",
    target_audience: str = "general audience"
) -> str:
    """
    Read multiple webpages and generate a podcast script based on their content.
    
    Args:
        urls: Array of website URLs to base the podcast on
        podcast_style: Style of podcast (solo_narrative, educational_deep_dive, news_commentary, storytelling)
        episode_length: Target length (short_5_10_min, medium_15_25_min, long_30_45_min, extended_60_min)
        tone: Overall tone (casual, professional, humorous, dramatic, educational, investigative)
        target_audience: Who is the podcast for
    """
    
    print(f"Fetching {len(urls)} webpages...")
    
    # Fetch all webpages concurrently
    fetch_tasks = [fetch_webpage(url) for url in urls]
    results = await asyncio.gather(*fetch_tasks)
    
    # Build context from all pages
    context = "# Source Material from Webpages:\n\n"
    successful_fetches = 0
    source_summaries = []
    
    for i, result in enumerate(results, 1):
        if result["success"]:
            context += f"## Source {i}: {result['title']}\n"
            context += f"URL: {result['url']}\n\n"
            context += f"{result['content']}\n\n"
            context += "---\n\n"
            successful_fetches += 1
            source_summaries.append(f"- {result['title']} ({result['url']})")
        else:
            context += f"## Source {i}: FAILED\n"
            context += f"URL: {result['url']}\n"
            context += f"Error: {result['error']}\n\n"
    
    if successful_fetches == 0:
        return "Error: Failed to fetch any webpages successfully. Please check the URLs."
    
    print(f"Successfully fetched {successful_fetches}/{len(urls)} webpages")
    
    prompt = f"""You are a professional podcast scriptwriter. Based on the following source material from {successful_fetches} webpages, write a complete podcast script.

{context}

PODCAST SPECIFICATIONS:
- Style: {podcast_style}
- Episode Length: {episode_length}
- Tone: {tone}
- Target Audience: {target_audience}

SCRIPT REQUIREMENTS:
1. FORMAT: Write in standard podcast script format with clear speaker labels
2. NATURAL DIALOGUE: Make it sound like reading facts based on findings from research
3. PACING: Include natural pauses [PAUSE], transitions, and segment breaks
4. AUTHENTICITY: Make the narrator sound like they're reporting based on findings
5. CITATIONS: Naturally mention sources when referencing specific information

SOURCES TO CREDIT:
{chr(10).join(source_summaries)}

Generate a complete, production-ready podcast script that brings this content to life in an engaging way for {target_audience}.

Make sure script focuses only on delivering information. No need to add additional flair. Just information from the url and context.

Make sure the script matches the {episode_length} target length. 

When generating the text do not add tone cues do not try to add comments, just have the text itself.
"""

    # Generate script with Claude
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        temperature=0.7,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    script_content = message.content[0].text
    
    response = f"""# PODCAST SCRIPT GENERATED

**Episode Type:** {podcast_style.replace('_', ' ').title()}
**Length:** {episode_length.replace('_', ' ')}
**Tone:** {tone.title()}
**Target Audience:** {target_audience}
**Sources Analyzed:** {successful_fetches}/{len(urls)}

---

{script_content}

---

**Sources Referenced:**
{chr(10).join(source_summaries)}
"""
    
    return response


@mcp.tool()
async def generate_storytelling_podcast(
    urls: list[str],
    narrative_style: str = "documentary",
    narrator_voice: str = "third_person_omniscient"
) -> str:
    """
    Generate a narrative storytelling podcast based on the content from URLs.
    
    Args:
        urls: Array of website URLs
        narrative_style: investigative_journalism, historical_narrative, personal_story, documentary
        narrator_voice: first_person, third_person_omniscient, third_person_limited
    """
    
    print(f"Fetching {len(urls)} webpages for storytelling...")
    
    # Fetch webpages
    fetch_tasks = [fetch_webpage(url) for url in urls]
    results = await asyncio.gather(*fetch_tasks)
    
    context = "# Story Source Material:\n\n"
    source_summaries = []
    
    for i, result in enumerate(results, 1):
        if result["success"]:
            context += f"## Source {i}: {result['title']}\n"
            context += f"{result['content']}\n\n---\n\n"
            source_summaries.append(f"- {result['title']} ({result['url']})")
    
    prompt = f"""You are a master storyteller and podcast scriptwriter. Based on the following source material, create a captivating narrative podcast script.

{context}

NARRATIVE SPECIFICATIONS:
- Style: {narrative_style}
- Voice: {narrator_voice}

STORYTELLING REQUIREMENTS:
1. Craft a compelling narrative arc (setup, rising action, climax, resolution)
2. Use vivid, descriptive language that paints pictures in the listener's mind
3. Build suspense and maintain engagement throughout
4. Include scene-setting and atmospheric descriptions
5. Use pacing effectively:
   - Short sentences for tension
   - Longer, flowing sentences for reflection
   - Strategic [PAUSE] markers for dramatic effect
6. Incorporate direct quotes from sources where powerful
7. Make the listener feel like they're experiencing the story with the narrator
8. Use narrative techniques:
   - Foreshadowing (hint at what's coming)
   - Callbacks (reference earlier points with new meaning)
   - Revelations (strategic information drops)
9. Include [MUSIC CUE: description] where it would enhance the story

Transform this information into a story that people will want to hear from beginning to end."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}]
    )
    
    script = message.content[0].text
    
    return f"""# NARRATIVE PODCAST SCRIPT

**Style:** {narrative_style.replace('_', ' ').title()}
**Voice:** {narrator_voice.replace('_', ' ').title()}

---

{script}

---

**Sources:**
{chr(10).join(source_summaries)}
"""


@mcp.tool()
async def analyze_sources_for_podcast(
    urls: list[str],
    podcast_type: str = "general"
) -> str:
    """
    Analyze URLs and suggest podcast structure, key topics, and potential angles.
    
    Args:
        urls: Array of website URLs to analyze
        podcast_type: Type of podcast you're planning
    """
    
    print(f"Fetching and analyzing {len(urls)} webpages...")
    
    # Fetch webpages
    fetch_tasks = [fetch_webpage(url) for url in urls]
    results = await asyncio.gather(*fetch_tasks)
    
    context = "# Content to Analyze:\n\n"
    source_summaries = []
    
    for i, result in enumerate(results, 1):
        if result["success"]:
            # Use first 3000 chars for analysis to save tokens
            preview = result['content'][:3000]
            context += f"## Source {i}: {result['title']}\n"
            context += f"URL: {result['url']}\n\n"
            context += f"{preview}...\n\n---\n\n"
            source_summaries.append(f"- {result['title']} ({result['url']})")
    
    prompt = f"""You are a podcast content strategist. Analyze the following sources to provide strategic recommendations for creating a {podcast_type} podcast.

{context}

ANALYSIS FRAMEWORK:
Provide a comprehensive analysis with:

1. **MAIN THEMES**: What are the core topics across all sources? Identify 3-5 major themes.

2. **HOOK IDEAS**: Suggest 5 compelling ways to open the podcast that will grab listeners immediately.

3. **KEY TALKING POINTS**: List the main points to cover in order. Create a logical flow.

4. **INTERESTING ANGLES**: What are 3-4 unique perspectives or angles that aren't obvious?

5. **POTENTIAL SEGMENTS**: How should the episode be structured? Suggest segment titles and durations.

6. **QUESTIONS TO ADDRESS**: What would the audience want to know? List 7-10 questions.

7. **STORYTELLING OPPORTUNITIES**: Identify specific anecdotes, examples, or narrative moments.

8. **RECOMMENDED FORMAT**: What podcast style would work best and why?

9. **ESTIMATED LENGTH**: Based on the depth of content, how long should this episode be?

10. **CHALLENGES**: What concepts might be difficult to explain in audio?

11. **PRODUCTION NOTES**: Suggestions for music, sound effects, or pacing?

Be specific and actionable. Reference actual content from the sources."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis = message.content[0].text
    
    return f"""# PODCAST SOURCE ANALYSIS

{analysis}

---

**Sources Analyzed:**
{chr(10).join(source_summaries)}

---

Ready to generate? Use 'generate_podcast_script' with your chosen parameters based on this analysis.
"""


@mcp.tool()
async def compare_sources_podcast(
    urls: list[str],
    comparison_angle: str = "different perspectives on the same topic"
) -> str:
    """
    Create a podcast that compares and contrasts information from multiple sources.
    
    Args:
        urls: Array of website URLs with different perspectives
        comparison_angle: What aspect to compare
    """
    
    print(f"Fetching {len(urls)} webpages for comparison...")
    
    # Fetch webpages
    fetch_tasks = [fetch_webpage(url) for url in urls]
    results = await asyncio.gather(*fetch_tasks)
    
    context = "# Sources to Compare:\n\n"
    source_summaries = []
    
    for i, result in enumerate(results, 1):
        if result["success"]:
            context += f"## Source {i}: {result['title']}\n"
            context += f"URL: {result['url']}\n\n"
            context += f"{result['content']}\n\n---\n\n"
            source_summaries.append(f"- {result['title']} ({result['url']})")
    
    prompt = f"""You are creating a podcast that explores {comparison_angle}. 

{context}

TASK:
Create a podcast script that:

1. **INTRODUCES THE LANDSCAPE**: What's the topic and why do different views exist?

2. **PRESENTS EACH PERSPECTIVE**: 
   - Fairly represent each source's viewpoint
   - Use direct quotes where powerful
   - Explain the reasoning behind each position

3. **COMPARES AND CONTRASTS**:
   - Where do they agree?
   - Where do they disagree?
   - What are the key points of tension?

4. **ANALYZES**:
   - Which arguments are stronger and why?
   - What evidence supports each side?

5. **SYNTHESIZES**:
   - What can we learn from examining all perspectives?
   - Is there a middle ground?
   - What questions remain unanswered?

FORMAT:
- Conversational but analytical tone
- Include [PAUSE] for reflection moments
- Structure with clear segments
- 20-30 minute script length

Make it balanced, thoughtful, and engaging."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return f"""# COMPARATIVE ANALYSIS PODCAST

**Comparison Focus:** {comparison_angle}
**Sources:** {len(urls)}

---

{message.content[0].text}

---

**Sources Compared:**
{chr(10).join(source_summaries)}
"""


# For running as a standalone script
if __name__ == "__main__":
    import asyncio
    import sys
    
    if len(sys.argv) > 1:
        # Direct execution mode
        urls = sys.argv[1:]
        
        async def run():
            print(f"Generating podcast script from {len(urls)} URLs...\n")
            result = await generate_podcast_script(
                urls=urls,
                podcast_style="solo_narrative",
                episode_length="medium_15_25_min",
                tone="casual"
            )
            
            # Save to file
            with open("podcast_script.md", "w") as f:
                f.write(result)
            
            print(result)
            print("\n✅ Script saved to podcast_script.md")
        
        asyncio.run(run())
    else:
        # Run as MCP server
        mcp.run()