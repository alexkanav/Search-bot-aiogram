from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]

    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_multiline_keyboard(items: list[str], buttons_per_row: int) -> ReplyKeyboardMarkup:
    if buttons_per_row <= 0:
        raise ValueError("buttons_per_row must be greater than 0")

    builder = ReplyKeyboardBuilder()
    for item in items:
        builder.add(KeyboardButton(text=item))
    builder.adjust(buttons_per_row)

    return builder.as_markup(resize_keyboard=True)
