"""
Document ingestion and chunking pipeline for UC Berkeley Dining Guide.
Fetches documents from URLs, cleans them, and chunks them for RAG system.
Uses requests for static content, Playwright for JavaScript-heavy sites.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re
import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# Document sources from planning.md
DOCUMENTS = [
    {
        "id": 1,
        "name": "Berkeleyside - Freshmen Food Guide",
        "url": "https://www.berkeleyside.org/2025/08/26/where-to-eat-if-you-are-new-to-berkeley",
        "type": "article",
    },
    {
        "id": 2,
        "name": "UC Berkeley Dining Locations",
        "url": "https://dining.berkeley.edu/locations",
        "type": "directory",
    },
    {
        "id": 3,
        "name": "Berkeley Life: Dining at UC Berkeley",
        "url": "https://life.berkeley.edu/dining-at-uc-berkeley-where-to-eat",
        "type": "guide",
    },
    {
        "id": 4,
        "name": "UC Berkeley Foodscape Map",
        "url": "https://food.berkeley.edu/foodscape-map",
        "type": "interactive",
    },
    {
        "id": 5,
        "name": "UC Berkeley Basic Needs Center",
        "url": "https://basicneeds.berkeley.edu",
        "type": "resource",
    },
    {
        "id": 6,
        "name": "Cal Student Store - Dining & Food",
        "url": "https://store.berkeley.edu/dining",
        "type": "directory",
    },
    {
        "id": 7,
        "name": "Berkeley Food Institute Resources",
        "url": "https://food.berkeley.edu/about/",
        "type": "resource",
    },
    {
        "id": 8,
        "name": "UC Berkeley Housing & Dining",
        "url": "https://housing.berkeley.edu/",
        "type": "guide",
    },
    {
        "id": 9,
        "name": "Berkeley Student Food Cooperative",
        "url": "https://www.berkeleystudentfood.org/",
        "type": "resource",
    },
    {
        "id": 10,
        "name": "Resident Student Services - Dining",
        "url": "https://reslife.berkeley.edu/",
        "type": "guide",
    },
]

# Configuration from planning.md
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200


def fetch_document(url):
    """Fetch raw HTML from URL. Try requests first, fall back to Playwright for JS-heavy sites."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Try fast requests method first
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        # Check if we got meaningful content (not a JS-only page)
        if len(html) > 1000 and ('<html' in html.lower() or '<body' in html.lower()):
            return html, "requests"
    except Exception as e:
        pass

    # Fall back to Playwright for JavaScript-heavy sites
    if PLAYWRIGHT_AVAILABLE:
        try:
            html = asyncio.run(_fetch_with_playwright(url))
            if html and len(html) > 1000:
                return html, "playwright"
        except Exception as e:
            pass

    return None, None


async def _fetch_with_playwright(url):
    """Fetch page using Playwright headless browser (handles JavaScript)."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=30000, wait_until="networkidle")
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        raise Exception(f"Playwright error: {e}")


def clean_document(html_content):
    """
    Clean HTML document: remove navigation, ads, boilerplate, scripts, styles.
    Keep substantive content. LESS aggressive than before.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style tags entirely
    for tag in soup(["script", "style", "meta", "noscript"]):
        tag.decompose()

    # Remove only the most obvious unwanted elements by ID/class
    # Be targeted, not aggressive
    unwanted_selectors = [
        "nav", "footer", "header",
        "[role='navigation']",
        ".navbar", ".nav-menu",
        ".sidebar", ".aside",
        "[class*='advertisement']", "[class*='ad-container']",
        "[class*='cookie']", "[class*='banner-ad']",
        "[class*='social-share']",
        ".breadcrumb",
        "[id*='comments']", "[class*='-comments']",
    ]

    for selector in unwanted_selectors:
        try:
            for tag in soup.select(selector):
                tag.decompose()
        except:
            pass

    # Extract main content more intelligently
    main_content = None

    # Try to find main content area
    for candidate in ["main", "article", "[role='main']", ".post-content",
                      ".content", ".article-body", ".entry-content", "#content"]:
        attempt = soup.select_one(candidate)
        if attempt:
            # Verify it has substantial text
            text_length = len(attempt.get_text(strip=True))
            if text_length > 300:  # At least 300 chars of real content
                main_content = attempt
                break

    # Fallback: use body if main content not found
    if not main_content:
        main_content = soup.body if soup.body else soup

    # Extract text
    text = main_content.get_text(separator="\n", strip=True)

    # Clean up whitespace and entities
    text = re.sub(r"\n\s*\n+", "\n\n", text)  # Normalize newlines
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"&[a-z]+;", " ", text)  # Remove remaining entities
    text = re.sub(r" +", " ", text)  # Remove excess spaces

    return text.strip()


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks using LangChain."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return chunks


