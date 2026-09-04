from pydantic import BaseModel, Field, HttpUrl

from models.items import ItemCard
from utils.enums import Command


class SearchParams(BaseModel):
    command: Command
    chat_id: int
    url: HttpUrl
    query: str
    region: str | None = None
    location: str | None = None
    max_price: int | None = Field(default=None, ge=0)
    timeout: int | None = Field(default=None, ge=0)


class SearchResult(BaseModel):
    items: list[ItemCard]