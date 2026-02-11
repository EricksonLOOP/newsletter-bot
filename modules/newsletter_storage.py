from sqlalchemy import desc

from models.db_models import NewsletterSummary


class NewsletterStorage:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_by_source_key(self, source_key: str) -> NewsletterSummary | None:
        session = self.session_factory()
        try:
            return (
                session.query(NewsletterSummary)
                .filter_by(source_key=source_key)
                .one_or_none()
            )
        finally:
            session.close()

    def save_summary(self, source_key: str, source_url: str | None, source_name: str | None, summary_model):
        session = self.session_factory()
        try:
            existing = (
                session.query(NewsletterSummary)
                .filter_by(source_key=source_key)
                .one_or_none()
            )
            if existing:
                return existing

            record = NewsletterSummary(
                source_key=source_key,
                source_url=source_url,
                source_name=source_name,
                title=summary_model.title,
                description=summary_model.description,
                summary_json=summary_model.dict(),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_summaries(self, limit: int = 50, offset: int = 0) -> list[NewsletterSummary]:
        session = self.session_factory()
        try:
            return (
                session.query(NewsletterSummary)
                .order_by(desc(NewsletterSummary.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def get_by_ids(self, ids: list[int]) -> list[NewsletterSummary]:
        if not ids:
            return []
        session = self.session_factory()
        try:
            return (
                session.query(NewsletterSummary)
                .filter(NewsletterSummary.id.in_(ids))
                .order_by(desc(NewsletterSummary.created_at))
                .all()
            )
        finally:
            session.close()
