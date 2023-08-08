from aiogram import Router, Bot
from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

from game.game import Lobby


router = Router()


@router.inline_query()
async def inline_handler(query: InlineQuery):
    name = query.from_user.first_name
    link = Lobby.get_invite_link(query.from_user.id)
    invite_button = [InlineKeyboardButton(text="✔Accept", url=link, callback_data=f"invite message")]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[invite_button])
    text = f"{name} invites you to play Battleship!"
    pict = "https://www.leak.pt/wp-content/uploads/2021/04/radr.webp"
    item = InlineQueryResultArticle(
        id=str(query.from_user.id),
        title="Battleship1",
        description="Invite a friend to play",
        thumb_url=pict,
        reply_markup=keyboard,
        input_message_content=InputTextMessageContent(
            message_text=text
        )
    )
    return await query.answer([item], cache_time=20, is_personal=True)
