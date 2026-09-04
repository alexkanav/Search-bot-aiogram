import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.logging_config import configure_logging
from infrastructure.mongo_repository import create_mongodb_repository
from infrastructure.rabbitmq import RabbitMQ
from routes import router
from scraper.marketplace_scraper import MarketplaceScraper
from services.search_control import SearchService
from services.task_manager import TaskManager
from settings import Settings

app_settings = Settings()

configure_logging(app_settings.log_file_path, logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scraper = None
    mongo_client = None
    rabbit = None

    try:
        scraper = await MarketplaceScraper.create()
        app.state.scraper = scraper

        repository, mongo_client = await create_mongodb_repository(
            app_settings
        )

        task_manager = TaskManager()

        rabbit = RabbitMQ(str(app_settings.RABBITMQ_URL))
        await rabbit.connect()

        service = SearchService(
            repository,
            scraper,
            rabbit,
            task_manager,
        )

        await rabbit.consume(
            "search_request",
            service.search_handle,
        )

        await rabbit.consume(
            "db_request",
            service.repository_handler,
        )

        yield

    finally:
        if rabbit:
            await rabbit.close()

        if scraper:
            await scraper.close()

        if mongo_client:
            mongo_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
