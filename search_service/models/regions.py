from pydantic import BaseModel, HttpUrl


class RegionRequest(BaseModel):
    url: HttpUrl


class RegionsResponse(BaseModel):
    regions: list[str]
