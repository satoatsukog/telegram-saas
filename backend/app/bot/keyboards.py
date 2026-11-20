from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def open_app_kb(url: str, text: str = "Open RecallDeck") -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
    return InlineKeyboardMarkup(inline_keyboard=[[button]])
