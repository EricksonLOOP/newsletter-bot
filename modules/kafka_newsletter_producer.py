import json
import os
from typing import Iterable
from urllib.parse import urlparse

from confluent_kafka import Producer

from models.newsletter_bot_json_article import NewsletterArticleModel


_LOCAL_NAME_MAP = {
	"global": "Global",
	"br": "BR",
	"us": "US",
	"eu": "EU",
	"asia": "ASIA",
	"africa": "AFRICA",
	"latam": "LATAM",
}

_LOCAL_TLDS = {
	".br": "BR",
	".us": "US",
	".eu": "EU",
	".asia": "ASIA",
	".africa": "AFRICA",
	".mx": "LATAM",
	".ar": "LATAM",
	".cl": "LATAM",
	".co": "LATAM",
	".pe": "LATAM",
	".uy": "LATAM",
	".py": "LATAM",
	".bo": "LATAM",
	".ec": "LATAM",
	".ve": "LATAM",
}

_LOCAL_KEYWORDS = {
	"BR": {"brasil", "brazil", "brasileiro", "sao paulo", "rio", "brasilia"},
	"US": {"usa", "u.s.", "united states", "america", "american", "new york", "california"},
	"EU": {"europe", "european", "eu", "europeia", "ue", "germany", "france", "spain", "italy", "uk", "united kingdom"},
	"ASIA": {"asia", "asian", "china", "japan", "india", "korea"},
	"AFRICA": {"africa", "african", "nigeria", "south africa", "egypt"},
	"LATAM": {"latam", "latin america", "america latina", "mexico", "argentina", "chile", "colombia", "peru", "uruguay", "paraguay", "bolivia", "ecuador", "venezuela"},
}

_CONTENT_NAMES = {
	"IA",
	"WORLD",
	"POLITICS",
	"ECONOMY",
	"TECH",
	"SCIENCE",
	"HEALTH",
	"SPORTS",
	"ENTERTAINMENT",
	"CULTURE",
	"EDUCATION",
	"ENVIRONMENT",
	"CRIME",
	"LIFESTYLE",
	"BUSINESS",
	"SOFTWARE",
	"TRAVEL",
	"OPINION",
	"BREAKING",
}

_CONTENT_KEYWORDS = {
	"IA": {"ai", "a.i.", "artificial intelligence", "inteligencia artificial", "machine learning", "ml", "llm"},
	"WORLD": {"world", "global", "international", "mundo", "internacional"},
	"POLITICS": {"politics", "political", "election", "government", "congress", "senate", "president", "politica", "eleicao", "governo"},
	"ECONOMY": {"economy", "economic", "inflation", "gdp", "market", "stock", "finance", "financas", "economia", "mercado"},
	"TECH": {"tech", "technology", "startup", "gadgets", "device", "hardware"},
	"SCIENCE": {"science", "research", "space", "nasa", "discovery", "ciencia"},
	"HEALTH": {"health", "medicine", "medical", "hospital", "saude", "vacina"},
	"SPORTS": {"sports", "football", "soccer", "nba", "fifa", "esporte"},
	"ENTERTAINMENT": {"entertainment", "movie", "series", "music", "celebrity", "cinema", "serie"},
	"CULTURE": {"culture", "art", "museum", "cultura", "arte"},
	"EDUCATION": {"education", "school", "university", "college", "educacao", "enem"},
	"ENVIRONMENT": {"environment", "climate", "sustainability", "green", "meio ambiente", "clima"},
	"CRIME": {"crime", "police", "investigation", "law", "crime", "policia"},
	"LIFESTYLE": {"lifestyle", "fashion", "food", "travel", "vida", "moda", "culinaria"},
	"BUSINESS": {"business", "entrepreneur", "company", "merger", "negocio", "empreendedor"},
	"SOFTWARE": {"software", "developer", "programming", "code", "coding", "dev"},
	"TRAVEL": {"travel", "tourism", "trip", "turismo", "viagem"},
	"OPINION": {"opinion", "editorial", "column", "opniao", "coluna"},
	"BREAKING": {"breaking", "urgent", "alert", "urgente", "ultima hora"},
}


