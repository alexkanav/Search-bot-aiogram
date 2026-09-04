from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from constants import SEARCH_BUTTON, CANCEL_BUTTON
from keyboards import make_row_keyboard
from states import SearchFlow


async def start_search_flow(message: Message, state: FSMContext) -> None:
    await message.answer(text="Що шукаєте?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SearchFlow.selecting_item)


async def cancel_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text="Дію відхилено.", reply_markup=ReplyKeyboardRemove())


async def stop_search(
        message: Message,
        state: FSMContext,
) -> None:
    await state.clear()

    await message.answer(
        text="Пошук зупинено.\nЗвертайтесь ще, в мене немає вихідних)",
        reply_markup=ReplyKeyboardRemove(),
    )


async def ask_for_action(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Оберіть дію",
        reply_markup=make_row_keyboard([SEARCH_BUTTON, CANCEL_BUTTON]),
    )
    await state.set_state(SearchFlow.confirming_search)
