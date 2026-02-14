#!/usr/bin/env python3
"""
Example script demonstrating web search using blaxel-search MCP server.
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from web_search import WebSearchManager, search_for_links

# Load environment variables from .env file
load_dotenv()


def interactive_search():
    """Interactive search mode."""
    print("Interactive Web Search")
    print("=" * 50)
    print("Enter your search queries (or 'quit' to exit)")
    print("This will find relevant links for podcast research")
    print()
    
    with WebSearchManager(max_results_per_search=8) as search_manager:
        while True:
            query = input("\nEnter your topic/question: ")
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query.strip():
                continue
            
            print(f"\nSearching for: '{query}'")
            print("-" * 40)
            
            try:
                results = search_manager.search_for_topic(query, max_results=8, news_only=True)
                
                if results:
                    print(f"\nFound {len(results)} relevant sources:")
                    print()
                    
                    for i, result in enumerate(results, 1):
                        print(f"{i}. {result.title}")
                        print(f"   🔗 {result.url}")
                        if result.description:
                            # Truncate long descriptions
                            desc = result.description[:150]
                            if len(result.description) > 150:
                                desc += "..."
                            print(f"   📄 {desc}")
                        if result.relevance_score > 0:
                            print(f"   📊 Relevance: {result.relevance_score:.2f}")
                        print()
                else:
                    print("❌ No relevant sources found. Try a different query.")
                    
            except Exception as e:
                print(f"❌ Error during search: {e}")


def batch_search_demo():
    """Demonstrate batch searching with common podcast topics."""
    print("\nBatch Search Demo")
    print("=" * 50)
    
    demo_topics = [
        "artificial intelligence latest breakthroughs 2024",
        "climate change solutions renewable energy",
        "space exploration Mars missions recent",
        "cryptocurrency blockchain future trends",
        "quantum computing practical applications"
    ]
    
    with WebSearchManager(max_results_per_search=5) as search_manager:
        for topic in demo_topics:
            print(f"\nTopic: {topic}")
            print("-" * 60)
            
            results = search_manager.search_for_topic(topic, max_results=5, news_only=True)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.title}")
                    print(f"   {result.url}")
                    if result.description:
                        print(f"   {result.description[:100]}...")
                print()
            else:
                print("No results found for this topic.\n")


def synchronous_example():
    """Example using the synchronous wrapper."""
    print("\nSynchronous Search Example")
    print("=" * 50)
    
    query = "machine learning natural language processing 2024"
    print(f"Searching for: {query}")
    
    try:
        results = search_for_links(query, max_results=5)
        
        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.url}")
                if result.description:
                    print(f"   {result.description[:100]}...")
                print()
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")


def check_prerequisites():
    """Check if blaxel-search is available."""
    print("Checking Prerequisites")
    print("=" * 50)
    
    import subprocess
    
    try:
        # Check if Node.js is available
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js is available: {result.stdout.strip()}")
        else:
            print("✗ Node.js is not available")
            return False
    except FileNotFoundError:
        print("✗ Node.js is not installed")
        return False
    
    try:
        # Check if npx is available
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npx is available: {result.stdout.strip()}")
        else:
            print("✗ npx is not available")
            return False
    except FileNotFoundError:
        print("✗ npx is not available")
        return False
    
    # Note: We can't easily check if blaxel-search is available without running it
    print("✓ Prerequisites look good!")
    print("\nNote: blaxel-search will be downloaded automatically via npx when needed")
    
    return True


def main():
    """Main function."""
    print("Web Search Example using DuckDuckGo")
    print("=" * 60)
    
    print("\nChoose an option:")
    print("1. Interactive search")
    print("2. Batch search demo")
    print("3. Synchronous example")
    print("4. All examples")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    try:
        if choice == '1':
            interactive_search()
        elif choice == '2':
            batch_search_demo()
        elif choice == '3':
            synchronous_example()
        elif choice == '4':
            batch_search_demo()
            synchronous_example()
            interactive_search()
        else:
            print("Invalid choice. Running interactive search...")
            interactive_search()
            
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Try different search terms")


if __name__ == "__main__":
    main()