from pydantic import BaseModel, HttpUrl


class LocationsRequest(BaseModel):
    region: str
    url: HttpUrl


class LocationsResponse(BaseModel):
    locations: list[str]


