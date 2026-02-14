"""
BingusSpoingus - AI-powered podcast generation from user text.
"""

from .web_search import WebSearchManager, SearchResult, search_for_links

__all__ = ['WebSearchManager', 'SearchResult', 'search_for_links']
__version__ = '0.1.0'