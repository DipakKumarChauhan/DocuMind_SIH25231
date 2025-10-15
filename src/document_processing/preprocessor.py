"""
Text preprocessing and normalization utilities.
"""

import re
from typing import Optional


class TextPreprocessor:
    """Text cleaning and normalization utilities."""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace while preserving paragraph breaks."""
        # Replace multiple spaces with single space
        text = re.sub(r'[^\S\n]+', ' ', text)
        # Replace 3+ newlines with 2 (preserve paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def remove_special_characters(
        text: str,
        keep_punctuation: bool = True,
    ) -> str:
        """Remove special characters while optionally keeping punctuation."""
        if keep_punctuation:
            # Keep alphanumeric, spaces, and basic punctuation
            text = re.sub(r'[^a-zA-Z0-9\s.,!?;:()\-\'"]+', '', text)
        else:
            # Keep only alphanumeric and spaces
            text = re.sub(r'[^a-zA-Z0-9\s]+', '', text)
        return text
    
    @staticmethod
    def clean_text(
        text: str,
        normalize_ws: bool = True,
        remove_special: bool = False,
    ) -> str:
        """
        Apply multiple cleaning operations.
        
        Args:
            text: Input text
            normalize_ws: Normalize whitespace
            remove_special: Remove special characters
            
        Returns:
            Cleaned text
        """
        if normalize_ws:
            text = TextPreprocessor.normalize_whitespace(text)
        
        if remove_special:
            text = TextPreprocessor.remove_special_characters(text)
        
        return text.strip()
