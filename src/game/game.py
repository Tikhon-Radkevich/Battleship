import logging

from random import sample, choice

from src.game.game_errors import ConstructorErrors, GameErrors
from src.keyboards.constructor import get_constructor_keyboard
from src.keyboards.game import get_field_keyboard, get_radar_keyboard
from src.keyboards.general import get_invite_keyboard
from src.game.battleship import Field


class Player:
    PLAYERS = {}

    def __init__(self, player_id, player_name, bot):
        self.bot = bot
        self.PLAYERS[player_id] = self
        self.player_id = player_id
        self.name = player_name
        self.field_message_id = None
        self.radar_message_id = None
        self.field = None
        self.game = None

    def __str__(self):
        return f"{self.__class__}: id {self.player_id}"

    async def show_constructor(self):
        field, ships = self.field.show()
        ship_for_putting = self.field.ship_for_putting
        keyboard = get_constructor_keyboard(field, ships, ship_for_putting)
        text = self.__get_text_for_constructor(ship_for_putting)
        try:
            await self.bot.edit_message_text(
                text=text, chat_id=self.player_id, message_id=self.field_message_id, reply_markup=keyboard)
        except Exception as e:
            logging.error(str(e))

    def get_display_buttons(self):
        field, _ = self.field.show()
        keyboard = get_field_keyboard(field)
        return keyboard

    def get_radar_buttons(self):
        field, _ = self.field.show()
        keyboard = get_radar_keyboard(field)
        return keyboard

    @classmethod
    def __get_text_for_constructor(cls, ship_for_putting):
        if ship_for_putting:
            length = ship_for_putting.length
            if ship_for_putting.directions == ship_for_putting.HORIZONTAL:
                text = f"{ship_for_putting.name} \n{'🟦'*length + '⬅'}"
            else:
                ship_instr = "⬇ \n" + '🟦 \n' * length
                text = f"{ship_for_putting.name}: \n{ship_instr}"
        else:
            text = "chose the ship"
        return text


class Lobby:
    LOBBIES = {}

    def __init__(self, lobby_id):
        self.lobby_id = int(lobby_id)
        self.players = {}
        Lobby.LOBBIES[lobby_id] = self

    @classmethod
    async def create_constructor(cls, lobby_id):
        constructor = BattleshipConstructor(int(lobby_id))
        for player_id in constructor.players:
            await constructor.show_constructor(player_id)

    @classmethod
    async def show_info(cls, lobby_id, bot):
        lobby = cls.LOBBIES.get(lobby_id)
        player_names = "\n".join([player.name for player in lobby.players.values()])
        keyboard = get_invite_keyboard()
        for player_id in lobby.players:
            mess = await bot.send_message(text=player_names, chat_id=player_id, reply_markup=keyboard)
            lobby.players[player_id].field_message_id = mess.message_id

    @classmethod
    async def add_player(cls, lobby_id: int, player_id: int, bot):
        lobby = cls.LOBBIES.get(lobby_id)
        if len(lobby.players) < 2:
            player = Player.PLAYERS.get(player_id)
            lobby.players[player_id] = player
            player.game = lobby
            await cls.show_info(lobby_id, bot)
            if len(lobby.players) == 2:
                return await cls.create_constructor(lobby_id)

    @classmethod
    def get_members(cls, lobby_id):
        lobby = cls.LOBBIES.get(lobby_id)
        return lobby.players.values()

    @classmethod
    def get_invite_link(cls, lobby_id):
        link = f"https://t.me/Battle_ship_game_bot?start=join_battleship_{lobby_id}"
        return link


class BattleshipConstructor:
    CONSTRUCTORS = {}

    def __init__(self, lobby_id: int):
        self.players = {}
        self._add_players(lobby_id)
        self.ready_players = []

    @classmethod
    async def put_or_remove_ship(cls, player_id, coords):
        constructor = cls.CONSTRUCTORS.get(player_id)
        field = constructor.players.get(player_id).field
        try:
            field.put_the_ship(coords)
        except ConstructorErrors.FieldWasSaved:
            return
        except (ConstructorErrors.NoChosenShip, ConstructorErrors.ForbiddenCellForShip):
            try:
                field.remove_the_ship(coords)
            except ConstructorErrors.NoShipOnCell:
                return
        await cls.show_constructor(player_id)

    @classmethod
    async def chose_ship(cls, player_id, ship_name):
        constructor = cls.CONSTRUCTORS.get(player_id)
        field = constructor.players.get(player_id).field
        field.chose(ship_name)
        await cls.show_constructor(player_id)

    @classmethod
    async def turn_ship(cls, player_id):
        constructor = cls.CONSTRUCTORS.get(player_id)
        field = constructor.players.get(player_id).field
        field.turn_ship()
        await cls.show_constructor(player_id)

    @classmethod
    async def show_constructor(cls, player_id):
        player = Player.PLAYERS.get(player_id)
        await player.show_constructor()

    @classmethod
    async def ready_for_battleship(cls, player_id, bot):
        constructor = cls.CONSTRUCTORS[player_id]
        player = constructor.players[player_id]
        player.field.saved = True
        constructor.ready_players.append(player)
        if len(constructor.ready_players) < 2:
            await bot.edit_message_text(
                text="Waiting for an opponent...", chat_id=player_id, message_id=player.field_message_id)
        else:
            BattleshipGame(constructor.players, bot)
            await BattleshipGame.show(player_id, bot)

    def _add_players(self, lobby_id):
        lobby = Lobby.LOBBIES.get(lobby_id)
        self.players = lobby.players
        for player_id in self.players.keys():
            self.CONSTRUCTORS[int(player_id)] = self
        self._add_fields()

    def _add_fields(self):
        for player_id in self.players:
            field = Field()
            setattr(self.players[player_id], "field", field)


