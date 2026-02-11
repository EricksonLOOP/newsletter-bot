import hashlib
import json


def build_source_key(article: dict) -> tuple[str, str | None, str | None]:
    url = article.get("url") or article.get("link")
    source = article.get("source") or {}
    source_name = source.get("name") if isinstance(source, dict) else None

    if url:
        return url, url, source_name

    title = (article.get("title") or "").strip()
    published = article.get("publishedAt") or article.get("published_at") or ""
    raw = f"{title}|{published}"
    if not raw.strip("|"):
        raw = json.dumps(article, sort_keys=True)

    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"no-url:{digest}", None, source_name
