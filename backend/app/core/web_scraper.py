# app/core/web_scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def find_terms_url(base_url):
    """
    Find likely Terms & Conditions or Privacy Policy link.
    """
    if not base_url.startswith("http"):
        base_url = "https://" + base_url

    try:
        res = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        links = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)]
        patterns = ["terms", "condition", "privacy", "policy", "legal"]

        for link in links:
            if any(re.search(p, link, re.I) for p in patterns):
                return link
        return None

    except Exception as e:
        print(f"[ERROR] Could not fetch links: {e}")
        return None


def extract_paragraphs_from_url(url):
    """
    Return a list of paragraph-like text blocks from a webpage.
    Prefer actual <p> tags; if none found, fall back to splitting the visible
    text by two or more newlines or by sentences if necessary.
    """
    try:
        print(f"DEBUG: Fetching {url}...")
        # Use a more modern and generic User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        res = requests.get(url, headers=headers, timeout=15)
        print(f"DEBUG: Status Code: {res.status_code}")
        
        if res.status_code in [403, 401]:
            print(f"❌ Access Denied (Status {res.status_code}). The website might be blocking scrapers.")
            # Try one more time with a different user agent (mobile)
            headers["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            print("🔄 Retrying with mobile User-Agent...")
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code in [403, 401]:
                 return []
            
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Aggressive cleanup of non-content
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "svg", "button", "input", "form"]):
            tag.decompose()

        paragraphs = []

        # Strategy 1: Look for specific privacy policy containers first
        content_divs = soup.find_all("div", class_=re.compile(r"privacy|policy|terms|legal|content|article|main", re.I))
        if content_divs:
            for div in content_divs:
                # Extract text from these specific divs
                texts = [t.strip() for t in div.stripped_strings if len(t.strip()) > 30]
                paragraphs.extend(texts)

        # Strategy 2: Standard <p> tags if Strategy 1 yielded little
        if len(paragraphs) < 5:
            for p in soup.find_all("p"):
                text = " ".join(p.stripped_strings)
                if text and len(text) > 30: # Filter out tiny captions
                    paragraphs.append(text)

        # Strategy 3: Generic div/section text if still empty
        if not paragraphs:
            for tag_name in ("div", "section", "article", "li"):
                for tag in soup.find_all(tag_name):
                    text = " ".join(tag.stripped_strings)
                    if text and len(text.split()) > 15:  # moderate length
                        paragraphs.append(text)

        # Strategy 4: The "Nuclear Option" - just get all text and split by newlines
        if not paragraphs:
            print("⚠ Parsing fallback: Extracting all visible text.")
            visible = "\n".join(soup.stripped_strings)
            # Split by double newlines to preserve some paragraph structure
            raw_pars = [p.strip() for p in re.split(r"\n{2,}", visible) if len(p.strip()) > 40]
            paragraphs = raw_pars

        # Deduplicate while preserving order
        seen = set()
        unique_paragraphs = []
        for p in paragraphs:
            if p not in seen:
                seen.add(p)
                unique_paragraphs.append(p)

        return unique_paragraphs
    except Exception as e:
        print(f"[ERROR] Could not extract paragraphs: {e}")
        return []


def get_terms_text(base_url):
    """
    Main function — find and extract T&C text with paragraphs separated.
    Handles both direct policy links and base URLs by searching for links.
    """
    # 1. Check if the provided URL looks like a policy itself or if user wants direct access
    lower_url = base_url.lower()
    is_direct_candidate = any(x in lower_url for x in ["terms", "privacy", "policy", "condition", "legal"])
    
    terms_url = None
    paragraphs = []

    if is_direct_candidate:
        print(f"ℹ URL looks like a direct policy link: {base_url}")
        target_url = base_url if base_url.startswith("http") else "https://" + base_url
        paragraphs = extract_paragraphs_from_url(target_url)
        if paragraphs and len(paragraphs) > 2: # Heuristic: if we got meaningful content
            terms_url = target_url
            print(f"✅ Successfully scraped direct link: {terms_url}")
            return terms_url, paragraphs
        else:
            print("⚠ Direct link scrape yielded insufficient data. Trying to find sub-links...")

    # 2. If not direct or direct failed, try to find a link from the base URL
    if not terms_url:
        terms_url = find_terms_url(base_url)
    
    # 3. If found via search, scrape it
    if terms_url:
        print(f"✅ Found policy link: {terms_url}")
        paragraphs = extract_paragraphs_from_url(terms_url)
    else:
        # Fallback: maybe the base URL *was* the content but didn't match keywords?
        # Only try if we haven't tried it as a direct candidate yet
        if not is_direct_candidate:
           print("⚠ No specific policy link found. Attempting to scrape the base URL as a fallback...")
           target_url = base_url if base_url.startswith("http") else "https://" + base_url
           paragraphs = extract_paragraphs_from_url(target_url)
           if paragraphs:
               terms_url = target_url
               print(f"✅ Scraped content from base URL: {terms_url}")
           else:
               print("❌ No content found on base URL either.")
    
    if not terms_url:
        print("⚠ No terms page or content found.")
        return None, []

    return terms_url, paragraphs

# Adapter for Lang Graph
def scrape_policy(url: str) -> str:
    """
    Scrapes the privacy policy from the given URL.
    Returns the combined text of the policy.
    """
    print(f"DEBUG: app.core.web_scraper calling get_terms_text for {url}")
    terms_url, paragraphs = get_terms_text(url)
    
    if not paragraphs:
        # Fallback or error handling
        return ""
    
    return "\n\n".join(paragraphs)
