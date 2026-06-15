"""
Embedding and retrieval pipeline for UC Berkeley Dining Guide.
Embeds chunks with all-MiniLM-L6-v2 and loads into ChromaDB.
Provides retrieval function for RAG pipeline.
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


# Configuration from planning.md
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 12  # Increased from 8 to retrieve more context, rank better results higher


def load_chunks(chunks_file="documents/chunks.json"):
    """Load chunks from JSON file."""
    with open(chunks_file) as f:
        chunks = json.load(f)
    return chunks


def setup_chromadb(db_path="documents/chroma_db"):
    """Initialize ChromaDB client and collection."""
    settings = Settings(
        persist_directory=db_path,
        anonymized_telemetry=False,
    )
    client = chromadb.Client(settings)

    # Create or get collection
    collection = client.get_or_create_collection(
        name="dining_chunks",
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity
    )

    return client, collection


def embed_and_store_chunks(chunks, collection, model):
    """
    Embed all chunks and store in ChromaDB with metadata.

    Args:
        chunks: List of chunk dicts
        collection: ChromaDB collection
        model: SentenceTransformer model
    """
    print(f"\nEmbedding {len(chunks)} chunks with {EMBEDDING_MODEL}...")

    # Prepare data for ChromaDB
    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{chunk['doc_id']}_{chunk['chunk_index']}"
        ids.append(chunk_id)
        documents.append(chunk['content'])

        # Metadata for attribution
        metadata = {
            "source": chunk['doc_name'],
            "doc_id": str(chunk['doc_id']),
            "chunk_index": str(chunk['chunk_index']),
            "char_count": str(chunk['char_count']),
        }
        metadatas.append(metadata)

    # Embed all chunks at once
    embeddings = model.encode(documents, show_progress_bar=True)

    # Add to ChromaDB
    print(f"Storing {len(chunks)} embeddings in ChromaDB...")
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas,
    )

    print(f"✓ Stored {len(chunks)} chunks")
    return collection


def retrieve(query, collection, model, top_k=TOP_K):
    """
    Retrieve top-k most relevant chunks for a query.

    Args:
        query: Query string
        collection: ChromaDB collection
        model: SentenceTransformer model
        top_k: Number of chunks to retrieve

    Returns:
        List of dicts with chunk content, source, and distance score
    """
    # Embed the query
    query_embedding = model.encode([query])[0].tolist()

    # Retrieve from ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    retrieved = []
    if results['documents'] and len(results['documents']) > 0:
        for i, doc in enumerate(results['documents'][0]):
            retrieved.append({
                'content': doc,
                'source': results['metadatas'][0][i]['source'],
                'doc_id': results['metadatas'][0][i]['doc_id'],
                'chunk_index': results['metadatas'][0][i]['chunk_index'],
                'distance': results['distances'][0][i],  # Cosine distance (0 = identical, 1 = opposite)
            })

    return retrieved


def main():
    """Main embedding and retrieval setup."""
    print("=" * 80)
    print("EMBEDDING AND RETRIEVAL SETUP")
    print("=" * 80)

    # Load model
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"✓ Model loaded (dimension: {model.get_sentence_embedding_dimension()})")

    # Load chunks
    print(f"\nLoading chunks...")
    chunks = load_chunks()
    print(f"✓ Loaded {len(chunks)} chunks")

    # Setup ChromaDB
    print(f"\nInitializing ChromaDB...")
    client, collection = setup_chromadb()
    print(f"✓ ChromaDB ready")

    # Check if already embedded (optional: skip if collection is not empty)
    try:
        existing_count = collection.count()
        if existing_count > 0:
            print(f"\n⚠️  Collection already has {existing_count} chunks")
            print("   Skipping embedding (delete documents/chroma_db to re-embed)")
            return model, collection
    except:
        pass

    # Embed and store chunks
    collection = embed_and_store_chunks(chunks, collection, model)

    print("\n" + "=" * 80)
    print("✓ EMBEDDING COMPLETE — Ready for retrieval testing")
    print("=" * 80)

    return model, collection


if __name__ == "__main__":
    model, collection = main()
