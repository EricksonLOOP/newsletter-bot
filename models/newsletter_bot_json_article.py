from typing import List, ClassVar

from langchain_community.tools.json.tool import JsonSpec
from pydantic.v1 import BaseModel

from models.source_model import SourceModel
from models.topic_model import TopicModel


class NewsletterArticleModel(BaseModel):
    title: str
    description: str
    topics: List[TopicModel]
    source:SourceModel

