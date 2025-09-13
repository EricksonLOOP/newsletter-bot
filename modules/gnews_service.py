import requests

class GNewsService:
    DEFAULT_GNEWS_URL = "https://gnews.io/api/v4/"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_news(
        self,
        max: int = 10,
        q: str = "",
        lang: str = 'any',
        country: str = 'any',
        in_news: str = 'any',
        page: int = 1,
    ):
        params = {
            "q": q,
            "lang": lang,
            "max": max,
            "page": page,
            "country": country,
            "in": in_news,
            "apikey": self.api_key
        }

        response = requests.get(f"{self.DEFAULT_GNEWS_URL}search", params=params)
        response.raise_for_status()  # garante que erros HTTP sejam lançados
        data = response.json()

        return data.get("articles", [])
