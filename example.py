"""
Example usage of DocuMind RAG system.
Demonstrates programmatic API usage.
"""

from pathlib import Path
from src.api import RAGService
from src.core.logger import app_logger


def example_basic_usage():
    """Basic usage example."""
    print("=" * 80)
    print("DocuMind RAG System - Basic Example")
    print("=" * 80)
    
    # Initialize service
    print("\n1. Initializing RAG service...")
    service = RAGService()
    
    # Check stats
    print("\n2. System stats:")
    stats = service.get_stats()
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Embedding model: {stats['embedding_model']}")
    print(f"   LLM model: {stats['llm_model']}")
    
    # Index documents (example - create test documents first)
    print("\n3. Indexing documents...")
    
    # Create a sample document
    test_dir = Path("data/uploads")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = test_dir / "sample_doc.txt"
    test_file.write_text("""
Project Timeline Document

Project Name: DocuMind RAG System
Start Date: October 1, 2025
End Date: October 15, 2025

Milestones:
- Week 1: Architecture design and setup
- Week 2: Core development (document processing, embeddings, vector store)
- Week 3: RAG pipeline and LLM integration
- Week 4: UI development and testing

Team Members:
- Alice: Lead Developer
- Bob: ML Engineer
- Charlie: UI/UX Designer

Budget: $50,000
Status: On Track
""")
    
    # Index the document
    results = service.index_documents([str(test_file)])
    
    for result in results:
        print(f"   ✓ Indexed: {result.file_name}")
        print(f"     Chunks: {result.chunks_created}")
        print(f"     Pages: {result.total_pages}")
    
    # Query the system
    print("\n4. Querying the system...")
    queries = [
        "What is the project timeline?",
        "Who are the team members?",
        "What is the budget?",
    ]
    
    for query in queries:
        print(f"\n   Q: {query}")
        response = service.query(query, top_k=3)
        
        print(f"   A: {response.answer}")
        print(f"   Sources: {response.num_sources}, Citations: {len(response.citations)}")
        
        if response.citations:
            print(f"   Used sources:")
            for num in response.citations[:2]:  # Show first 2
                if num in response.citation_map:
                    source = response.citation_map[num]
                    print(f"     [{num}] {source['file_name']} - Page {source['page']}")
    
    print("\n" + "=" * 80)
    print("Example complete!")
    print("=" * 80)


def example_with_filters():
    """Example using metadata filters."""
    print("\n\nAdvanced Example: Filtering by Document")
    print("=" * 80)
    
    service = RAGService()
    
    # Query with filters
    response = service.query(
        query="What is the status?",
        top_k=5,
        filters={"file_name": "sample_doc.txt"}  # Only search in specific file
    )
    
    print(f"Query: What is the status?")
    print(f"Answer: {response.answer}")
    print(f"Sources: {[s.file_name for s in response.sources]}")


if __name__ == "__main__":
    try:
        example_basic_usage()
        example_with_filters()
    except Exception as e:
        print(f"\nError: {e}")
        app_logger.error(f"Example failed: {e}", exc_info=True)
        print("\nMake sure to:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run setup: python setup.py")
        print("3. Set OpenAI API key in .env file")
