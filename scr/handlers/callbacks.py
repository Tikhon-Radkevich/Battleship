from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import Text

from game.game import Lobby, BattleshipConstructor, BattleshipGame


router = Router()


@router.callback_query(text="create_battleship_lobby")
async def create_lobby(callback: CallbackQuery, bot: Bot):
    lobby_id = callback.message.chat.id
    player_id = lobby_id
    Lobby(lobby_id)
    await Lobby.add_player(lobby_id, player_id, bot)
    await callback.answer()


@router.callback_query(text="create_battleship_constructor")
async def create_constructor(callback: CallbackQuery):
    lobby_id = callback.data.split("/")[-1]
    constructor = BattleshipConstructor(int(lobby_id))
    for player_id in constructor.players:
        await constructor.show_constructor(player_id)
    await callback.answer()


@router.callback_query(Text(text_startswith="chose_ship"))
async def chose_ship(callback: CallbackQuery):
    ship_name = callback.data.split("/")[-1]
    player_id = callback.message.chat.id
    await BattleshipConstructor.chose_ship(player_id, ship_name)
    await callback.answer()


@router.callback_query(Text(text_startswith="put_or_remove_ship"))
async def put_or_remove_ship(callback: CallbackQuery):
    # try to add ship if the ship is chosen else try to remove ship
    coords = callback.data.split("/")[-1]
    player_id = callback.message.chat.id
    await BattleshipConstructor.put_or_remove_ship(player_id, coords)
    await callback.answer()


@router.callback_query(Text(text_startswith="turn_ship"))
async def turn_ship(callback: CallbackQuery):
    player_id = callback.message.chat.id
    await BattleshipConstructor.turn_ship(player_id)
    await callback.answer()


@router.callback_query(Text(text_startswith="ready_for_battleship"))
async def ready_for_battleship(callback: CallbackQuery, bot: Bot):
    player_id = callback.message.chat.id
    await BattleshipConstructor.ready_for_battleship(player_id, bot)
    await callback.answer()


@router.callback_query(Text(text_startswith="shot"))
async def make_shot(callback: CallbackQuery, bot: Bot):
    coords = callback.data.split("/")[-1]
    player_id = callback.message.chat.id
    await BattleshipGame.make_shot(int(player_id), coords, bot)
    await callback.answer()
