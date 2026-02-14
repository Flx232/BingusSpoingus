#!/usr/bin/env python3
"""
Quick test of the web search functionality.
"""

from src.web_search import search_for_links, WebSearchManager

def test_multiple_searches():
    """Test the search functionality with various topics."""
    print("Testing Web Search with Various Topics")
    print("=" * 50)
    
    test_queries = [
        "I want to learn about quantum computing",
        "latest developments in renewable energy 2024",
        "machine learning applications in healthcare",
        "space exploration Mars missions recent discoveries"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        print("-" * 40)
        
        try:
            results = search_for_links(query, max_results=3)
            
            if results:
                print(f"✓ Found {len(results)} relevant sources:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result.title[:60]}...")
                    print(f"     {result.url}")
                    print(f"     Score: {result.relevance_score:.2f}")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_search_manager():
    """Test the WebSearchManager context manager."""
    print("\n\nTesting WebSearchManager Context Manager")
    print("=" * 50)
    
    with WebSearchManager(max_results_per_search=4) as manager:
        query = "artificial intelligence ethics and safety"
        print(f"Searching for: {query}")
        
        results = manager.search_for_topic(query, max_results=4, news_only=True)
        
        if results:
            print(f"\n✓ Found {len(results)} sources via WebSearchManager:")
            for result in results:
                print(f"• {result.title[:50]}...")
                print(f"  {result.url}")
        else:
            print("❌ No results found")

if __name__ == "__main__":
    test_multiple_searches()
    test_search_manager()