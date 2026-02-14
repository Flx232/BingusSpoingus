"""
Web search module using blaxel-search MCP server to find relevant links.

This module communicates with the blaxel-search MCP endpoint to find
relevant web sources for podcast content generation.
"""

import json
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import time
import uuid
from datetime import datetime, timedelta, timezone


@dataclass
class SearchResult:
    """Data class for search results."""
    title: str
    url: str
    description: str
    relevance_score: float = 0.0


class BlaxelSearchMCPClient:
    """Client for communicating with blaxel-search MCP server via HTTP."""
    
    def __init__(self, endpoint_url: str = "https://mcp-blaxel-search-vzjx7r.bl.run/mcp", auth_token: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            endpoint_url: The HTTP endpoint for the blaxel-search MCP server
            auth_token: Optional authentication token
        """
        self.endpoint_url = endpoint_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        # Add authentication if provided
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
        
    def _send_mcp_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an MCP JSON-RPC request to the server.
        
        Args:
            method: The MCP method to call
            params: Parameters for the method
            
        Returns:
            Response from the MCP server
        """
        # Create JSON-RPC 2.0 request
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {}
        }
        
        try:
            print(f"Sending MCP request to {self.endpoint_url}")
            print(f"Method: {method}")
            print(f"Params: {params}")
            
            response = self.session.post(
                self.endpoint_url,
                json=request_data,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"HTTP error: {response.status_code}")
                print(f"Response body: {response.text}")
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if "error" in response_data:
                error_msg = response_data["error"].get("message", "Unknown MCP error")
                raise Exception(f"MCP Error: {error_msg}")
                
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise Exception(f"Network error communicating with MCP server: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response.text}")
            raise Exception(f"Invalid JSON response from MCP server: {e}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of available tools
        """
        response = self._send_mcp_request("tools/list")
        return response.get("result", {}).get("tools", [])
    
    def search(self, query: str, max_results: int = 10, news_only: bool = False, days_back: int = 7) -> List[SearchResult]:
        """
        Perform a search using the web_search_exa tool from MCP server.
        """
        try:
            # Base arguments expected by the tool
            arguments = {
                "query": query,
                "numResults": max_results
            }
            
            # Apply Exa's news and date filters if requested
            if news_only:
                arguments["category"] = "news"
                
                if days_back:
                    # Calculate the cutoff date and format it to ISO 8601 for Exa
                    start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
                    arguments["startPublishedDate"] = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Call the web_search_exa tool
            response = self._send_mcp_request(
                "tools/call",
                {
                    "name": "web_search_exa",
                    "arguments": arguments
                }
            )
            
            # Extract results from response
            result_data = response.get("result", {})
            
            # Handle different possible response formats
            if "content" in result_data:
                content = result_data["content"]
                
                # If content is a list with text content
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and "text" in content[0]:
                        content_text = content[0]["text"]
                        try:
                            # Try to parse as JSON
                            search_data = json.loads(content_text)
                        except json.JSONDecodeError:
                            # If not JSON, treat as plain text
                            return self._parse_text_results(content_text, query)
                    else:
                        search_data = content
                elif isinstance(content, str):
                    try:
                        search_data = json.loads(content)
                    except json.JSONDecodeError:
                        return self._parse_text_results(content, query)
                else:
                    search_data = content
            else:
                search_data = result_data
            
            return self._parse_search_results(search_data, max_results)
            
        except Exception as e:
            print(f"Error during blaxel-search: {e}")
            return []
    
    def _parse_search_results(self, data: Any, max_results: int) -> List[SearchResult]:
        """
        Parse search results from various possible formats.
        
        Args:
            data: Raw search result data
            max_results: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        try:
            # Handle different data structures
            if isinstance(data, dict):
                if "results" in data:
                    # Standard format with results array
                    for item in data["results"][:max_results]:
                        if isinstance(item, dict):
                            result = self._create_search_result(item)
                            if result:
                                results.append(result)
                
                elif "links" in data:
                    # Alternative format with links array
                    for item in data["links"][:max_results]:
                        if isinstance(item, dict):
                            result = self._create_search_result(item)
                            if result:
                                results.append(result)
                
                elif "url" in data:
                    # Single result format
                    result = self._create_search_result(data)
                    if result:
                        results.append(result)
            
            elif isinstance(data, list):
                # Direct list of results
                for item in data[:max_results]:
                    if isinstance(item, dict):
                        result = self._create_search_result(item)
                        if result:
                            results.append(result)
        
        except Exception as e:
            print(f"Error parsing search results: {e}")
        
        return results
    
    def _create_search_result(self, item: Dict[str, Any]) -> Optional[SearchResult]:
        """
        Create a SearchResult from a result item.
        
        Args:
            item: Dictionary containing result data
            
        Returns:
            SearchResult object or None if invalid
        """
        try:
            # Extract fields with various possible names
            title = (item.get("title") or 
                    item.get("name") or 
                    item.get("heading") or 
                    "Search Result")
            
            url = (item.get("url") or 
                  item.get("link") or 
                  item.get("href") or "")
            
            description = (item.get("description") or 
                          item.get("snippet") or 
                          item.get("summary") or 
                          item.get("content") or "")
            
            relevance_score = float(item.get("relevance_score", 0.0)) or float(item.get("score", 0.0))
            
            if url and title:
                return SearchResult(
                    title=str(title)[:200],  # Limit length
                    url=str(url),
                    description=str(description)[:300],  # Limit length
                    relevance_score=relevance_score
                )
        except Exception as e:
            print(f"Error creating search result from {item}: {e}")
        
        return None
    
    def _parse_text_results(self, text: str, query: str) -> List[SearchResult]:
        """
        Parse text-based search results.
        
        Args:
            text: Plain text results
            query: Original search query
            
        Returns:
            List of SearchResult objects
        """
        # For now, return a single result with the text
        # This could be enhanced to parse structured text
        return [SearchResult(
            title=f"Search results for: {query}",
            url="",
            description=text[:300] + ("..." if len(text) > 300 else ""),
            relevance_score=0.5
        )]


class WebSearchManager:
    """High-level manager for web searches using blaxel-search MCP."""
    
    def __init__(self, max_results_per_search: int = 10, endpoint_url: str = None, auth_token: str = None):
        """
        Initialize the WebSearchManager.
        
        Args:
            max_results_per_search: Maximum results per search query
            endpoint_url: Custom MCP endpoint URL (optional)
            auth_token: Authentication token for MCP server (optional)
        """
        self.max_results = max_results_per_search
        endpoint = endpoint_url or "https://mcp-blaxel-search-vzjx7r.bl.run/mcp"
        
        # Try to get auth token from environment if not provided
        if not auth_token:
            import os
            auth_token = os.getenv('BLAXEL_AUTH_TOKEN')
            
        self.client = BlaxelSearchMCPClient(endpoint, auth_token)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def search_for_topic(self, user_input: str, max_results: Optional[int] = None, news_only: bool = True, days_back: int = 7) -> List[SearchResult]:
        """
        Search for web content based on user input using blaxel-search MCP.
        """
        max_results = max_results or self.max_results
        print(f"Searching for: '{user_input}' (News Focus: {news_only}, Days Back: {days_back})")
        
        try:
            # Pass the new arguments down to the client
            results = self.client.search(user_input, max_results, news_only, days_back)
            print(f"Found {len(results)} relevant links")
            return results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of available tools
        """
        try:
            return self.client.list_tools()
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []
    
    def format_results(self, results: List[SearchResult]) -> str:
        """
        Format search results for display.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Formatted string of results
        """
        if not results:
            return "No relevant links found."
        
        output = []
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result.title}")
            if result.url:
                output.append(f"   URL: {result.url}")
            if result.description:
                output.append(f"   Description: {result.description}")
            if result.relevance_score > 0:
                output.append(f"   Relevance: {result.relevance_score:.2f}")
            output.append("")
        
        return "\n".join(output)


# Synchronous function for easier use
def search_for_links(user_input: str, max_results: int = 10, endpoint_url: str = None, auth_token: str = None) -> List[SearchResult]:
    """
    Search for links using blaxel-search MCP.
    
    Args:
        user_input: The user's query/topic of interest
        max_results: Maximum number of results to return
        endpoint_url: Custom MCP endpoint URL (optional)
        auth_token: Authentication token for MCP server (optional)
        
    Returns:
        List of SearchResult objects with relevant links
    """
    with WebSearchManager(max_results, endpoint_url, auth_token) as search_manager:
        return search_manager.search_for_topic(user_input, max_results, news_only=True)


# Example usage
if __name__ == "__main__":
    async def main():
        """Example usage of the web search functionality."""
        
        test_queries = [
            "artificial intelligence machine learning latest developments",
            "climate change renewable energy solutions 2024",
            "quantum computing breakthroughs recent research",
            "cryptocurrency blockchain technology trends"
        ]
        
        async with WebSearchManager(max_results_per_search=5) as search_manager:
            for query in test_queries:
                print(f"\nSearching for: {query}")
                print("-" * 50)
                
                results = await search_manager.search_for_topic(query, max_results=5, news_only=True)
                
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"{i}. {result.title}")
                        print(f"   {result.url}")
                        if result.description:
                            print(f"   {result.description[:100]}...")
                        print()
                else:
                    print("No results found.")
                
                print("=" * 50)
    
    # Run the example
    print("Web Search Example using blaxel-search MCP server")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure blaxel-search is available:")
        print("npm install -g blaxel-search")