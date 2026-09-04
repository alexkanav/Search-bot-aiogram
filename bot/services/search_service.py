import json
import logging
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, HttpUrl
from redis.asyncio import Redis
from redis.exceptions import RedisError

from config import REGIONS_ENDPOINT, LOCATIONS_ENDPOINT, CACHE_TTL
from models.locations import LocationsRequest, LocationsResponse
from models.regions import RegionsRequest, RegionsResponse

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
            self,
            base_url: HttpUrl,
            token: str,
            redis: Redis | None,
    ) -> None:
        self.base_url = str(base_url)
        self.token = token
        self.redis = redis

    async def post_json[T1: BaseModel, T2: BaseModel](
            self,
            endpoint: str,
            payload: T1,
            response_model: type[T2],
    ) -> T2:
        timeout = httpx.Timeout(
            connect=5.0,
            read=20.0,
            write=5.0,
            pool=5.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                urljoin(self.base_url, endpoint),
                json=payload.model_dump(mode="json"),
                headers={"Authorization": f"Bearer {self.token}"},
            )

        response.raise_for_status()
        return response_model.model_validate(response.json())

    async def get_cache(self, cache_key: str) -> list[str] | None:
        try:
            cached = await self.redis.get(cache_key)

            if cached is None:
                return None

            return json.loads(cached)

        except (RedisError, json.JSONDecodeError) as e:
            logger.warning("Failed to fetch data from cache: %s", e)
            return None

    async def set_cache(self, cache_key: str, data: str) -> None:
        try:
            await self.redis.set(
                cache_key,
                data,
                ex=CACHE_TTL,
            )
        except RedisError as e:
            logger.warning("Failed to cache data: %s", e)

    async def get_regions(self, target_url: str) -> list[str]:
        cache_key = f"regions:{target_url}"

        if self.redis:
            cached = await self.get_cache(cache_key)

            if cached is not None:
                return cached

        try:
            response = await self.post_json(
                REGIONS_ENDPOINT,
                RegionsRequest(
                    url=target_url,
                ),
                RegionsResponse,
            )
            regions = response.regions

        except httpx.HTTPError as e:
            logger.warning("Failed to fetch regions: %s", e)
            return []

        if regions and self.redis:
            await self.set_cache(cache_key, json.dumps(regions))

        return regions

    async def get_locations(
            self,
            target_url: str,
            region: str,
    ) -> list[str]:
        cache_key = f"locations:{region}:{target_url}"

        if self.redis:
            cached = await self.get_cache(cache_key)

            if cached is not None:
                return cached

        try:
            response = await self.post_json(
                LOCATIONS_ENDPOINT,
                LocationsRequest(
                    region=region,
                    url=target_url,
                ),
                LocationsResponse,
            )
            locations = response.locations

        except httpx.HTTPError as e:
            logger.warning("Failed to fetch locations: %s", e)
            return []

        if locations and self.redis:
            await self.set_cache(cache_key, json.dumps(locations))

        return locations
