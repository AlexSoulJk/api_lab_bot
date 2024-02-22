from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_keyboard(buttons: list[tuple[str, CallbackData]], adjust=(1,)):
    builder = InlineKeyboardBuilder()
    print(buttons)
    for title, callback_data in buttons:
        builder.button(text=title, callback_data=callback_data)
    builder.adjust(*adjust)

    return builder.as_markup()

def get_keyboard_reply(buttons: list[str], adjust=(1,)):
    # buttons: [("text", Admin)]
    builder = ReplyKeyboardBuilder()
    print(buttons)
    for title in buttons:
        builder.button(text=title)
    builder.adjust(*adjust)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True, selective=True)