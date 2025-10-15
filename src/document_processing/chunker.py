"""
Smart text chunking with sentence-aware splitting and overlap.
Implements token-based chunking with configurable overlap for better context preservation.
"""

from typing import List, Dict, Any
import re

import nltk
from nltk.tokenize import sent_tokenize
import tiktoken

from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import ChunkingError


# Ensure NLTK punkt tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    app_logger.warning("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)


class TextChunker:
    """
    Intelligent text chunking with sentence awareness and token-based sizing.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        max_chunk_size: int = None,
    ):
        """
        Initialize chunker with configuration.
        
        Args:
            chunk_size: Target chunk size in tokens (default from settings)
            chunk_overlap: Overlap size in tokens (default from settings)
            max_chunk_size: Maximum allowed chunk size (default from settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.max_chunk_size = max_chunk_size or settings.max_chunk_size
        
        # Initialize tokenizer (GPT-2 tokenizer as proxy for token counting)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            app_logger.warning("Failed to load tiktoken, using rough word-based estimation")
            self.tokenizer = None
        
        app_logger.info(
            f"Chunker initialized: chunk_size={self.chunk_size}, "
            f"overlap={self.chunk_overlap}, max={self.max_chunk_size}"
        )
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough approximation: 1 token ≈ 0.75 words
            return int(len(text.split()) * 1.33)
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks with metadata.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dicts with text, metadata, and position info
        """
        if not text or not text.strip():
            return []
        
        metadata = metadata or {}
        
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            app_logger.debug(f"Split text into {len(sentences)} sentences")
            
            chunks = []
            current_chunk = []
            current_tokens = 0
            start_char = 0
            
            for sentence in sentences:
                sentence_tokens = self.count_tokens(sentence)
                
                # If single sentence exceeds max, split it further
                if sentence_tokens > self.max_chunk_size:
                    app_logger.warning(
                        f"Sentence exceeds max chunk size ({sentence_tokens} tokens), "
                        "splitting by words"
                    )
                    # Add current chunk if exists
                    if current_chunk:
                        chunk_text = ' '.join(current_chunk)
                        chunks.append(self._create_chunk(
                            chunk_text, start_char, metadata, len(chunks)
                        ))
                        current_chunk = []
                        current_tokens = 0
                    
                    # Split long sentence
                    word_chunks = self._split_long_sentence(sentence)
                    for wc in word_chunks:
                        chunks.append(self._create_chunk(
                            wc, start_char, metadata, len(chunks)
                        ))
                        start_char += len(wc)
                    
                    continue
                
                # Check if adding sentence exceeds chunk size
                if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunk_text = ' '.join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, start_char, metadata, len(chunks)
                    ))
                    
                    # Handle overlap: keep last few sentences
                    overlap_sentences = self._get_overlap_sentences(
                        current_chunk, self.chunk_overlap
                    )
                    
                    # Calculate new start position
                    if overlap_sentences:
                        # Find where overlap starts in original text
                        overlap_text = ' '.join(overlap_sentences)
                        start_char = chunk_text.rfind(overlap_text)
                        if start_char == -1:
                            start_char = len(chunk_text)
                    else:
                        start_char += len(chunk_text)
                    
                    current_chunk = overlap_sentences
                    current_tokens = sum(self.count_tokens(s) for s in overlap_sentences)
                
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
            
            # Add final chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(self._create_chunk(
                    chunk_text, start_char, metadata, len(chunks)
                ))
            
            app_logger.info(f"Created {len(chunks)} chunks from text")
            return chunks
            
        except Exception as e:
            app_logger.error(f"Chunking failed: {e}")
            raise ChunkingError(f"Failed to chunk text: {e}") from e
    
    def _create_chunk(
        self,
        text: str,
        start_char: int,
        metadata: Dict[str, Any],
        chunk_index: int,
    ) -> Dict[str, Any]:
        """Create chunk dictionary with metadata."""
        return {
            "text": text.strip(),
            "chunk_id": chunk_index,
            "start_char": start_char,
            "end_char": start_char + len(text),
            "token_count": self.count_tokens(text),
            "char_count": len(text),
            **metadata,
        }
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_tokens: int) -> List[str]:
        """Get last N sentences that fit within overlap token count."""
        overlap_sentences = []
        total_tokens = 0
        
        # Work backwards from end
        for sentence in reversed(sentences):
            sentence_tokens = self.count_tokens(sentence)
            if total_tokens + sentence_tokens <= overlap_tokens:
                overlap_sentences.insert(0, sentence)
                total_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split a long sentence into smaller chunks by words."""
        words = sentence.split()
        chunks = []
        current = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self.count_tokens(word)
            if current_tokens + word_tokens > self.chunk_size and current:
                chunks.append(' '.join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens
        
        if current:
            chunks.append(' '.join(current))
        
        return chunks
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk an entire extracted document.
        
        Args:
            document: Document dict from TextExtractor
            
        Returns:
            List of all chunks with preserved metadata
        """
        all_chunks = []
        
        file_metadata = {
            "file_name": document["file_name"],
            "file_type": document["file_type"],
            "file_path": document["file_path"],
        }
        
        for page_data in document["content"]:
            page_metadata = {
                **file_metadata,
                "page": page_data.get("page", 1),
                "paragraph": page_data.get("paragraph"),
            }
            
            chunks = self.chunk_text(page_data["text"], page_metadata)
            all_chunks.extend(chunks)
        
        app_logger.info(
            f"Chunked document '{document['file_name']}' into {len(all_chunks)} chunks"
        )
        return all_chunks
