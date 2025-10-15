"""
Tests for text extractors.
"""

import pytest
from pathlib import Path
from src.document_processing import TextExtractor
from src.core.exceptions import DocumentProcessingError


def test_extract_from_txt(tmp_path):
    """Test text extraction from TXT file."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_content = "This is a test document.\nIt has multiple lines."
    test_file.write_text(test_content)
    
    # Extract
    result = TextExtractor.extract(test_file)
    
    assert result["file_name"] == "test.txt"
    assert result["file_type"] == "txt"
    assert len(result["content"]) == 1
    assert "test document" in result["content"][0]["text"]


def test_extract_unsupported_format(tmp_path):
    """Test that unsupported formats raise error."""
    test_file = tmp_path / "test.xyz"
    test_file.write_text("content")
    
    with pytest.raises(DocumentProcessingError):
        TextExtractor.extract(test_file)


def test_extract_nonexistent_file():
    """Test that nonexistent files raise error."""
    with pytest.raises(DocumentProcessingError):
        TextExtractor.extract(Path("nonexistent.pdf"))