def main():
    """Main ingestion pipeline."""
    documents_dir = Path("documents")
    documents_dir.mkdir(exist_ok=True)

    raw_documents = []
    all_chunks = []

    print("=" * 80)
    print("UC BERKELEY DINING GUIDE — DOCUMENT INGESTION")
    print("=" * 80)

    for doc in DOCUMENTS:
        print(f"\n[{doc['id']}] Fetching: {doc['name']}")
        result = fetch_document(doc["url"])

        if isinstance(result, tuple):
            html, method = result
        else:
            html = result
            method = None

        if not html:
            print(f"  ✗ Failed to fetch from {doc['url']}")
            continue

        print(f"  ✓ Fetched with {method} ({len(html)} chars)")

        cleaned_text = clean_document(html)
        print(f"  → Cleaned text: {len(cleaned_text)} characters")

        if len(cleaned_text) < 100:
            print(f"  ✗ Content too short after cleaning (likely parsing error)")
            continue

        # Chunk the document
        chunks = chunk_text(cleaned_text)
        print(f"  → Chunked into {len(chunks)} pieces")

        # Store raw document
        raw_doc = {
            "id": doc["id"],
            "name": doc["name"],
            "url": doc["url"],
            "type": doc["type"],
            "fetch_method": method,
            "cleaned_text": cleaned_text,
            "raw_char_count": len(html),
            "cleaned_char_count": len(cleaned_text),
            "chunk_count": len(chunks),
        }
        raw_documents.append(raw_doc)

        # Store chunks with metadata
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "doc_id": doc["id"],
                "doc_name": doc["name"],
                "chunk_index": i,
                "content": chunk,
                "char_count": len(chunk),
            })

    # Save to JSON for inspection
    print(f"\n{'=' * 80}")
    print(f"SUMMARY: Ingested {len(raw_documents)} documents")
    print(f"Total chunks: {len(all_chunks)}")

    # Save raw documents
    with open(documents_dir / "raw_documents.json", "w") as f:
        json.dump(raw_documents, f, indent=2)
    print(f"\n✓ Saved raw_documents.json ({len(raw_documents)} docs)")

    # Save chunks
    with open(documents_dir / "chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"✓ Saved chunks.json ({len(all_chunks)} chunks)")

    # Print first cleaned document for verification
    if raw_documents:
        print(f"\n{'=' * 80}")
        print("VERIFICATION: First Cleaned Document")
        print(f"{'=' * 80}")
        first_doc = raw_documents[0]
        print(f"\nSource: {first_doc['name']}")
        print(f"URL: {first_doc['url']}")
        print(f"Cleaned length: {first_doc['cleaned_char_count']} characters")
        print(f"\n--- Content Preview (first 2000 chars) ---\n")
        print(first_doc['cleaned_text'][:2000])
        print("\n...")

        # Check for remaining HTML entities or nav artifacts
        issues = []
        if "&" in first_doc['cleaned_text'] and ";" in first_doc['cleaned_text']:
            issues.append("Possible HTML entities remaining")
        if any(nav_word in first_doc['cleaned_text'].lower()
               for nav_word in ["menu", "navigation", "home", "about", "contact"]):
            issues.append("Possible nav text remaining (common words only - verify)")

        if issues:
            print(f"\n⚠ Potential issues detected:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n✓ Document appears clean (no obvious HTML artifacts)")


if __name__ == "__main__":
    main()
