"""
Tests for text chunker.
"""

import pytest
from src.document_processing import TextChunker


def test_chunk_text_basic():
    """Test basic text chunking."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    
    text = " ".join([f"Sentence {i}." for i in range(20)])
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("chunk_id" in chunk for chunk in chunks)


def test_chunk_text_with_metadata():
    """Test chunking with metadata preservation."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    
    text = "This is a test. " * 10
    metadata = {"file_name": "test.txt", "page": 1}
    
    chunks = chunker.chunk_text(text, metadata)
    
    assert all(chunk["file_name"] == "test.txt" for chunk in chunks)
    assert all(chunk["page"] == 1 for chunk in chunks)


def test_empty_text():
    """Test that empty text returns empty chunks."""
    chunker = TextChunker()
    chunks = chunker.chunk_text("")
    
    assert chunks == []
