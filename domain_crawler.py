import os
import time
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import google.generativeai as genai

# ----------------- Load API Key from .env -----------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("API Key not found. Please set GEMINI_API_KEY in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ----------------- Domain Crawler -----------------
def crawl_domain(start_url, max_pages=20):
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
                "content": text[:2000]  # limit content to avoid huge prompts
            })

            # Collect same-domain links
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                if urlparse(href).netloc == urlparse(start_url).netloc and href not in visited:
                    queue.append(href)

            time.sleep(1)  # polite crawl delay

        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")

    return results

# ----------------- Gemini Summarizer with Rate-Limit Handling -----------------
def gemini_summarize(pages):
    results = []

    if not pages:
        print("No pages to summarize.")
        return results

    for page in pages:
        retries = 3
        summary = ""
        while retries > 0:
            try:
                prompt = f"Summarize this webpage content:\n\n{page['content']}"
                response = model.generate_content(prompt)
                summary = response.text
                break  # success
            except genai.ApiError as e:
                if "429" in str(e):
                    # Parse retry_delay if available, default to 35s
                    retry_delay = 35
                    print(f"⚠️ Rate limit hit. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retries -= 1
                else:
                    summary = f"Error summarizing page: {e}"
                    break
            except Exception as e:
                summary = f"Error summarizing page: {e}"
                break

        if not summary:
            summary = "⚠️ Could not summarize due to repeated rate limits or errors."

        results.append({"url": page["url"], "summary": summary})

        time.sleep(2)  # small delay between summarizations to avoid hitting limits

    return results

# ----------------- Main Execution -----------------
if __name__ == "__main__":
    start_url = input("Enter the website URL to crawl: ").strip()
    if not start_url.startswith("http"):
        start_url = "https://" + start_url

    pages = crawl_domain(start_url, max_pages=20)
    print(f"\n✅ Crawled {len(pages)} pages")

    summaries = gemini_summarize(pages)

    print("\n===== Domain Crawl + Gemini Summaries =====\n")
    for res in summaries:
        print(f"URL: {res['url']}")
        print(f"Summary: {res['summary']}")
        print("-" * 50)