def _split_csv(value: str | None) -> list[str]:
	if not value:
		return []
	return [item.strip() for item in value.split(",") if item.strip()]


def _normalize_locals(locals_raw: Iterable[str]) -> list[str]:
	normalized = []
	for item in locals_raw:
		key = item.strip().lower()
		mapped = _LOCAL_NAME_MAP.get(key)
		if mapped and mapped not in normalized:
			normalized.append(mapped)
	return normalized


def _normalize_content_types(content_raw: Iterable[str]) -> list[str]:
	normalized = []
	for item in content_raw:
		key = item.strip().upper()
		if key in _CONTENT_NAMES and key not in normalized:
			normalized.append(key)
	return normalized


def _extract_text_chunks(news_model: NewsletterArticleModel) -> list[str]:
	chunks = [news_model.title, news_model.description, news_model.source.name, news_model.source.url]
	for topic in news_model.topics:
		chunks.append(topic.title)
		chunks.extend(topic.paragraphs)
	additional = []
	for attr in ("tags", "topics", "keywords", "categories"):
		value = getattr(news_model, attr, None)
		if isinstance(value, list):
			additional.extend([str(item) for item in value])
	chunks.extend(additional)
	return [chunk for chunk in chunks if chunk]


def _detect_locals_from_text(chunks: Iterable[str]) -> list[str]:
	text = " ".join(chunks).lower()
	locals_found: list[str] = []
	for local_key, keywords in _LOCAL_KEYWORDS.items():
		if any(keyword in text for keyword in keywords):
			locals_found.append(local_key)
	return locals_found


def _detect_locals_from_url(url: str | None) -> list[str]:
	if not url:
		return []
	try:
		hostname = urlparse(url).hostname or ""
		for tld, local_key in _LOCAL_TLDS.items():
			if hostname.endswith(tld):
				return [local_key]
	except Exception:
		return []
	return []


def _detect_content_types(chunks: Iterable[str]) -> list[str]:
	text = " ".join(chunks).lower()
	content_found: list[str] = []
	for content_key, keywords in _CONTENT_KEYWORDS.items():
		if any(keyword in text for keyword in keywords):
			content_found.append(content_key)
	return content_found


def _build_paragraphs(news_model: NewsletterArticleModel) -> list[str]:
	paragraphs: list[str] = []
	for topic in news_model.topics:
		if topic.title:
			paragraphs.append(topic.title.strip())
		for paragraph in topic.paragraphs:
			if paragraph and paragraph.strip():
				paragraphs.append(paragraph.strip())
	return paragraphs


def build_content_payload(news_model: NewsletterArticleModel) -> dict:
	chunks = _extract_text_chunks(news_model)
	locals_found = _detect_locals_from_url(news_model.source.url)
	locals_found.extend(_detect_locals_from_text(chunks))
	locals_normalized = _normalize_locals(locals_found)
	if not locals_normalized:
		locals_normalized = ["Global"]

	content_found = _detect_content_types(chunks)
	content_normalized = _normalize_content_types(content_found)
	if not content_normalized:
		content_normalized = ["WORLD"]

	return {
		"title": news_model.title,
		"subTitle": news_model.description or "",
		"paragraphs": _build_paragraphs(news_model),
		"locals": locals_normalized,
		"contentTypes": content_normalized,
		"resource": {
			"name": news_model.source.name,
			"url": news_model.source.url,
		},
	}


def _delivery_report(err, msg):
	if err is not None:
		print(f"Erro ao enviar mensagem: {err}")
	else:
		print(f"Mensagem enviada para {msg.topic()} [{msg.partition()}]")


def _build_producer() -> Producer:
	conf = {
		"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
		"client.id": os.getenv("KAFKA_CLIENT_ID", "newsletter-producer"),
	}
	return Producer(conf)


def send_newsletter_to_kafka(news_model: NewsletterArticleModel, topic: str | None = None) -> None:
	producer = _build_producer()
	resolved_topic = topic or os.getenv("KAFKA_TOPIC", "aboutt-news")
	payload = build_content_payload(news_model)

	producer.produce(
		resolved_topic,
		key=news_model.title,
		value=json.dumps(payload, ensure_ascii=True),
		callback=_delivery_report,
	)
	producer.flush()
