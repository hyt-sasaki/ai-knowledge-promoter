"""Domain layer for MCP Server.

This package contains domain models and repository interfaces.
"""

from .models import Knowledge, SearchResult
from .repositories import KnowledgeRepository

__all__ = ["Knowledge", "SearchResult", "KnowledgeRepository"]
