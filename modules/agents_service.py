import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)



class MultiAgents:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def json_manager_agent(self, system_message:str):
        """
        Cria um parser direto para NewsletterArticleModel
        """

        return self._create_simple_agent(
                llm=self.llm,
                system_message=system_message,
            )

    @staticmethod
    def _create_simple_agent(llm: BaseChatModel, system_message: str):
        """Cria um agente simples sem ferramentas para processamento de texto."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}")
        ])

        class SimpleAgent:
            """Agente simples que formata prompt e chama o LLM."""

            def __init__(self):
                self.llm = llm
                self.prompt = prompt

            def invoke(self, inputs: dict):
                """Chama o LLM com o prompt formatado."""
                messages = self.prompt.format_messages(**inputs)
                logger.debug("Invocando LLM (messages=%d)", len(messages))
                response = self.llm.invoke(messages)
                output = self._extract_text(response)
                if not output.strip():
                    logger.warning("Resposta do LLM vazia")
                    raise ValueError("Resposta do LLM vazia ou invalida.")
                logger.debug("Resposta do LLM recebida (chars=%d)", len(output))
                return {"output": output}

            @staticmethod
            def _extract_text(response) -> str:
                content = getattr(response, "content", None)
                if content:
                    return str(content)
                text_attr = getattr(response, "text", None)
                if text_attr:
                    return str(text_attr)
                extra = getattr(response, "additional_kwargs", {}) or {}
                if isinstance(extra, dict):
                    for key in ("text", "content"):
                        if extra.get(key):
                            return str(extra[key])
                logger.debug("Nao foi possivel extrair texto da resposta do LLM")
                return ""

        return SimpleAgent()