from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def open_app_kb(url: str) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text="Open RecallDeck", web_app=WebAppInfo(url=url))
    return InlineKeyboardMarkup(inline_keyboard=[[button]])
