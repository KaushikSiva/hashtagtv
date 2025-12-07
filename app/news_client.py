"\"\"\"News client interacting with the X news API.\"\"\""
from typing import List

from xdk import Client

from .config import X_BEARER_TOKEN

DEFAULT_NEWS_FIELDS = ["title", "summary", "published_at"]


def _build_client() -> Client | None:
    if not X_BEARER_TOKEN:
        return None
    return Client(bearer_token=X_BEARER_TOKEN)


def fetch_top_news(query: str, max_results: int) -> List[str]:
    """Search X news stories that match the provided query."""
    if not query:
        return []

    client = _build_client()
    if not client:
        return []

    try:
        response = client.news.search(
            query=query,
            max_results=min(max_results, 100),
            news_fields=DEFAULT_NEWS_FIELDS,
        )
    except Exception:
        return []

    payload = response.model_dump()
    articles = payload.get("data") or []

    entries: List[str] = []
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary") or article.get("description") or ""
        snippet = " ".join(filter(None, [title.strip(), summary.strip()]))
        if snippet:
            entries.append(snippet)

    return entries[:max_results]
