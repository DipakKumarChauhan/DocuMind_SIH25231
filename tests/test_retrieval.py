"""
Tests for retrieval functionality.
"""

import pytest
from src.retrieval import Retriever
from src.core.exceptions import RetrievalError


def test_empty_query_raises_error():
    """Test that empty query raises error."""
    retriever = Retriever()
    
    with pytest.raises(RetrievalError):
        retriever.retrieve("")


# Note: More comprehensive tests would require mocking ChromaDB
# or setting up a test database
