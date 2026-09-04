import asyncio
import logging

import aio_pika

from infrastructure.mongo_repository import ItemRepository
from infrastructure.rabbitmq import RabbitMQ
from models.items import ItemParams
from models.search import SearchParams
from scraper.marketplace_scraper import MarketplaceScraper
from services.task_manager import TaskManager
from utils.enums import Command

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
            self,
            repository: ItemRepository,
            scraper: MarketplaceScraper,
            rabbit: RabbitMQ,
            task_manager: TaskManager,
    ) -> None:
        self.repository = repository
        self.scraper = scraper
        self.rabbit = rabbit
        self.task_manager = task_manager

    async def search_handle(self, message: aio_pika.IncomingMessage) -> None:
        search_params = SearchParams.model_validate_json(message.body)

        match search_params.command:
            case Command.START:
                self.start_monitoring(search_params)

            case Command.STOP:
                self.stop_search(search_params.chat_id)

    async def repository_handler(self, message: aio_pika.IncomingMessage) -> None:
        item_params = ItemParams.model_validate_json(message.body)
        if item_params.card_id != "0":
            items = await self.repository.get_item(item_params.chat_id, item_params.card_id)
        else:
            items = await self.repository.get_items(item_params.chat_id, item_params.query)

        await self.rabbit.publish(
            queue="search_result",
            body={
                "items": [
                    item.model_dump(mode="json")
                    for item in items
                ],
            },
        )

    def start_monitoring(
            self,
            search_params: SearchParams,
    ) -> None:
        self.task_manager.start(
            search_params.chat_id,
            self.run_monitoring(search_params)
        )

    def stop_search(self, chat_id: int) -> None:
        self.task_manager.cancel(chat_id)
        self.scraper.clear_seen_cards(chat_id)

    async def process_new_items(
            self,
            search_params: SearchParams
    ) -> None:
        new_items = await self.scraper.find_new_items(search_params)
        if not new_items:
            return

        await self.rabbit.publish(
            queue="search_result",
            body={
                "items": [
                    item.model_dump(mode="json")
                    for item in new_items
                ],
            },
        )

        await self.repository.insert_items(search_params.chat_id, new_items)

    async def run_monitoring(
            self,
            search_params: SearchParams,
    ) -> None:

        try:
            if not search_params.timeout:
                await self.process_new_items(search_params)
                return

            while True:
                await self.process_new_items(search_params)

                await asyncio.sleep(search_params.timeout * 60)

        except asyncio.CancelledError:
            logger.info("Stopped monitoring user %s", search_params.chat_id)

        except Exception:
            logger.exception("Monitoring failed for user %s", search_params.chat_id)
