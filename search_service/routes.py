from fastapi import APIRouter, HTTPException, Request, Depends, Header

from config import TOKEN, REGIONS_ENDPOINT, LOCATIONS_ENDPOINT
from models.locations import LocationsRequest, LocationsResponse
from models.regions import RegionRequest, RegionsResponse
from scraper.marketplace_scraper import MarketplaceScraper


async def verify_token(
        authorization: str = Header(...),
) -> None:
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )


def get_scraper(request: Request) -> MarketplaceScraper:
    return request.app.state.scraper


router = APIRouter(
    dependencies=[Depends(verify_token)]
)


@router.post(REGIONS_ENDPOINT, response_model=RegionsResponse)
async def fetch_regions(
        data: RegionRequest,
        scraper: MarketplaceScraper = Depends(get_scraper),
) -> RegionsResponse:
    regions = await scraper.get_regions(data.url)
    return RegionsResponse(regions=regions)


@router.post(LOCATIONS_ENDPOINT, response_model=LocationsResponse)
async def fetch_locations(
        data: LocationsRequest,
        scraper: MarketplaceScraper = Depends(get_scraper),
) -> LocationsResponse:
    locations = await scraper.get_locations(
        data.region,
        data.url,
    )
    return LocationsResponse(locations=locations)
