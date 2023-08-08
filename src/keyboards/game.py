from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_field_keyboard(field) -> InlineKeyboardMarkup:
    keyboard = []
    for i, line in enumerate(field):
        line_buttons = []
        for j, cell in enumerate(line):
            button = InlineKeyboardButton(text=cell.get_my_display(), callback_data=f"None{i}{j}")
            line_buttons.append(button)
        keyboard.append(line_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_radar_keyboard(field) -> InlineKeyboardMarkup:
    keyboard = []
    for i, line in enumerate(field):
        line_buttons = []
        for j, cell in enumerate(line):
            button = InlineKeyboardButton(text=cell.get_enemy_display(), callback_data=f"shot/{i} {j}")
            line_buttons.append(button)
        keyboard.append(line_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
