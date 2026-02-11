from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class NewsletterSummary(Base):
    __tablename__ = "newsletter_summaries"

    id = Column(Integer, primary_key=True)
    source_key = Column(String(1024), unique=True, nullable=False)
    source_url = Column(String(1024), nullable=True)
    source_name = Column(String(255), nullable=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    summary_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
