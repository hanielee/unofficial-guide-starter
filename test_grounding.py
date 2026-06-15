"""
End-to-end grounding test: verify system doesn't hallucinate outside document scope.
"""

from generation import answer_question
from embedding_and_retrieval import main as setup_embedding_retrieval
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ ERROR: GROQ_API_KEY not set in .env")
    exit(1)

print("=" * 80)
print("GROUNDING TEST: End-to-End RAG Pipeline")
print("=" * 80)

# Setup
print("\nInitializing system...")
model, collection = setup_embedding_retrieval()
client = Groq(api_key=api_key)
print("✓ Ready\n")

# Test cases: IN-DOMAIN (should answer) vs OUT-OF-DOMAIN (should refuse)
test_cases = [
    {
        "type": "IN-DOMAIN",
        "query": "What are the main dining commons at UC Berkeley?",
        "description": "Should retrieve and answer from official dining page"
    },
    {
        "type": "IN-DOMAIN",
        "query": "Where can I find affordable food under $10 near campus?",
        "description": "Should cite Berkeleyside Cheese 'N' Stuff recommendation"
    },
    {
        "type": "OUT-OF-DOMAIN",
        "query": "What is the grading policy for CS 61A at UC Berkeley?",
        "description": "Should refuse - NOT about dining/food resources"
    },
    {
        "type": "OUT-OF-DOMAIN",
        "query": "How do I apply for housing at UC Berkeley?",
        "description": "Should refuse - NOT about dining/food resources"
    },
]

for i, test in enumerate(test_cases, 1):
    print("─" * 80)
    print(f"TEST {i}: {test['type']}")
    print(f"Query: {test['query']}")
    print(f"Expected: {test['description']}")
    print("─" * 80)

    result = answer_question(test['query'], model, collection, client)

    print(f"\n📝 ANSWER:")
    print(result['answer'])

    print(f"\n📍 TOP 2 SOURCES RETRIEVED:")
    for j, chunk in enumerate(result['retrieved_chunks'][:2], 1):
        print(f"   {j}. {chunk['source']} (distance: {chunk['distance']:.3f})")

    # Check grounding
    is_grounded = (
        "don't have" in result['answer'].lower() or
        "insufficient" in result['answer'].lower() or
        "not enough" in result['answer'].lower() or
        "[source:" in result['answer'].lower()
    )

    if test['type'] == "IN-DOMAIN" and is_grounded:
        status = "✓ GROUNDED (cites sources)"
    elif test['type'] == "OUT-OF-DOMAIN" and "don't have" in result['answer'].lower():
        status = "✓ GROUNDED (refuses out-of-domain)"
    else:
        status = "⚠️  CHECK: May not be properly grounded"

    print(f"\n{status}\n")

print("\n" + "=" * 80)
print("GROUNDING TEST COMPLETE")
print("=" * 80)
print("\nInterpretation:")
print("  ✓ IN-DOMAIN queries should cite [Source: ...] or include direct quotes")
print("  ✓ OUT-OF-DOMAIN queries should say 'don't have enough information'")
print("  ❌ If OUT-OF-DOMAIN returns plausible-sounding answer without citing")
print("     documents, grounding has failed (LLM used training knowledge)")
