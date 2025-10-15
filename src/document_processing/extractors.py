"""
Document text extraction from various file formats.
Supports PDF, DOCX, and TXT files with robust error handling.
"""

from pathlib import Path
from typing import List, Dict, Any
import re

import fitz  # PyMuPDF
from docx import Document

from src.core.logger import app_logger
from src.core.exceptions import DocumentProcessingError


class TextExtractor:
    """Extract text from various document formats with metadata."""
    
    @staticmethod
    def extract_from_pdf(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from PDF with page-level metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of dicts with 'page', 'text', 'char_count' keys
            
        Raises:
            DocumentProcessingError: If extraction fails
        """
        try:
            app_logger.info(f"Extracting text from PDF: {file_path}")
            doc = fitz.open(file_path)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # Clean up text
                text = TextExtractor._clean_text(text)
                
                if text.strip():  # Only add non-empty pages
                    pages.append({
                        "page": page_num + 1,
                        "text": text,
                        "char_count": len(text),
                        "word_count": len(text.split()),
                    })
            
            doc.close()
            app_logger.info(f"Extracted {len(pages)} pages from PDF")
            return pages
            
        except Exception as e:
            app_logger.error(f"Failed to extract from PDF {file_path}: {e}")
            raise DocumentProcessingError(f"PDF extraction failed: {e}") from e
    
    @staticmethod
    def extract_from_docx(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from DOCX with paragraph-level metadata.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            List of dicts with 'paragraph', 'text', 'char_count' keys
        """
        try:
            app_logger.info(f"Extracting text from DOCX: {file_path}")
            doc = Document(file_path)
            paragraphs = []
            
            for idx, para in enumerate(doc.paragraphs):
                text = para.text
                text = TextExtractor._clean_text(text)
                
                if text.strip():
                    paragraphs.append({
                        "paragraph": idx + 1,
                        "text": text,
                        "char_count": len(text),
                        "word_count": len(text.split()),
                        "style": para.style.name if para.style else "Normal",
                    })
            
            app_logger.info(f"Extracted {len(paragraphs)} paragraphs from DOCX")
            return paragraphs
            
        except Exception as e:
            app_logger.error(f"Failed to extract from DOCX {file_path}: {e}")
            raise DocumentProcessingError(f"DOCX extraction failed: {e}") from e
    
    @staticmethod
    def extract_from_txt(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from TXT file.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            List with single dict containing full text
        """
        try:
            app_logger.info(f"Extracting text from TXT: {file_path}")
            
            # Try UTF-8 first, fallback to latin-1
            try:
                text = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                text = file_path.read_text(encoding='latin-1')
            
            text = TextExtractor._clean_text(text)
            
            return [{
                "page": 1,
                "text": text,
                "char_count": len(text),
                "word_count": len(text.split()),
            }]
            
        except Exception as e:
            app_logger.error(f"Failed to extract from TXT {file_path}: {e}")
            raise DocumentProcessingError(f"TXT extraction failed: {e}") from e
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines but preserve paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract(file_path: Path) -> Dict[str, Any]:
        """
        Extract text from file based on extension.
        
        Args:
            file_path: Path to document
            
        Returns:
            Dict with 'file_name', 'file_type', 'content' keys
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentProcessingError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        extractors = {
            '.pdf': TextExtractor.extract_from_pdf,
            '.docx': TextExtractor.extract_from_docx,
            '.txt': TextExtractor.extract_from_txt,
        }
        
        if extension not in extractors:
            raise DocumentProcessingError(
                f"Unsupported file type: {extension}. Supported: {list(extractors.keys())}"
            )
        
        content = extractors[extension](file_path)
        
        return {
            "file_name": file_path.name,
            "file_type": extension[1:],  # Remove dot
            "file_path": str(file_path),
            "content": content,
            "total_pages": len(content),
        }
