import json
from embedding_and_retrieval import retrieve, main as setup_embedding_retrieval

model, collection = setup_embedding_retrieval()

# Debug queries 2 and 3
debug_queries = [
    {
        "query": "What is recommended for an affordable lunch under $10 near campus?",
        "should_contain": "Cheese 'N' Stuff"
    },
    {
        "query": "Which convenience stores are listed on the Berkeley dining page?",
        "should_contain": "Bear Market, The Den, Cub Market"
    }
]

for q_dict in debug_queries:
    query = q_dict['query']
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"Looking for: {q_dict['should_contain']}")
    print(f"{'='*80}")
    
    retrieved = retrieve(query, collection, model, top_k=8)
    
    print(f"\nAll {len(retrieved)} results:")
    for i, result in enumerate(retrieved, 1):
        print(f"\n[{i}] {result['source']} (distance: {result['distance']:.4f})")
        # Check if it contains target
        contains = q_dict['should_contain'].lower() in result['content'].lower()
        status = "✓ CONTAINS TARGET" if contains else "✗ does not contain"
        print(f"    {status}")
        print(f"    Preview: {result['content'][:200]}...")

# Also check what's in chunks about these topics
print(f"\n\n{'='*80}")
print("MANUAL CHECK: All chunks with 'Cheese' or 'Bear Market'")
print(f"{'='*80}")

with open('documents/chunks.json') as f:
    chunks = json.load(f)

print(f"\nChunks containing 'Cheese':")
for chunk in chunks:
    if 'cheese' in chunk['content'].lower():
        print(f"  - Doc {chunk['doc_id']}, Chunk {chunk['chunk_index']}: {chunk['content'][:100]}...")

print(f"\nChunks containing 'Bear Market':")
for chunk in chunks:
    if 'bear market' in chunk['content'].lower():
        print(f"  - Doc {chunk['doc_id']}, Chunk {chunk['chunk_index']}: {chunk['content'][:100]}...")
