"""
Command-line interface for DocuMind RAG system.
"""

import argparse
from pathlib import Path
import sys

from src.api import RAGService
from src.core.logger import app_logger


def index_command(args):
    """Handle index command."""
    service = RAGService()
    
    files = args.files
    if args.directory:
        # Index all files in directory
        directory = Path(args.directory)
        files = list(directory.glob("*.pdf")) + \
                list(directory.glob("*.docx")) + \
                list(directory.glob("*.txt"))
        files = [str(f) for f in files]
    
    if not files:
        print("No files to index")
        return
    
    print(f"Indexing {len(files)} files...")
    results = service.index_documents(files)
    
    success = sum(1 for r in results if r.status == "success")
    print(f"\nIndexed {success}/{len(results)} documents successfully")
    
    for result in results:
        if result.status == "success":
            print(f"  ✓ {result.file_name}: {result.chunks_created} chunks")
        else:
            print(f"  ✗ {result.file_name}: {result.error}")


def query_command(args):
    """Handle query command."""
    service = RAGService()
    
    query = args.query
    print(f"\nQuery: {query}\n")
    
    response = service.query(query, top_k=args.top_k)
    
    print("Answer:")
    print("=" * 80)
    print(response.answer)
    print("=" * 80)
    
    if response.citations:
        print(f"\n📌 Citations ({len(response.citations)}):")
        for num in sorted(response.citations):
            if num in response.citation_map:
                source = response.citation_map[num]
                print(f"  [{num}] {source['file_name']} (Page {source['page']}) - "
                      f"Score: {source['similarity_score']:.2%}")
    
    print(f"\n📊 Stats: {response.num_sources} sources, "
          f"avg similarity: {response.avg_similarity:.2%}")


def stats_command(args):
    """Handle stats command."""
    service = RAGService()
    stats = service.get_stats()
    
    print("\n📊 System Statistics")
    print("=" * 50)
    print(f"Total Chunks:      {stats['total_chunks']}")
    print(f"Collection:        {stats['collection_name']}")
    print(f"Embedding Model:   {stats['embedding_model']}")
    print(f"Vector DB:         {stats['vector_db_type']}")
    print(f"LLM Model:         {stats['llm_model']}")
    print("=" * 50)


def clear_command(args):
    """Handle clear command."""
    if not args.confirm:
        response = input("Are you sure you want to clear all data? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled")
            return
    
    service = RAGService()
    service.clear_all()
    print("✓ All data cleared")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DocuMind - Multimodal RAG System CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index documents")
    index_parser.add_argument(
        "files",
        nargs="*",
        help="Files to index"
    )
    index_parser.add_argument(
        "-d", "--directory",
        help="Index all supported files in directory"
    )
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query indexed documents")
    query_parser.add_argument("query", help="Search query")
    query_parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=5,
        help="Number of sources to retrieve"
    )
    
    # Stats command
    subparsers.add_parser("stats", help="Show system statistics")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear all indexed data")
    clear_parser.add_argument(
        "-y", "--confirm",
        action="store_true",
        help="Skip confirmation"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "index":
            index_command(args)
        elif args.command == "query":
            query_command(args)
        elif args.command == "stats":
            stats_command(args)
        elif args.command == "clear":
            clear_command(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        app_logger.error(f"CLI error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
