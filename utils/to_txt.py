import os
from pathlib import Path

from models.newsletter_bot_json_article import NewsletterArticleModel


def save_newsletter_to_txt(news: NewsletterArticleModel, folder: str = "newsletters"):
    """
    Salva cada newsletter como um arquivo .txt em uma pasta especificada
    """
    # Cria a pasta se não existir
    Path(folder).mkdir(parents=True, exist_ok=True)

    # Nome do arquivo baseado no título (limpando caracteres inválidos)
    filename = f"{news.title}".replace(" ", "_").replace("/", "_")[:50] + ".txt"
    filepath = os.path.join(folder, filename)

    # Monta o conteúdo do arquivo
    content = f"Title: {news.title}\nDescription: {news.description}\n\n"
    for topic in news.topics:
        content += f"Topic {topic.index}: {topic.title}\n"
        for paragraph in topic.paragraphs:
            content += f"{paragraph}\n"
        content += "\n"
    content += f"Source: {news.source.name} - {news.source.url}\n"

    # Salva no arquivo
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved newsletter: {filepath}")
