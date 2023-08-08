from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_invite_keyboard() -> InlineKeyboardMarkup:
    button = [InlineKeyboardButton(text="Invite friend", switch_inline_query="")]
    return InlineKeyboardMarkup(inline_keyboard=[button])
