from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def make_row_keyboard(items: list) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_multiline_keyboard(items: list, number_of_lines: int) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    for i in items:
        builder.add(KeyboardButton(text=str(i)))
    builder.adjust(number_of_lines)
    return builder.as_markup(resize_keyboard=True)


def make_row_inline_keyboard(items: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        text, data = list(item.items())[0]  # text is the button label, data is a dict
        if 'url' in data:
            builder.row(InlineKeyboardButton(text=text, url=data['url']))
        elif 'callback_data' in data:
            builder.row(InlineKeyboardButton(text=text, callback_data=data['callback_data']))
    return builder.as_markup()