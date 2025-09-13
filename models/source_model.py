from pydantic.v1 import BaseModel


class SourceModel(BaseModel):
    """
    name: Source name
    url: Source url
    """
    name:str
    url:str