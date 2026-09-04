import logging

import aio_pika
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError

from models.search import SearchResult

logger = logging.getLogger(__name__)


async def notify_user(
        message: aio_pika.IncomingMessage,
        bot: Bot,
) -> None:
    result = SearchResult.model_validate_json(message.body)

    for item in result.items:
        text = (
            f"ID: {item.card_id}\n"
            f"Товар: {item.query}\n"
            f"Опис: {item.description}\n"
            f"Ціна: {item.price}\n"
            f"Опубліковано: {item.location_and_date}\n"
            f"Дивитись на сайті: {item.item_url}\n"
        )

        if item.image_url:
            try:
                await bot.send_photo(
                    chat_id=item.chat_id,
                    photo=str(item.image_url),
                    caption=text,
                )
                continue

            except TelegramBadRequest:
                logger.warning(
                    "Failed to send image for card %s, "
                    "falling back to text message",
                    item.card_id,
                )

        try:
            await bot.send_message(
                chat_id=item.chat_id,
                text=text,
            )

        except TelegramAPIError:
            logger.exception(
                "Failed to notify user about card %s",
                item.card_id,
            )
