import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_source import handlers

from config import token


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # If you do not specify storage, the default will be MemoryStorage
    dp = Dispatcher(storage=MemoryStorage())
    # bot = Bot(config.bot_token.get_secret_value())
    bot = Bot(token=token)
    dp.include_router(handlers.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
