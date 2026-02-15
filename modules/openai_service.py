import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover - optional dependency
    ChatGoogleGenerativeAI = None

from models.newsletter_bot_json_article import NewsletterArticleModel
from modules.agents_service import MultiAgents

logger = logging.getLogger(__name__)


class NewsLetterBot:
    def __init__(
        self,
        openai_api_key: str | None = None,
        gemini_api_key: str | None = None,
        model_name: str = "gpt-4.1-mini-2025-04-14",
        gemini_model_name: str = "gemini-2.0-flash-lite",
        temperature: float = 0.7,
        llm_provider: str | None = None,
    ):
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        self.gemini_model_name = gemini_model_name
        self.temperature = temperature
        self.llm_provider = (llm_provider or "auto").lower()
        logger.info("Inicializando NewsLetterBot (provider=%s)", self.llm_provider)
        self.agents = MultiAgents(self._initialize_llm())

    def _initialize_llm(self) -> BaseChatModel:
        provider = self._select_provider()
        logger.info("LLM selecionado: %s", provider)
        if provider == "openai":
            logger.debug("Usando OpenAI model=%s temperature=%.2f", self.model_name, self.temperature)
            return ChatOpenAI(
                api_key=SecretStr(self.openai_api_key),
                model=self.model_name,
                temperature=self.temperature,
            )
        if provider == "gemini":
            if ChatGoogleGenerativeAI is None:
                raise RuntimeError(
                    "langchain-google-genai nao esta instalado; instale para usar Gemini."
                )
            logger.debug("Usando Gemini model=%s temperature=%.2f", self.gemini_model_name, self.temperature)
            return ChatGoogleGenerativeAI(
                google_api_key=self.gemini_api_key,
                model=self.gemini_model_name,
                temperature=self.temperature,
            )
        raise ValueError(f"Provedor LLM desconhecido: {provider}")

    def _select_provider(self) -> str:
        if self.llm_provider in {"openai", "gemini"}:
            logger.info("LLM provider forçado: %s", self.llm_provider)
            self._validate_provider_key(self.llm_provider)
            return self.llm_provider

        if self.openai_api_key:
            logger.info("LLM provider auto: openai")
            return "openai"
        if self.gemini_api_key:
            logger.info("LLM provider auto: gemini")
            return "gemini"

        raise ValueError("Nenhuma chave LLM encontrada (OPENAI_API_KEY ou GEMINI_API_KEY).")

    def _validate_provider_key(self, provider: str) -> None:
        if provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY nao configurada para usar OpenAI.")
        if provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY nao configurada para usar Gemini.")

    def create_newsletter(self, newsletter: dict) -> str:
        """
        Divide o tópico em sub-assuntos e gera JSON no formato NewsletterArticleModel
        """
        # Convertemos o dict em string para enviar no prompt
        newsletter_str = json.dumps(newsletter, indent=2)
        logger.debug("Gerando newsletter (input_chars=%d)", len(newsletter_str))
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
        output = result["output"]
        logger.debug("Newsletter gerada (output_chars=%d)", len(output))
        return output

