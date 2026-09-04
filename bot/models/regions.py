from pydantic import BaseModel, HttpUrl


class RegionsRequest(BaseModel):
    url: HttpUrl


class RegionsResponse(BaseModel):
    regions: list[str]
