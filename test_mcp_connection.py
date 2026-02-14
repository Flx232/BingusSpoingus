#!/usr/bin/env python3
"""
Test MCP connection to blaxel-search server.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.web_search import BlaxelSearchMCPClient, search_for_links, WebSearchManager


def test_mcp_connection():
    """Test basic MCP connection and list available tools."""
    print("Testing MCP Connection to blaxel-search")
    print("=" * 50)
    
    endpoint_url = "https://mcp-blaxel-search-vzjx7r.bl.run/mcp"
    print(f"Endpoint: {endpoint_url}")
    
    # Get auth token from environment
    import os
    auth_token = os.getenv('BLAXEL_AUTH_TOKEN')
    if auth_token:
        print("✓ Using authentication token from BLAXEL_AUTH_TOKEN")
    else:
        print("⚠ No BLAXEL_AUTH_TOKEN found in environment")
    
    client = BlaxelSearchMCPClient(endpoint_url, auth_token)
    
    try:
        print("\nListing available tools...")
        tools = client.list_tools()
        
        if tools:
            print(f"\n✓ Connected successfully! Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                print(f"\n{i}. Tool: {tool.get('name', 'Unknown')}")
                if 'description' in tool:
                    print(f"   Description: {tool['description']}")
                if 'inputSchema' in tool:
                    print(f"   Input schema: {tool['inputSchema']}")
        else:
            print("✗ No tools found (but connection worked)")
    
    except Exception as e:
        print(f"✗ Error connecting to MCP server: {e}")
        return False
    
    return True


def test_search_functionality():
    """Test actual search functionality."""
    print("\n\nTesting Search Functionality")
    print("=" * 50)
    
    test_queries = [
        "artificial intelligence latest developments",
        "quantum computing applications",
        "renewable energy solutions 2024"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 40)
        
        try:
            results = search_for_links(query, max_results=3)
            
            if results:
                print(f"✓ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. {result.title}")
                    if result.url:
                        print(f"     URL: {result.url}")
                    if result.description:
                        print(f"     Description: {result.description[:100]}...")
                    if result.relevance_score > 0:
                        print(f"     Relevance: {result.relevance_score:.2f}")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error during search: {e}")


def test_with_manager():
    """Test using WebSearchManager context manager."""
    print("\n\nTesting WebSearchManager")
    print("=" * 50)
    
    with WebSearchManager() as manager:
        # First, list available tools
        print("Checking available tools...")
        tools = manager.list_available_tools()
        if tools:
            print(f"✓ Found {len(tools)} tools available")
        
        # Then test search
        query = "machine learning healthcare applications"
        print(f"\nSearching for: '{query}'")
        
        results = manager.search_for_topic(query, max_results=5)
        
        if results:
            print(f"\n✓ Search successful! Found {len(results)} results")
            # Use the format_results method
            print("\nFormatted results:")
            print(manager.format_results(results))
        else:
            print("❌ No search results")


if __name__ == "__main__":
    print("Blaxel-Search MCP Integration Test")
    print("=" * 60)
    
    # Test 1: Basic connection
    if test_mcp_connection():
        # Test 2: Search functionality
        test_search_functionality()
        
        # Test 3: WebSearchManager
        test_with_manager()
    else:
        print("\nSkipping further tests due to connection failure.")
        print("\nPlease check:")
        print("1. The MCP endpoint URL is correct")
        print("2. You have internet connectivity")
        print("3. The blaxel-search MCP server is running")