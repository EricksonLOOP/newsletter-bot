from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



class MultiAgents:
    def __init__(self, llm: ChatOpenAI):
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
    def _create_simple_agent(llm: ChatOpenAI, system_message: str):
        """Cria um agente simples sem ferramentas para processamento de texto."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("system", "{input}")
        ])

        class SimpleAgent:
            """Agente simples que formata prompt e chama o LLM."""

            def __init__(self):
                self.llm = llm
                self.prompt = prompt

            def invoke(self, inputs: dict):
                """Chama o LLM com o prompt formatado."""
                messages = self.prompt.format_messages(**inputs)
                response = self.llm.invoke(messages)
                return {"output": response.content}

        return SimpleAgent()