from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def make_row_keyboard(items: list[str]):
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_multiline_keyboard(items, number_of_lines):
    builder = ReplyKeyboardBuilder()
    for i in items:
        builder.add(KeyboardButton(text=str(i)))
    builder.adjust(number_of_lines)
    return builder.as_markup(resize_keyboard=True)


def make_row_inline_keyboard(items):
    builder = InlineKeyboardBuilder()
    for i in items:
        if list(items[i].keys())[0] == 'url':
            builder.row(InlineKeyboardButton(
                    text=i, url=items[i].get('url'))
                )
        if list(items[i].keys())[0] == 'callback_data':
            builder.row(InlineKeyboardButton(
                    text=i, callback_data=items[i].get('callback_data'))
                )
    return builder.as_markup()
