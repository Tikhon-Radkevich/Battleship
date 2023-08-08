from aiogram import Router, Bot
from aiogram.dispatcher.filters.command import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand

from src.game.game import Lobby, Player

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, bot: Bot):
    Player(message.chat.id, message.chat.first_name, bot)
    if "join_battleship" in message.text:
        lobby_id = message.text.split("_")[-1]
        await Lobby.add_player(int(lobby_id), message.chat.id, bot)
    else:
        text = "Hi! Create the game."
        battleship = [InlineKeyboardButton(text="Battleship", callback_data="create_battleship_lobby")]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[battleship])
        await message.answer(text, reply_markup=keyboard)


@router.message(Command(commands=["battleship"]))
async def cmd_get_battleship_invite_link(message: Message, bot: Bot):
    router.callback_query(CallbackQuery(data="create_battleship_lobby", message=message))


async def set_default_commands(bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Run Bot"),
        BotCommand(command="battleship", description="Create Game"),
    ])
