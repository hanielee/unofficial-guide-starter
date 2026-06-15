from embedding_and_retrieval import retrieve, main as setup_embedding_retrieval

model, collection = setup_embedding_retrieval()

# Check if target chunks are in top-12
debug_queries = [
    {
        "query": "What is recommended for an affordable lunch under $10 near campus?",
        "target": ["Cheese 'N' Stuff", "fresh lunch", "$10"],
        "source_contains": "Berkeleyside"
    },
    {
        "query": "Which convenience stores are listed on the Berkeley dining page?",
        "target": ["Bear Market", "The Den", "Cub Market"],
        "source_contains": "UC Berkeley Dining Locations"
    },
]

print("=" * 80)
print("CHECKING IF TARGET CHUNKS ARE IN TOP-12")
print("=" * 80)

for q_dict in debug_queries:
    query = q_dict['query']
    targets = q_dict['target']
    
    print(f"\n\nQuery: {query}")
    print(f"Looking for: {targets}")
    
    retrieved = retrieve(query, collection, model, top_k=12)
    
    # Check each result
    found_at_position = None
    for i, result in enumerate(retrieved, 1):
        any_match = any(target.lower() in result['content'].lower() for target in targets)
        if any_match:
            print(f"  ✓ FOUND at position #{i} in {result['source']}")
            print(f"    Distance: {result['distance']:.4f}")
            if not found_at_position:
                found_at_position = i
            # Show content
            for target in targets:
                if target.lower() in result['content'].lower():
                    idx = result['content'].lower().find(target.lower())
                    preview = result['content'][max(0, idx-50):min(len(result['content']), idx+100)]
                    print(f"      ...{preview}...")
    
    if not found_at_position:
        print(f"  ✗ NOT FOUND in top-12 results")
        print(f"    This is a retrieval failure - the correct chunk isn't in the results")
