#!/usr/bin/env python3
"""
System validation script: Checks all components without requiring Groq API.
Run this to verify everything is set up correctly.
"""

import sys
import os
from pathlib import Path

def check_files():
    """Check that all required files exist."""
    print("\n📋 CHECKING PROJECT FILES")
    print("─" * 60)

    required_files = {
        "ingestion.py": "Document ingestion & chunking",
        "embedding_and_retrieval.py": "Embedding & retrieval engine",
        "generation.py": "LLM generation (requires API key)",
        "app.py": "Gradio web interface",
        "documents/chunks.json": "Embedded chunks",
        "documents/raw_documents.json": "Cleaned documents",
        ".env.example": "API key template",
        "requirements.txt": "Dependencies",
    }

    all_exist = True
    for file, description in required_files.items():
        path = Path(file)
        status = "✓" if path.exists() else "✗"
        print(f"{status} {file:35s} {description}")
        if not path.exists():
            all_exist = False

    return all_exist

def check_dependencies():
    """Check that Python dependencies are installed."""
    print("\n📦 CHECKING DEPENDENCIES")
    print("─" * 60)

    required = {
        "requests": "HTTP requests",
        "beautifulsoup4": "HTML parsing",
        "sentence_transformers": "Embeddings",
        "chromadb": "Vector store",
        "langchain_text_splitters": "Chunking",
        "gradio": "Web interface",
        "groq": "LLM API (Groq)",
        "python-dotenv": "Environment variables",
    }

    all_installed = True
    for module, description in required.items():
        try:
            __import__(module.replace("_", "-").replace("-", "_"))
            print(f"✓ {module:30s} {description}")
        except ImportError:
            print(f"✗ {module:30s} {description}")
            all_installed = False

    return all_installed

def check_env():
    """Check .env configuration."""
    print("\n🔐 CHECKING ENVIRONMENT SETUP")
    print("─" * 60)

    env_path = Path(".env")

    if env_path.exists():
        print("✓ .env file exists")
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")
        if api_key and api_key != "your_key_here":
            print("✓ GROQ_API_KEY is set (will work for generation)")
            return True
        else:
            print("✗ GROQ_API_KEY not set or uses placeholder")
            return False
    else:
        print("✗ .env file not found")
        print(f"  → Run: cp .env.example .env")
        print(f"  → Then add your GROQ_API_KEY from https://console.groq.com")
        return False

def check_data():
    """Check that documents have been ingested."""
    print("\n📚 CHECKING INGESTED DATA")
    print("─" * 60)

    try:
        import json

        with open("documents/chunks.json") as f:
            chunks = json.load(f)

        with open("documents/raw_documents.json") as f:
            docs = json.load(f)

        print(f"✓ {len(chunks)} chunks ingested")
        print(f"✓ {len(docs)} documents processed")

        chunk_sizes = [c['char_count'] for c in chunks]
        print(f"  Chunk size: {min(chunk_sizes)}-{max(chunk_sizes)} chars")
        print(f"  Average: {sum(chunk_sizes)//len(chunk_sizes)} chars")

        return True
    except Exception as e:
        print(f"✗ Error checking data: {e}")
        return False

def check_vector_store():
    """Check if embeddings are loaded in ChromaDB."""
    print("\n🔍 CHECKING VECTOR STORE")
    print("─" * 60)

    try:
        from chromadb import Client
        from chromadb.config import Settings

        settings = Settings(
            persist_directory="documents/chroma_db",
            anonymized_telemetry=False,
        )
        client = Client(settings)
        collection = client.get_or_create_collection(
            name="dining_chunks",
            metadata={"hnsw:space": "cosine"}
        )

        count = collection.count()
        if count > 0:
            print(f"✓ ChromaDB loaded with {count} embeddings")
            return True
        else:
            print("✗ ChromaDB exists but is empty (need to run embedding_and_retrieval.py)")
            return False
    except Exception as e:
        print(f"✗ Error checking ChromaDB: {e}")
        return False

def main():
    print("=" * 60)
    print("🍽️  UC BERKELEY DINING GUIDE — SYSTEM VALIDATION")
    print("=" * 60)

    results = {}

    results["files"] = check_files()
    results["dependencies"] = check_dependencies()
    results["data"] = check_data()
    results["vector_store"] = check_vector_store()
    results["env"] = check_env()

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n✅ SYSTEM READY!")
        print("\nNext steps:")
        print("  1. Test grounding: python3 demo_grounding.py")
        print("  2. Test retrieval: python3 test_retrieval.py")
        print("  3. Launch web UI: python3 app.py")
        print("     (Then open http://localhost:7860)")
        return 0
    else:
        print("\n⚠️  SYSTEM INCOMPLETE")

        if not results["env"]:
            print("\n🔑 PRIORITY: Set up your Groq API key")
            print("   1. Visit https://console.groq.com")
            print("   2. Sign up (free, no credit card)")
            print("   3. Copy your API key")
            print("   4. Add to .env: GROQ_API_KEY=your_key")

        if not results["vector_store"]:
            print("\n📊 PRIORITY: Create embeddings")
            print("   Run: python3 embedding_and_retrieval.py")

        return 1

if __name__ == "__main__":
    sys.exit(main())
