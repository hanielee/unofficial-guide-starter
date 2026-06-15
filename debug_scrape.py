import requests
from bs4 import BeautifulSoup
import re

urls = {
    "Berkeleyside": "https://www.berkeleyside.org/2025/08/26/where-to-eat-if-you-are-new-to-berkeley",
    "Basic Needs": "https://basicneeds.berkeley.edu",
}

for name, url in urls.items():
    print(f"\n{'='*80}")
    print(f"DEBUG: {name}")
    print(f"{'='*80}")
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; educational-rag/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        print(f"✓ Fetched: {len(html)} characters")
        print(f"  Status code: {response.status_code}")
        
        # Show first 500 chars
        print(f"\n--- First 500 chars of raw HTML ---")
        print(html[:500])
        
        # Try to find main content
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for content areas
        main = soup.select_one("main, [role='main'], article, .content, .post")
        if main:
            text = main.get_text()[:300]
            print(f"\n--- Text from main element (first 300 chars) ---")
            print(text)
        
        # Check for specific patterns
        scripts = len(soup.find_all("script"))
        styles = len(soup.find_all("style"))
        print(f"\n  Scripts: {scripts}, Styles: {styles}")
        
        # Look for specific content keywords
        html_lower = html.lower()
        keywords = ["dining", "food", "restaurant", "cafe", "freshmen"]
        for kw in keywords:
            count = html_lower.count(kw)
            if count > 0:
                print(f"  '{kw}' found {count} times")
                
    except Exception as e:
        print(f"✗ Error: {e}")
