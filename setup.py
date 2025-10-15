"""
Setup script for quick initialization.
Downloads NLTK data and creates necessary directories.
"""

import nltk
from pathlib import Path
from src.core.config import settings
from src.core.logger import app_logger


def setup():
    """Initialize DocuMind system."""
    print("🚀 Setting up DocuMind...")
    
    # Download NLTK data
    print("\n📦 Downloading NLTK data...")
    try:
        nltk.download('punkt', quiet=True)
        print("  ✓ NLTK punkt tokenizer downloaded")
    except Exception as e:
        print(f"  ⚠ NLTK download warning: {e}")
    
    # Create directories
    print("\n📁 Creating directories...")
    directories = [
        settings.upload_dir,
        settings.cache_dir,
        settings.chroma_persist_dir,
        settings.log_file.parent,
        Path("data/uploads"),
        Path("data/cache"),
        Path("data/vectordb"),
        Path("logs"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # Create .env if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚙️  Creating .env file...")
        env_example = Path(".env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("  ✓ .env created from .env.example")
            print("  ⚠️  Please edit .env and add your OpenAI API key")
        else:
            print("  ⚠️  .env.example not found")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env and add your OpenAI API key")
    print("2. Run: streamlit run ui/streamlit_app.py")
    print("   or use CLI: python cli.py --help")


if __name__ == "__main__":
    setup()