class BattleshipGame:
    WIN_STICKERS = [
        "CAACAgIAAxkBAAEFq0hjB0StFxIJHKTeXHrpQYcdkUGX1QACmiAAAtcciEi5pUupwFI8bikE",
        "CAACAgIAAxkBAAEFq1JjB0UrOJ_Q9oTGH9tSfNTP-8VAMwACwRkAAkTFiEhwA2dCxITSQykE",
        "CAACAgIAAxkBAAEFq1djB0VXcbvFcCv3nw92E7DT6iu4SgACrxsAApY7uhcxMzPwuOWMCykE",
        "CAACAgIAAxkBAAEFq2xjB0Y8mHUVau-QZbbzjr6UeYpHRQACwBsAApY7uhfw79-ZUS4_KykE",
    ]
    LOSE_STICKERS = [
        "CAACAgIAAxkBAAEFq2BjB0WRazi1Rc8rPD222BzgMFRDLQACQhkAArvgiUgqL2zYc0O9EikE",
        "CAACAgIAAxkBAAEFq2JjB0WfDKjEVJ0DKRc1DGXP9bLpagACsBsAApY7uhdbigH-SKAneikE",
        "CAACAgIAAxkBAAEFq25jB0ZjcGEBWHBkhY84aVXQSaFhywACsRsAApY7uheiI6DhNjzQXykE"
    ]

    def __init__(self, players, bot):
        self.bot = bot
        self.players = players
        self.__set_game()
        self.current_step_player = None
        self.next_step_player = None
        self.__set_steps()

    @classmethod
    async def make_shot(cls, player_id: int, coords, bot):
        player = Player.PLAYERS.get(player_id)
        game = player.game
        if game.current_step_player != player:
            return
        enemy = game.next_step_player
        try:
            enemy.field.shot(coords)
            game.current_step_player, game.next_step_player = game.next_step_player, game.current_step_player
        except GameErrors.ShipHit:
            pass
        except GameErrors.KilledCell:
            return
        except GameErrors.GameOver:
            await cls.show(player_id, bot)
            await cls.game_over(player_id, bot)
            return
        await cls.show(player_id, bot)

    @classmethod
    async def show(cls, player_id, bot):
        game = Player.PLAYERS.get(player_id).game
        for player in game.players.values():
            players = list(game.players.values())
            players.remove(player)
            enemy = players[0]
            radar_keyboard = enemy.get_radar_buttons()
            await cls.__send_field_and_radar(player, radar_keyboard, game.current_step_player, bot)

    @classmethod
    async def game_over(cls, player_id, bot):
        game = Player.PLAYERS.get(player_id).game
        winner = game.current_step_player
        loser = game.next_step_player
        win_text = "You won!"
        lose_text = "You lose :("
        winner_keyboard = loser.get_display_buttons()
        loser_keyboard = winner.get_display_buttons()
        win_sticker = choice(cls.WIN_STICKERS)
        lose_sticker = choice(cls.LOSE_STICKERS)
        messages = [
            (winner, win_text, winner_keyboard, win_sticker),
            (loser, lose_text, loser_keyboard, lose_sticker)
        ]
        for (p, t, k, s) in messages:
            m = await bot.edit_message_text(text=t, chat_id=p.player_id, message_id=p.radar_message_id, reply_markup=k)
            await bot.send_sticker(chat_id=p.player_id, sticker=s, reply_to_message_id=m.message_id)

    @classmethod
    async def __send_field_and_radar(cls, player, radar_keyboard, current_step_player, bot):
        field_keyboard = player.get_display_buttons()
        field_mess_id = player.field_message_id
        radar_mess_id = player.radar_message_id
        chat_id = player.player_id
        if player == current_step_player:
            step = "🟢 Your step"
        else:
            step = "🔴 Enemy step"
        field_text = "Your field"
        radar_text = f"Radar \t{step}"
        try:
            await bot.edit_message_text(field_text, chat_id, field_mess_id, reply_markup=field_keyboard)
        except Exception as e:
            logging.error(str(e))
        if radar_mess_id:
            try:
                await bot.edit_message_text(radar_text, chat_id, radar_mess_id, reply_markup=radar_keyboard)
            except Exception as e:
                logging.error(str(e))
        else:
            mess = await bot.send_message(text=radar_text, chat_id=chat_id, reply_markup=radar_keyboard)
            player.radar_message_id = mess.message_id

    def __set_game(self):
        for player in self.players.values():
            player.game = self

    def __set_steps(self):
        self.current_step_player, self.next_step_player = sample(list(self.players.values()), k=2)
