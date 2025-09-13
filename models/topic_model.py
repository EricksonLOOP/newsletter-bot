from pydantic.v1 import BaseModel

class TopicModel(BaseModel):
    """
    title: Title of the topic
    paragraphs: list of paragraphs
    index: index of the topic in the newsletter e.g: 1 first topic, 2 second topic, etc.
    """
    title: str
    index:int
    paragraphs: list[str]