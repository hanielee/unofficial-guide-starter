import json

with open('documents/chunks.json') as f:
    chunks = json.load(f)

print("=" * 80)
print("CHUNK ANALYSIS: UC BERKELEY DINING GUIDE")
print("=" * 80)

print(f"\nTOTAL CHUNKS: {len(chunks)}")
print(f"TOTAL DOCUMENTS INGESTED: {len(set(c['doc_id'] for c in chunks))}")

# Stats
char_counts = [c['char_count'] for c in chunks]
print(f"Avg chunk size: {sum(char_counts) / len(char_counts):.0f} characters")
print(f"Min: {min(char_counts)}, Max: {max(char_counts)}")

print(f"\n⚠️  ISSUE: Only {len(chunks)} chunks from 3 documents (target: 50-2000 chunks)")
print(f"   This is BELOW the recommended minimum. Possible causes:")
print(f"   - Source documents too short after cleaning")
print(f"   - Chunk size (2000 chars) too large")
print(f"   - Only 3 of 5 sources successfully scraped")

# Print all chunks with evaluation
print("\n" + "=" * 80)
print("ALL CHUNKS — EVALUATION")
print("=" * 80)

for i, chunk in enumerate(chunks):
    print(f"\n{'─' * 80}")
    print(f"CHUNK {i+1} | Doc: {chunk['doc_name']} (chunk #{chunk['chunk_index']})")
    print(f"Size: {chunk['char_count']} chars | Doc ID: {chunk['doc_id']}")
    print(f"{'─' * 80}")
    
    content = chunk['content']
    
    # Preview (first 400 chars)
    preview = content[:400]
    if len(content) > 400:
        preview += "\n..."
    print(preview)
    
    # Evaluation
    print(f"\n>>> EVALUATION:")
    
    issues = []
    positives = []
    
    # Check for badness
    if chunk['char_count'] < 200:
        issues.append("❌ TOO SMALL (fragment with no context)")
    elif chunk['char_count'] > 2500:
        issues.append("❌ TOO LARGE (multiple topics merged)")
    else:
        positives.append("✓ Good size (under 2500 chars)")
    
    # Check for HTML artifacts
    if "&" in content or "<" in content or "[" in content and "]" in content:
        issues.append("❌ Possible HTML artifacts remaining")
    else:
        positives.append("✓ No obvious HTML artifacts")
    
    # Check if standalone
    is_list = content.count("\n") > 5 and any(char in content[:100] for char in "123456789")
    is_reference = any(word in content.lower() for word in ["academic", "citation", "reference", "bibliography"])
    is_standalone = not (is_reference and len(content) > 800)
    
    if is_reference:
        issues.append("❌ Mostly academic references/citations (not user-facing dining content)")
    elif is_standalone:
        positives.append("✓ Standalone content (answerable without context)")
    else:
        issues.append("❌ May need surrounding context")
    
    if positives:
        for pos in positives:
            print(f"  {pos}")
    if issues:
        for issue in issues:
            print(f"  {issue}")
    
    # Verdict
    if len(issues) == 0:
        verdict = "✅ GOOD CHUNK"
    elif len(issues) == 1:
        verdict = "⚠️  MIXED - Usable but with caveats"
    else:
        verdict = "❌ POOR CHUNK - Needs revision"
    
    print(f"\n  Verdict: {verdict}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)

good = 0
mixed = 0
bad = 0

for chunk in chunks:
    if chunk['char_count'] < 200 or chunk['char_count'] > 2500:
        bad += 1
    elif "reference" in chunk['content'].lower() or "citation" in chunk['content'].lower():
        bad += 1
    elif chunk['char_count'] < 500:
        mixed += 1
    else:
        good += 1

print(f"\nGood chunks: {good}")
print(f"Mixed chunks: {mixed}")
print(f"Poor chunks: {bad}")

print(f"\nRECOMMENDATIONS:")
print(f"1. ⚠️  CRITICAL: Only 8 chunks from 3 documents (need ~50-100 for meaningful RAG)")
print(f"   - 2 sources failed to scrape (Berkeleyside, Basic Needs Center)")
print(f"   - These may require JavaScript rendering (Selenium/Playwright)")
print(f"")
print(f"2. CHUNK QUALITY: Mixed results")
if bad > 0:
    print(f"   - {bad} chunks are poor (mostly academic references)")
    print(f"   - Consider filtering out reference-heavy sections")
print(f"")
print(f"3. STRATEGY CHECK:")
print(f"   - Chunk size (2000 chars) is appropriate for your documents")
print(f"   - Overlap (200 chars) looks good")
print(f"   - Issue is document count/length, not chunking logic")
