import json
import os
from typing import Iterable

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
	default_locals = _normalize_locals(_split_csv(os.getenv("KAFKA_DEFAULT_LOCALS", "Global")))
	if not default_locals:
		default_locals = ["Global"]

	default_content_types = _normalize_content_types(
		_split_csv(os.getenv("KAFKA_DEFAULT_CONTENT_TYPES", "WORLD"))
	)
	if not default_content_types:
		default_content_types = ["WORLD"]

	return {
		"title": news_model.title,
		"subTitle": news_model.description or "",
		"paragraphs": _build_paragraphs(news_model),
		"locals": default_locals,
		"contentTypes": default_content_types,
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
