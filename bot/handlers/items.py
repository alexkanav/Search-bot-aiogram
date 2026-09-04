from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import config
import keyboards
from constants import SEARCH_BUTTON, IMPORT_BUTTON, UNSUPPORTED_BUTTON_MESSAGE
from states import SearchFlow

router = Router()


@router.message(SearchFlow.selecting_item, F.text)
async def process_search_query(message: Message, state: FSMContext) -> None:
    await state.update_data(query=message.text.strip().lower())
    await message.answer(
        text="Оберіть дію: Новий пошук або Імпорт з базІ даних?",
        reply_markup=keyboards.make_row_keyboard([SEARCH_BUTTON, IMPORT_BUTTON]),
    )
    await state.set_state(SearchFlow.selecting_action)


@router.message(SearchFlow.selecting_action, F.text)
async def process_action_choice(message: Message, state: FSMContext) -> None:
    if message.text == SEARCH_BUTTON:
        await message.answer(
            "Виберіть Маркетплейс:",
            reply_markup=keyboards.make_multiline_keyboard(list(config.MARKETPLACE_URLS), 4),
        )
        await state.set_state(SearchFlow.selecting_marketplace)
        return

    if message.text == IMPORT_BUTTON:
        await message.answer(
            text="Введіть ID конкретної картки або 0 для пошуку всіх ID в базі даних?",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(SearchFlow.selecting_db_query)
        return

    await message.answer(UNSUPPORTED_BUTTON_MESSAGE)
