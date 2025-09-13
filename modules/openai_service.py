import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import SecretStr

from models.newsletter_bot_json_article import NewsletterArticleModel
from modules.agents_service import MultiAgents


class NewsLetterBot:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4.1-mini-2025-04-14", temperature: float = 0.7):
        self.api_key = openai_api_key
        self.model_name = model_name
        self.temperature = temperature
        self.agents = MultiAgents(self.__initialize_llm())

    def __initialize_llm(self):
        """
        Inicializa o LLM usando o ChatOpenAI da LangChain
        """
        llm = ChatOpenAI(
            api_key=SecretStr(self.api_key),
            model=self.model_name,
            temperature=self.temperature
        )
        return llm

    def create_newsletter(self, newsletter: dict) -> str:
        """
        Divide o tópico em sub-assuntos e gera JSON no formato NewsletterArticleModel
        """
        # Convertemos o dict em string para enviar no prompt
        newsletter_str = json.dumps(newsletter, indent=2)
        system_message = f"""
        Você é um assistente de curadoria de notícias. 
        Você recebe notícias já prontas, resume elas em +5 tópicos importantes com +3 parágrafos cada e cria um JSON de noticia completo.
        Você sempre retornar o JSON.
        Você é técnico e especialista no assunto.
        Você é detalhista.
        Você escreve de forma humana e em português bom.
        Você escreverá em cada parágrafo de cada tópico um texto super rico.
        Você nunca retorna nada além do JSON.

        """
        prompt_text = f"""
        CRIE UMA NOVA NOTÍCIA A PARTIR DESSA:
        "{newsletter_str}"
        
        ______________
        O JSON deve conter:
            - title: título resumido
            - description: resumo geral
            - topics: lista de tópicos com title, index e parágrafos
            - source: nome e url da fonte
            
        IMPORTANTE:
            - Nunca responda "I don't know".
            - Sempre gere um JSON válido no formato do schema.
        """

        result = self.agents.json_manager_agent(system_message).invoke({"input": prompt_text})

        return result["output"]

