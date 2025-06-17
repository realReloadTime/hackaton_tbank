from pydantic import BaseModel
from typing import Optional


class NewAIBase(BaseModel):
    title: Optional[str]
    link: str
    pubDate: Optional[str]
    text: str


class NewRequest(NewAIBase):
    pass
