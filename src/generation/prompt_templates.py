"""
RAG prompt templates for citation-based answers.
"""

from typing import List, Dict, Any


class PromptTemplates:
    """Collection of prompt templates for RAG."""
    
    @staticmethod
    def format_sources(chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks as numbered sources.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Formatted sources string
        """
        sources = []
        
        for i, chunk in enumerate(chunks, 1):
            file_name = chunk.get("file_name", "Unknown")
            page = chunk.get("page", "N/A")
            text = chunk.get("text", "")
            
            # Truncate long text for readability
            max_len = 800  # Increased from 300 to provide more context
            if len(text) > max_len:
                text = text[:max_len] + "..."
            
            source = f'[{i}] {file_name} - Page {page}\n"{text}"'
            sources.append(source)
        
        return "\n\n".join(sources)
    
    @staticmethod
    def create_rag_system_prompt() -> str:
        """
        Create system prompt for RAG.
        
        Returns:
            System prompt instructing citation-based answering
        """
        return """You are a helpful AI assistant that answers questions based ONLY on the provided source documents.

Your task:
1. Read the sources carefully
2. Provide a comprehensive, detailed answer to the user's question
3. ALWAYS cite your sources using [1], [2], etc. notation after each statement
4. If the information is not found in the sources, clearly state: "I don't find supporting information in the provided sources."
5. Do not make up or infer information beyond what's explicitly stated in the sources

Format your answer as:
- Provide a thorough, well-explained answer to the question
- Support each claim with citations [1], [2], etc.
- Include relevant details and context from the sources
- At the end, add a "Sources used:" section listing the sources

Be detailed, precise, and helpful. Aim for comprehensive answers that fully address the question."""
    
    @staticmethod
    def create_rag_user_prompt(
        query: str,
        chunks: List[Dict[str, Any]],
    ) -> str:
        """
        Create user prompt with query and sources.
        
        Args:
            query: User's question
            chunks: Retrieved source chunks
            
        Returns:
            Formatted user prompt
        """
        sources_text = PromptTemplates.format_sources(chunks)
        
        return f"""Sources:
{sources_text}

Question: {query}

Please answer the question using only the sources provided above. Remember to cite your sources using [1], [2], etc."""
    
    @staticmethod
    def create_full_rag_prompt(
        query: str,
        chunks: List[Dict[str, Any]],
    ) -> tuple[str, str]:
        """
        Create complete RAG prompt (system + user).
        
        Args:
            query: User question
            chunks: Retrieved chunks
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = PromptTemplates.create_rag_system_prompt()
        user_prompt = PromptTemplates.create_rag_user_prompt(query, chunks)
        
        return system_prompt, user_prompt
