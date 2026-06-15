"""
Test retrieval with evaluation queries from planning.md.
Evaluates retrieval quality before moving to generation stage.
"""

from embedding_and_retrieval import main as setup_embedding_retrieval, retrieve
import json


EVALUATION_QUERIES = [
    {
        "id": 1,
        "query": "What are the names of UC Berkeley's main dining commons?",
        "expected": "Café 3, Clark Kerr, Crossroads, and Foothill"
    },
    {
        "id": 2,
        "query": "What is recommended for an affordable lunch under $10 near campus?",
        "expected": "Cheese 'N' Stuff - a fresh lunch for less than $10"
    },
    {
        "id": 3,
        "query": "Which convenience stores are listed on the Berkeley dining page?",
        "expected": "Bear Market, CKCub, Cub Market, The Den, Pizzeria 1868"
    },
    {
        "id": 4,
        "query": "What types of food resources does UC Berkeley's Foodscape Map display?",
        "expected": "Food resources, groceries, food pantries, and dining locations"
    },
    {
        "id": 5,
        "query": "What resources does the Basic Needs Center offer to help students afford food?",
        "expected": "CalFresh support, food pantry, emergency food relief"
    },
]


def print_chunk_preview(content, max_chars=400):
    """Print a preview of chunk content."""
    preview = content[:max_chars]
    if len(content) > max_chars:
        preview += "\n..."
    return preview


def evaluate_retrieval(retrieved, query_expected):
    """
    Evaluate if retrieved chunks are relevant to the query.

    Returns: quality score and reasoning
    """
    if not retrieved:
        return "FAIL", "No chunks retrieved"

    top_result = retrieved[0]
    content_lower = top_result['content'].lower()
    expected_lower = query_expected.lower()

    # Check for keyword overlap
    expected_keywords = set(expected_lower.split())
    # Remove common words
    expected_keywords = {w for w in expected_keywords if len(w) > 3}

    content_keywords = set(content_lower.split())
    overlap = len(expected_keywords & content_keywords)

    distance = top_result['distance']

    # Heuristic evaluation
    if distance < 0.3 and overlap > 0:
        return "EXCELLENT", f"High relevance (distance: {distance:.3f}, overlap: {overlap} keywords)"
    elif distance < 0.5 and overlap > 0:
        return "GOOD", f"Relevant (distance: {distance:.3f}, overlap: {overlap} keywords)"
    elif distance < 0.7:
        return "FAIR", f"Somewhat relevant (distance: {distance:.3f})"
    else:
        return "POOR", f"Low relevance (distance: {distance:.3f})"


def test_retrieval():
    """Test retrieval with evaluation queries."""
    print("=" * 80)
    print("RETRIEVAL QUALITY TEST")
    print("=" * 80)

    # Setup
    model, collection = setup_embedding_retrieval()

    print("\n" + "=" * 80)
    print("TESTING WITH EVALUATION QUERIES")
    print("=" * 80)

    results_summary = []

    for query_test in EVALUATION_QUERIES:
        query_id = query_test['id']
        query = query_test['query']
        expected = query_test['expected']

        print(f"\n{'─' * 80}")
        print(f"QUERY {query_id}: {query}")
        print(f"Expected answer: {expected}")
        print(f"{'─' * 80}")

        # Retrieve
        retrieved = retrieve(query, collection, model, top_k=12)

        if not retrieved:
            print("❌ NO RESULTS RETRIEVED")
            results_summary.append((query_id, "FAIL", "No retrieval"))
            continue

        # Print top 3 results
        for i, result in enumerate(retrieved[:3]):
            print(f"\n[{i+1}] Source: {result['source']} (Chunk {result['chunk_index']})")
            print(f"    Distance: {result['distance']:.4f}")
            print(f"\n    Content preview:")
            preview = print_chunk_preview(result['content'], 300)
            for line in preview.split('\n'):
                print(f"    {line}")

        # Evaluate
        quality, reasoning = evaluate_retrieval(retrieved, expected)
        print(f"\n>>> EVALUATION: {quality}")
        print(f"    {reasoning}")

        results_summary.append((query_id, quality, retrieved[0]['source'] if retrieved else "N/A"))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    quality_scores = {"EXCELLENT": 0, "GOOD": 0, "FAIR": 0, "POOR": 0, "FAIL": 0}

    for query_id, quality, source in results_summary:
        quality_scores[quality] += 1
        status_icon = {
            "EXCELLENT": "✅",
            "GOOD": "✅",
            "FAIR": "⚠️ ",
            "POOR": "❌",
            "FAIL": "❌"
        }[quality]
        print(f"  {status_icon} Query {query_id}: {quality:10s} (source: {source})")

    print(f"\nOverall:")
    print(f"  Excellent: {quality_scores['EXCELLENT']}")
    print(f"  Good:      {quality_scores['GOOD']}")
    print(f"  Fair:      {quality_scores['FAIR']}")
    print(f"  Poor:      {quality_scores['POOR']}")
    print(f"  Failed:    {quality_scores['FAIL']}")

    success_rate = (quality_scores['EXCELLENT'] + quality_scores['GOOD']) / len(EVALUATION_QUERIES)
    print(f"\nSuccess rate (Excellent + Good): {success_rate:.0%}")

    if success_rate >= 0.8:
        print("\n✅ RETRIEVAL QUALITY: READY FOR GENERATION STAGE")
    elif success_rate >= 0.6:
        print("\n⚠️  RETRIEVAL QUALITY: ACCEPTABLE, but consider tuning")
    else:
        print("\n❌ RETRIEVAL QUALITY: NEEDS IMPROVEMENT before generation")


if __name__ == "__main__":
    test_retrieval()
