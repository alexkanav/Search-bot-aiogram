import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from handlers.commands import router as common_router
from handlers.data_collector import router as collector_router
from handlers.database import router as database_router
from handlers.items import router as item_router
from infrastructure.logging_config import configure_logging
from infrastructure.rabbitmq import RabbitMQ
from infrastructure.redis import create_redis_client
from services.notification_service import notify_user
from services.search_service import SearchService
from settings import Settings
from setup_commands import set_commands


async def main() -> None:
    settings = Settings()
    configure_logging(settings.log_file_path, logging.INFO)

    redis_client = await create_redis_client(settings.redis_url)
    storage = RedisStorage(redis_client) if redis_client else MemoryStorage()

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher(storage=storage)

    rabbitmq = RabbitMQ(str(settings.RABBITMQ_URL))
    await rabbitmq.connect()
    consumer_tag = await rabbitmq.consume(
        "search_result",
        notify_user,
        bot,
    )
    search_service = SearchService(
        base_url=settings.SEARCH_SERVICE_URL,
        token=settings.SERVICE_TOKEN,
        redis=redis_client,
    )

    dp["rabbitmq"] = rabbitmq
    dp["search_service"] = search_service

    dp.include_router(common_router)
    dp.include_router(item_router)
    dp.include_router(collector_router)
    dp.include_router(database_router)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await rabbitmq.close()

        if redis_client:
            await redis_client.aclose()

        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
