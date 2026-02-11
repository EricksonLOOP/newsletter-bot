import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.db_service import init_db
from modules.newsletter_storage import NewsletterStorage


class NewsletterOut(BaseModel):
    id: int
    title: str
    description: str | None
    source_url: str | None
    source_name: str | None
    created_at: datetime
    summary_json: dict


class NewsletterListOut(BaseModel):
    total: int
    items: list[NewsletterOut]


app = FastAPI(title="Newsletter Bot API")

frontend_origin = os.getenv("DASHBOARD_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionLocal = init_db()
storage = NewsletterStorage(SessionLocal)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/newsletters", response_model=NewsletterListOut)
def list_newsletters(limit: int = 50, offset: int = 0):
    limit = min(max(limit, 1), 200)
    offset = max(offset, 0)
    records = storage.list_summaries(limit=limit, offset=offset)
    items = [
        NewsletterOut(
            id=record.id,
            title=record.title,
            description=record.description,
            source_url=record.source_url,
            source_name=record.source_name,
            created_at=record.created_at,
            summary_json=record.summary_json,
        )
        for record in records
    ]
    total = len(items)
    return NewsletterListOut(total=total, items=items)


