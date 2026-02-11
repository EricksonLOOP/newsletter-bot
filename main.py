import json
import os
import time

from dotenv import load_dotenv

from models.newsletter_bot_json_article import NewsletterArticleModel
from modules.cache_service import build_cache_from_env
from modules.db_service import init_db
from modules.gnews_service import GNewsService
from modules.newsletter_storage import NewsletterStorage
from modules.newsletter_utils import build_source_key

from modules.kafka_newsletter_producer import send_newsletter_to_kafka
from modules.openai_service import NewsLetterBot
from utils.to_txt import save_newsletter_to_txt

load_dotenv()
GNEWS_KEY = os.getenv("GNEWS_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

gnews = GNewsService(GNEWS_KEY)
bot = NewsLetterBot(OPENAI_KEY)

SessionLocal = init_db()
storage = NewsletterStorage(SessionLocal)
cache = build_cache_from_env()

if __name__ == "__main__":
    while True:
        print("Pegando noticias no GNEWS...")
        # asdasd
        newsletters: list[dict] = gnews.get_news(max=100, q="world", lang="any", country="any")
        print(f"FORAM ENCONTRADAS: {len(newsletters)} noticias")
        if len(newsletters) > 0:
            for newsletter in newsletters:
                time.sleep(10.0)
                try:
                    source_key, source_url, source_name = build_source_key(newsletter)

                    cached_summary = cache.get_summary(source_key)
                    if cached_summary:
                        news_model = NewsletterArticleModel(**cached_summary)
                        storage.save_summary(source_key, source_url, source_name, news_model)
                        save_newsletter_to_txt(news_model)
                        continue

                    db_record = storage.get_by_source_key(source_key)
                    if db_record:
                        news_model = NewsletterArticleModel(**db_record.summary_json)
                        cache.set_summary(source_key, db_record.summary_json)
                        save_newsletter_to_txt(news_model)
                        continue

                    print("CRIANDO JSON...")
                    news: str = bot.create_newsletter(newsletter)
                    print("SALVANDO...")
                    news_dict = json.loads(news)
                    news_model = NewsletterArticleModel(**news_dict)

                    storage.save_summary(source_key, source_url, source_name, news_model)
                    cache.set_summary(source_key, news_model.dict())

                    print("SALV0!")
                    print("ENVIANDO PARA A FILA...")
                    send_newsletter_to_kafka(news_model)
                    save_newsletter_to_txt(news_model)
                except Exception as e:
                    print(f"Erro ao parser notícia \n {e}")

        time.sleep(10.0)
