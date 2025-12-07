\"\"\"FastAPI entry point for NewsBot.\"\"\"
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .avatar_client import create_avatar_video
from .news_client import fetch_top_news
from .summarizer import generate_news_script_from_items


class NewsRequest(BaseModel):
    query: str = Field(..., min_length=1)
    max_results: int = Field(30, ge=1, le=100)
    generate_video: bool = False


class NewsResult(BaseModel):
    query: str
    script: str
    news_items: List[str]
    avatar_video: Optional[dict] = None


CATEGORY_QUERIES = {
    \"sports\": \"sports news\",
    \"politics\": \"politics news\",
    \"finance\": \"finance news\",
    \"stocks\": \"stock market news\",
    \"tech\": \"technology news\",
    \"technology\": \"technology news\",
    \"weather\": \"weather news\",
}


def _resolve_query(category: str) -> str:
    normalized = category.strip().lower()
    return CATEGORY_QUERIES.get(normalized, f\"{normalized or 'general'} news\")


class CategoryRequest(BaseModel):
    categories: List[str] = Field(
        default_factory=lambda: [\"sports\", \"politics\", \"finance\", \"tech\", \"weather\"],
        min_items=1,
    )
    max_results: int = Field(30, ge=1, le=100)
    generate_video: bool = False


class CategorySummary(BaseModel):
    category: str
    query: str
    script: str
    news_items: List[str]
    avatar_video: Optional[dict] = None


class CategoryNewsResult(BaseModel):
    categories: List[CategorySummary]


app = FastAPI(title=\"NewsBot\")


@app.post(\"/news\", response_model=NewsResult)
async def generate_news_report(request: NewsRequest) -> NewsResult:
    news_items = fetch_top_news(request.query, request.max_results)
    script = generate_news_script_from_items(request.query, news_items)

    result = {
        \"query\": request.query,
        \"script\": script,
        \"news_items\": news_items,
        \"avatar_video\": None,
    }

    if request.generate_video:
        result[\"avatar_video\"] = create_avatar_video(script)

    return result


@app.post(\"/news/categories\", response_model=CategoryNewsResult)
async def generate_category_news(request: CategoryRequest) -> CategoryNewsResult:
    summaries: List[CategorySummary] = []

    for category in request.categories:
        query = _resolve_query(category)
        news_items = fetch_top_news(query, request.max_results)
        script = generate_news_script_from_items(query, news_items)
        avatar = create_avatar_video(script) if request.generate_video else None

        summaries.append(
            CategorySummary(
                category=category,
                query=query,
                script=script,
                news_items=news_items,
                avatar_video=avatar,
            )
        )

    return CategoryNewsResult(categories=summaries)
