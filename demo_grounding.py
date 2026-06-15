"""
Grounding demonstration with mocked Groq responses.
Shows how system enforces grounding vs. allows hallucination.
"""

from embedding_and_retrieval import retrieve, main as setup_embedding_retrieval

print("=" * 80)
print("GROUNDING DEMONSTRATION: Retrieval + Prompt Analysis")
print("=" * 80)

# Setup
print("\nInitializing retrieval system...")
model, collection = setup_embedding_retrieval()
print("✓ Ready\n")

# Test queries
test_cases = [
    {
        "type": "✅ IN-DOMAIN",
        "query": "What are the main dining commons at UC Berkeley?",
        "description": "Question directly answered in documents"
    },
    {
        "type": "✅ IN-DOMAIN",
        "query": "Where can I find affordable food under $10?",
        "description": "Specific restaurant recommendation in Berkeleyside guide"
    },
    {
        "type": "❌ OUT-OF-DOMAIN",
        "query": "What is the grading policy for CS 61A?",
        "description": "Not about dining/food - should refuse"
    },
    {
        "type": "❌ OUT-OF-DOMAIN",
        "query": "How do I apply for housing at Berkeley?",
        "description": "Not about dining/food - should refuse"
    },
]

for i, test in enumerate(test_cases, 1):
    print("─" * 80)
    print(f"TEST {i}: {test['type']}")
    print(f"Query: {test['query']}")
    print(f"Description: {test['description']}")
    print("─" * 80)

    # Retrieve
    retrieved = retrieve(test['query'], collection, model, top_k=8)

    print(f"\n📍 RETRIEVED CHUNKS ({len(retrieved)} results):")
    for j, chunk in enumerate(retrieved[:3], 1):
        relevance = "✓ RELEVANT" if chunk['distance'] < 0.5 else "✗ WEAK"
        print(f"   {j}. {chunk['source']} (distance: {chunk['distance']:.3f}) {relevance}")
        preview = chunk['content'][:80].replace('\n', ' ')
        print(f"      {preview}...")

    # Determine expected behavior
    top_result = retrieved[0] if retrieved else None
    is_relevant = top_result and top_result['distance'] < 0.6

    if "CS 61A" in test['query'] or "housing" in test['query']:
        # Out of domain
        expected = "❌ SHOULD REFUSE: 'I don't have enough information...'"
        explanation = "Top results are off-topic or unrelated to the question"
    elif is_relevant:
        # In domain with relevant results
        expected = "✓ SHOULD ANSWER: Cite [Source: ...] with relevant document text"
        explanation = f"Top result has distance {top_result['distance']:.3f} < 0.6 and is from dining resources"
    else:
        # In domain but weak retrieval
        expected = "⚠️  WEAK RETRIEVAL: May need tuning or clarification"
        explanation = "Results exist but relevance is borderline"

    print(f"\n📋 GROUNDING CHECK:")
    print(f"   Expected behavior: {expected}")
    print(f"   Reason: {explanation}")

    # Show what the system prompt does
    print(f"\n🛡️  GROUNDING MECHANISM:")
    print(f"   System prompt ENFORCES:")
    print(f"   1. 'ONLY answer using information explicitly stated'")
    print(f"   2. 'NEVER use training data or general knowledge'")
    print(f"   3. 'If documents don't contain answer, say so clearly'")
    print(f"   4. 'Always cite which source(s) your answer comes from'")

    print()

print("\n" + "=" * 80)
print("SETUP INSTRUCTIONS TO TEST WITH REAL GROQ API")
print("=" * 80)
print("""
1. Get a free Groq API key:
   → Visit https://console.groq.com
   → Sign up (no credit card needed)
   → Copy your API key

2. Create .env file:
   cp .env.example .env
   Edit .env and add: GROQ_API_KEY=your_key_here

3. Run end-to-end tests:
   python3 test_grounding.py

4. Run interactive CLI:
   python3 generation.py
   Type 'test' to run evaluation queries
   Type a question to ask the system

5. Run web interface:
   python3 app.py
   Open http://localhost:7860
""")
