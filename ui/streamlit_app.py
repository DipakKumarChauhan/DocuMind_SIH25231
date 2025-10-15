"""
Streamlit UI for DocuMind RAG system.
Provides interactive document upload and query interface.
"""

import streamlit as st
from pathlib import Path
import sys
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import RAGService
from src.core.logger import app_logger
from src.core.config import settings


# Page configuration
st.set_page_config(
    page_title="DocuMind - Multimodal RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .citation {
        background-color: #E3F2FD;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .source-card {
        background-color: #F5F5F5;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_rag_service():
    """Initialize RAG service (cached for performance)."""
    return RAGService()


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">📚 DocuMind</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Multimodal RAG System with Citation-Based Answers</div>',
        unsafe_allow_html=True
    )
    
    # Initialize service
    try:
        rag_service = get_rag_service()
    except Exception as e:
        st.error(f"Failed to initialize RAG service: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Upload section
        st.subheader("📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF, DOCX, or TXT files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )
        
        if st.button("Index Documents", type="primary"):
            if uploaded_files:
                with st.spinner("Indexing documents..."):
                    # Save uploaded files
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = settings.upload_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(str(file_path))
                    
                    # Index documents
                    results = rag_service.index_documents(file_paths)
                    
                    # Show results
                    success_count = sum(1 for r in results if r.status == "success")
                    st.success(f"Indexed {success_count}/{len(results)} documents")
                    
                    for result in results:
                        if result.status == "success":
                            st.write(f"✅ {result.file_name}: {result.chunks_created} chunks")
                        else:
                            st.write(f"❌ {result.file_name}: {result.error}")
            else:
                st.warning("Please upload files first")
        
        st.divider()
        
        # Query settings
        st.subheader("🔍 Query Settings")
        top_k = st.slider("Number of sources", min_value=1, max_value=10, value=5)
        rerank = st.checkbox("Enable reranking", value=True)
        
        st.divider()
        
        # System stats
        st.subheader("📊 System Stats")
        if st.button("Refresh Stats"):
            stats = rag_service.get_stats()
            st.metric("Total Chunks", stats["total_chunks"])
            st.write(f"**Model:** {stats['embedding_model'].split('/')[-1]}")
            st.write(f"**LLM:** {stats['llm_model']}")
        
        st.divider()
        
        # Clear data
        if st.button("🗑️ Clear All Data", type="secondary"):
            rag_service.clear_all()
            st.success("All data cleared")
            st.rerun()
    
    # Main content
    st.header("💬 Ask Questions")
    
    # Query input
    query = st.text_input(
        "Enter your question:",
        placeholder="What is the project timeline?",
        help="Ask questions about your uploaded documents"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("🔍 Search", type="primary")
    
    if search_button and query:
        with st.spinner("Searching and generating answer..."):
            try:
                # Execute query
                response = rag_service.query(
                    query=query,
                    top_k=top_k,
                    rerank=rerank,
                )
                
                # Display answer
                st.subheader("📝 Answer")
                st.markdown(response.answer)
                
                # Display citations
                if response.citations:
                    st.subheader("📌 Citations")
                    
                    for citation_num in sorted(response.citations):
                        if citation_num in response.citation_map:
                            source = response.citation_map[citation_num]
                            
                            with st.expander(
                                f"[{citation_num}] {source['file_name']} - Page {source['page']}",
                                expanded=False
                            ):
                                st.write(f"**Relevance:** {source['similarity_score']:.2%}")
                                st.markdown(f"```\n{source['text'][:500]}...\n```")
                
                # Display all sources
                st.subheader(f"📚 All Sources ({len(response.sources)})")
                
                for i, source in enumerate(response.sources, 1):
                    with st.expander(
                        f"{i}. {source.file_name} (Page {source.page}) - "
                        f"Score: {source.similarity_score:.2%}",
                        expanded=False
                    ):
                        st.markdown(f"**Chunk ID:** {source.chunk_id}")
                        st.markdown(f"**Text:**\n\n{source.text}")
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sources Used", response.num_sources)
                with col2:
                    st.metric("Citations", len(response.citations))
                with col3:
                    st.metric("Avg Similarity", f"{response.avg_similarity:.2%}")
                
            except Exception as e:
                st.error(f"Query failed: {e}")
                app_logger.error(f"Query error: {e}", exc_info=True)
    
    elif search_button and not query:
        st.warning("Please enter a question")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>DocuMind v0.1.0 | Built with ❤️ for hackathon</p>
            <p><em>Powered by Sentence Transformers, ChromaDB, and OpenAI</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
