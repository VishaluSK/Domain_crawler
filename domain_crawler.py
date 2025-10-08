import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import google.generativeai as genai

# ----------------- Hardcoded API Key -----------------
# ⚠️ Replace this string with your actual API key from Google AI Studio
GEMINI_API_KEY = "paste your gemini api"  

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ----------------- Domain Crawler -----------------
def crawl_domain(start_url, max_pages=20):   # you can increase max_pages if needed
    visited = set()
    queue = deque([start_url])
    results = []

    headers = {"User-Agent": "Mozilla/5.0"}

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        try:
            print(f"Crawling: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Status code {response.status_code} for {url}")
                continue

            visited.add(url)

            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(" ", strip=True)

            results.append({
                "url": url,
                "content": text[:2000]  # keep content limited to avoid huge prompts
            })

            # Collect same-domain links
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                if urlparse(href).netloc == urlparse(start_url).netloc and href not in visited:
                    queue.append(href)

            time.sleep(1)  # polite delay between requests

        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")

    return results

# ----------------- Gemini Summarizer -----------------
def gemini_summarize(pages):
    results = []

    if not pages:
        print("No pages to summarize.")
        return results

    for page in pages:
        try:
            prompt = f"Summarize this webpage content:\n\n{page['content']}"
            response = model.generate_content(prompt)
            summary = response.text
        except Exception as e:
            summary = f"Error summarizing page: {e}"

        results.append({"url": page["url"], "summary": summary})

    return results

# ----------------- Main Execution -----------------
if __name__ == "__main__":
    start_url = input("Enter the website URL to crawl: ").strip()
    if not start_url.startswith("http"):
        start_url = "https://" + start_url

    # Step 1: Crawl domain
    pages = crawl_domain(start_url, max_pages=20)
    print(f"\n✅ Crawled {len(pages)} pages")

    # Step 2: Summarize pages
    summaries = gemini_summarize(pages)

    # Step 3: Print results
    print("\n===== Domain Crawl + Gemini Summaries =====\n")
    for res in summaries:
        print(f"URL: {res['url']}")
        print(f"Summary: {res['summary']}")
        print("-" * 50)
