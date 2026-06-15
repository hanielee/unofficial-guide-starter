"""
Generation module for UC Berkeley Dining Guide RAG.
Uses Groq API (llama-3.3-70b-versatile) to generate answers from retrieved chunks.
"""

from embedding_and_retrieval import retrieve, main as setup_embedding_retrieval
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration from planning.md
GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 12


def generate_answer(query, retrieved_chunks, client):
    """
    Generate an answer using Groq LLM based on retrieved chunks.

    Args:
        query: User's question
        retrieved_chunks: List of retrieved chunk dicts from retrieval()
        client: Groq client

    Returns:
        Generated answer string
    """

    # Format retrieved chunks as context
    context = "\n\n---\n\n".join([
        f"[Source: {chunk['source']}, Chunk {chunk['chunk_index']}]\n{chunk['content']}"
        for chunk in retrieved_chunks
    ])

    # Create the prompt with STRICT grounding enforcement
    system_prompt = """You are a helpful guide for UC Berkeley students about dining and food options on campus.

CRITICAL GROUNDING RULES (you MUST follow these):
1. ONLY answer using information explicitly stated in the provided documents
2. NEVER use your training data or general knowledge
3. NEVER make assumptions or infer information not directly stated
4. If a question cannot be answered from the documents, say: "I don't have enough information about that in the available documents."
5. Always cite which source(s) your answer comes from using the [Source: ...] labels
6. Be specific and concrete - quote or paraphrase the document text
7. Keep answers concise and focused

If you are unsure whether something is in the documents, it is NOT. Err on the side of saying you don't know."""

    user_prompt = f"""Answer the question ONLY using the following context. Do not use any outside knowledge.

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {query}

ANSWER (using only the context above, with source citations):"""

    # Call Groq API
    message = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    return message.choices[0].message.content


def answer_question(query, model, collection, client):
    """
    Full RAG pipeline: retrieve chunks and generate answer.

    Args:
        query: User's question
        model: Sentence transformer model
        collection: ChromaDB collection
        client: Groq client

    Returns:
        Dict with answer, retrieved chunks, and metadata
    """

    # Retrieve
    retrieved = retrieve(query, collection, model, top_k=TOP_K)

    # Generate
    answer = generate_answer(query, retrieved, client)

    return {
        "query": query,
        "answer": answer,
        "retrieved_chunks": retrieved,
        "num_sources": len(set(c['source'] for c in retrieved)),
    }


def main():
    """Interactive CLI for testing the full RAG pipeline."""
    print("=" * 80)
    print("UC BERKELEY DINING GUIDE — RAG SYSTEM")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GROQ_API_KEY not set in .env file")
        print("   Please add your Groq API key to .env:")
        print("   GROQ_API_KEY=your_key_here")
        return

    print("\nInitializing...")

    # Setup embedding and retrieval
    model, collection = setup_embedding_retrieval()

    # Setup Groq client
    client = Groq(api_key=api_key)
    print("✓ Groq client initialized")

    print("\n" + "=" * 80)
    print("Ready to answer questions about UC Berkeley dining!")
    print("Type 'quit' to exit, 'test' to run evaluation queries")
    print("=" * 80 + "\n")

    # Test evaluation queries
    evaluation_queries = [
        "What are the names of UC Berkeley's main dining commons?",
        "What is recommended for an affordable lunch under $10 near campus?",
        "Which convenience stores are listed on the Berkeley dining page?",
    ]

    while True:
        user_input = input("\n🍽️  Ask about Berkeley dining: ").strip()

        if user_input.lower() == "quit":
            print("\nGoodbye!")
            break

        if user_input.lower() == "test":
            print("\nRunning evaluation queries...\n")
            for i, query in enumerate(evaluation_queries, 1):
                print(f"\n{'='*80}")
                print(f"Test {i}: {query}")
                print(f"{'='*80}")

                result = answer_question(query, model, collection, client)

                print(f"\n📝 Answer:")
                print(result["answer"])

                print(f"\n📍 Sources ({result['num_sources']} unique):")
                for chunk in result["retrieved_chunks"][:3]:
                    print(f"   • {chunk['source']} (distance: {chunk['distance']:.3f})")
            continue

        if not user_input:
            continue

        print(f"\n🔍 Retrieving relevant chunks...")
        result = answer_question(user_input, model, collection, client)

        print(f"\n📝 Answer:")
        print(result["answer"])

        print(f"\n📍 Top sources ({result['num_sources']} unique):")
        for chunk in result["retrieved_chunks"][:3]:
            preview = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
            print(f"   • {chunk['source']} (distance: {chunk['distance']:.3f})")
            print(f"     {preview}")


if __name__ == "__main__":
    main()
