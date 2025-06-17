from pydantic import BaseModel


class NewAIBase(BaseModel):
    title: str
    link: str
    pubDate: str
    text: str


class NewRequest(NewAIBase):
    pass
