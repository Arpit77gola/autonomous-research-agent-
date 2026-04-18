from __future__ import annotations

import os
import re
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from graph.state import Source


_tavily: TavilyClient | None = None


def _get_tavily() -> TavilyClient:
    global _tavily
    if _tavily is None:
        key = os.getenv("TAVILY_API_KEY", "")
        if not key:
            raise EnvironmentError("TAVILY_API_KEY not set")
        _tavily = TavilyClient(api_key=key)
    return _tavily


def web_search(query: str, max_results: int | None = None) -> list[Source]:
    """Run a Tavily search. Returns list of Source objects."""
    n = max_results or int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    try:
        response = _get_tavily().search(
            query=query,
            search_depth="advanced",
            max_results=n,
            include_answer=True,
        )
        return [
            Source(
                url=r.get("url", ""),
                title=r.get("title", "Untitled"),
                snippet=r.get("content", ""),
                relevance_score=r.get("score", 1.0),
            )
            for r in response.get("results", [])
        ]
    except Exception as e:
        print(f"[search] Tavily error: {e}")
        return []


def scrape_page(url: str, max_chars: int = 3000) -> str:
    """Scrape readable text from a URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (ResearchAgent/1.0)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s{2,}", " ", text)[:max_chars]
    except Exception:
        return ""