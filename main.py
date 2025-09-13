import json
import os
import time

from models.newsletter_bot_json_article import NewsletterArticleModel
from modules.gnews_service import GNewsService
from dotenv import load_dotenv

# from modules.kafka_newsletter_producer import send_newsletter_to_kafka
from modules.openai_service import NewsLetterBot
from utils.to_txt import save_newsletter_to_txt

load_dotenv()
GNEWS_KEY = os.getenv('GNEWS_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
gnews = GNewsService(GNEWS_KEY)
bot = NewsLetterBot(OPENAI_KEY)

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
                    print("CRIANDO JSON...")
                    news: str = bot.create_newsletter(newsletter)
                    print("SALVANDO...")
                    news_dict = json.loads(news)
                    news_model = NewsletterArticleModel(**news_dict)

                    print("SALV0!")
                    print("ENVIANDO PARA A FILA...")
                    save_newsletter_to_txt(news_model)
                except Exception as e:
                    print(f"Erro ao parser notícia \n {e}")

        time.sleep(10.0)
