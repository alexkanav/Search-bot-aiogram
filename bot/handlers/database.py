from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.rabbitmq import RabbitMQ
from models.items import ItemParams
from states import SearchFlow
from utils.card import is_valid_card_id

router = Router()


@router.message(SearchFlow.selecting_db_query, F.text)
async def process_db_query(
        message: Message,
        state: FSMContext,
        rabbitmq: RabbitMQ,
) -> None:
    card_id = message.text.strip()
    if not is_valid_card_id(card_id):
        await message.answer(
            "Помилка. Ви ввели некоректний ID картки.",
        )
        return

    data = await state.get_data()
    item_params = ItemParams(
        card_id=card_id,
        chat_id=message.chat.id,
        query=data["query"],
    )

    await message.answer(
        text="Почекайте, завантажую...",
    )

    await rabbitmq.publish(
        queue="db_request",
        body=item_params.model_dump(mode="json"),
    )

    await state.clear()
