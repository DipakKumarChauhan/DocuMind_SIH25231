"""
Citation parser for extracting and validating citations from LLM responses.
"""

import re
from typing import List, Dict, Any, Tuple


class CitationParser:
    """Parse and validate citations in LLM-generated answers."""
    
    @staticmethod
    def extract_citations(text: str) -> List[int]:
        """
        Extract citation numbers from text.
        
        Args:
            text: Generated answer text
            
        Returns:
            List of citation numbers found
        """
        # Match patterns like [1], [2], [10], etc.
        pattern = r'\[(\d+)\]'
        matches = re.findall(pattern, text)
        
        # Convert to integers and deduplicate
        citations = list(set(int(m) for m in matches))
        citations.sort()
        
        return citations
    
    @staticmethod
    def validate_citations(
        text: str,
        num_sources: int,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that citations are within valid range.
        
        Args:
            text: Generated answer
            num_sources: Number of source chunks available
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        citations = CitationParser.extract_citations(text)
        errors = []
        
        for citation_num in citations:
            if citation_num < 1 or citation_num > num_sources:
                errors.append(
                    f"Invalid citation [{citation_num}]: "
                    f"only {num_sources} sources available"
                )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def map_citations_to_sources(
        text: str,
        chunks: List[Dict[str, Any]],
    ) -> Dict[int, Dict[str, Any]]:
        """
        Map citation numbers to actual source chunks.
        
        Args:
            text: Generated answer with citations
            chunks: List of source chunks (in order used)
            
        Returns:
            Dict mapping citation number to chunk metadata
        """
        citations = CitationParser.extract_citations(text)
        mapping = {}
        
        for citation_num in citations:
            # Citations are 1-indexed
            if 1 <= citation_num <= len(chunks):
                chunk = chunks[citation_num - 1]
                mapping[citation_num] = {
                    "file_name": chunk.get("file_name"),
                    "page": chunk.get("page"),
                    "text": chunk.get("text"),
                    "similarity_score": chunk.get("similarity_score"),
                }
        
        return mapping
    
    @staticmethod
    def format_citation_links(
        citations_map: Dict[int, Dict[str, Any]],
    ) -> str:
        """
        Format citation map as readable reference list.
        
        Args:
            citations_map: Mapping from citation number to source info
            
        Returns:
            Formatted reference list
        """
        if not citations_map:
            return "No citations found."
        
        lines = ["References:"]
        for num in sorted(citations_map.keys()):
            source = citations_map[num]
            file_name = source.get("file_name", "Unknown")
            page = source.get("page", "N/A")
            score = source.get("similarity_score", 0.0)
            
            lines.append(
                f"[{num}] {file_name} (Page {page}) - "
                f"Relevance: {score:.2f}"
            )
        
        return "\n".join(lines)
