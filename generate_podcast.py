#!/usr/bin/env python3
"""
Pipeline to generate podcast scripts from web search results.

This script:
1. Searches for relevant content using web_search.py
2. Extracts URLs from the search results
3. Passes URLs to script_maker.py to generate a podcast script
4. Saves the script to the 'script' folder
"""

import os
import sys
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web_search import search_for_links, WebSearchManager


def ensure_script_folder():
    """Ensure the 'script' folder exists."""
    script_folder = Path("script")
    script_folder.mkdir(exist_ok=True)
    return script_folder


def search_and_extract_urls(query: str, num_results: int = 10) -> list[str]:
    """
    Search for content and extract URLs from the results.
    
    Args:
        query: Search query
        num_results: Number of search results to get
        
    Returns:
        List of URLs
    """
    print(f"🔍 Searching for: '{query}'")
    print(f"   Number of results: {num_results}")
    print("-" * 50)
    
    # Perform search
    results = search_for_links(query, max_results=num_results)
    
    if not results:
        print("❌ No search results found!")
        return []
    
    # Extract URLs
    urls = []
    print(f"\n✅ Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        if result.url:
            urls.append(result.url)
            print(f"{i}. {result.title}")
            print(f"   URL: {result.url}")
            print()
    
    return urls


async def generate_script_from_urls(urls: list[str], output_filename: str, podcast_style: str = "solo_narrative", 
                                  episode_length: str = "medium_15_25_min", tone: str = "casual",
                                  target_audience: str = "general audience"):
    """
    Generate a podcast script from URLs using script_maker.py.
    
    Args:
        urls: List of URLs to use as sources
        output_filename: Output filename (without path)
        podcast_style: Style of podcast
        episode_length: Target episode length
        tone: Tone of the podcast
        target_audience: Target audience
    """
    if not urls:
        print("❌ No URLs provided for script generation!")
        return False
    
    print(f"\n📝 Generating podcast script from {len(urls)} URLs...")
    print(f"   Style: {podcast_style}")
    print(f"   Length: {episode_length}")
    print(f"   Tone: {tone}")
    print(f"   Audience: {target_audience}")
    print("-" * 50)
    
    # Import the generate_podcast_script function from script_maker
    try:
        from script_maker import generate_podcast_script
        
        # Generate the script
        script_content = await generate_podcast_script(
            urls=urls,
            podcast_style=podcast_style,
            episode_length=episode_length,
            tone=tone,
            target_audience=target_audience
        )
        
        # Save to file
        script_folder = ensure_script_folder()
        output_path = script_folder / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"\n✅ Script saved to: {output_path}")
        print(f"   File size: {len(script_content):,} characters")
        
        # Display a preview
        print("\n📄 Script Preview (first 500 characters):")
        print("-" * 50)
        print(script_content[:500])
        print("..." if len(script_content) > 500 else "")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return False


async def main():
    """Main function to run the pipeline."""
    print("🎙️ Podcast Script Generator")
    print("=" * 60)
    print()
    
    # Get user input
    if len(sys.argv) > 1:
        # Use command line argument
        query = ' '.join(sys.argv[1:])
        print(f"Using command line query: '{query}'")
    else:
        # Interactive mode
        query = input("Enter your search query (topic for podcast): ")
    
    if not query.strip():
        print("❌ No query provided!")
        return
    
    # Advanced options (could be made interactive or command line args)
    num_results = 8  # Number of search results to use
    podcast_style = "solo_narrative"  # Options: solo_narrative, educational_deep_dive, news_commentary, storytelling
    episode_length = "medium_15_25_min"  # Options: short_5_10_min, medium_15_25_min, long_30_45_min, extended_60_min
    tone = "casual"  # Options: casual, professional, humorous, dramatic, educational, investigative
    target_audience = "general audience"
    
    # Step 1: Search and extract URLs
    urls = search_and_extract_urls(query, num_results)
    
    if not urls:
        print("❌ No URLs found to generate script from!")
        return
    
    # Step 2: Generate podcast script
    # Create filename with timestamp and query
    safe_query = query.lower().replace(' ', '_')[:30]  # First 30 chars, spaces to underscores
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"podcast_{safe_query}_{timestamp}.md"
    
    success = await generate_script_from_urls(
        urls=urls, 
        output_filename=filename,
        podcast_style=podcast_style,
        episode_length=episode_length,
        tone=tone,
        target_audience=target_audience
    )
    
    if success:
        print(f"\n🎉 Podcast script generation complete!")
        print(f"   Topic: {query}")
        print(f"   Sources: {len(urls)} websites")
        print(f"   Script: script/{filename}")
    else:
        print("\n❌ Failed to generate podcast script")


def run_interactive():
    """Run in interactive mode with more options."""
    print("🎙️ Podcast Script Generator - Interactive Mode")
    print("=" * 60)
    
    # Get search query
    query = input("\nEnter your search query (topic for podcast): ")
    if not query.strip():
        print("❌ No query provided!")
        return
    
    # Get number of sources
    num_results = input("\nHow many web sources to use? (default: 8): ").strip()
    num_results = int(num_results) if num_results.isdigit() else 8
    
    # Get podcast style
    print("\nPodcast styles:")
    print("1. solo_narrative (default)")
    print("2. educational_deep_dive")
    print("3. news_commentary")
    print("4. storytelling")
    style_choice = input("Choose style (1-4, default: 1): ").strip()
    
    podcast_styles = {
        '1': 'solo_narrative',
        '2': 'educational_deep_dive',
        '3': 'news_commentary',
        '4': 'storytelling'
    }
    podcast_style = podcast_styles.get(style_choice, 'solo_narrative')
    
    # Get episode length
    print("\nEpisode length:")
    print("1. short_5_10_min")
    print("2. medium_15_25_min (default)")
    print("3. long_30_45_min")
    print("4. extended_60_min")
    length_choice = input("Choose length (1-4, default: 2): ").strip()
    
    episode_lengths = {
        '1': 'short_5_10_min',
        '2': 'medium_15_25_min',
        '3': 'long_30_45_min',
        '4': 'extended_60_min'
    }
    episode_length = episode_lengths.get(length_choice, 'medium_15_25_min')
    
    # Get tone
    print("\nPodcast tone:")
    print("1. casual (default)")
    print("2. professional")
    print("3. humorous")
    print("4. dramatic")
    print("5. educational")
    print("6. investigative")
    tone_choice = input("Choose tone (1-6, default: 1): ").strip()
    
    tones = {
        '1': 'casual',
        '2': 'professional',
        '3': 'humorous',
        '4': 'dramatic',
        '5': 'educational',
        '6': 'investigative'
    }
    tone = tones.get(tone_choice, 'casual')
    
    # Get target audience
    target_audience = input("\nTarget audience (default: general audience): ").strip()
    target_audience = target_audience if target_audience else "general audience"
    
    # Run the pipeline
    async def run():
        # Search and extract URLs
        urls = search_and_extract_urls(query, num_results)
        
        if not urls:
            print("❌ No URLs found to generate script from!")
            return
        
        # Generate filename
        safe_query = query.lower().replace(' ', '_')[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{safe_query}_{timestamp}.md"
        
        # Generate script
        await generate_script_from_urls(
            urls=urls,
            output_filename=filename,
            podcast_style=podcast_style,
            episode_length=episode_length,
            tone=tone,
            target_audience=target_audience
        )
    
    asyncio.run(run())


if __name__ == "__main__":
    if "--interactive" in sys.argv:
        run_interactive()
    else:
        asyncio.run(main())