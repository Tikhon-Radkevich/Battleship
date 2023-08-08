from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_constructor_keyboard(field, ships, ship_for_putting) -> InlineKeyboardMarkup:
    keyboard = []
    for i, line in enumerate(field):
        line_buttons = []
        for j, cell in enumerate(line):
            button = InlineKeyboardButton(text=cell.get_my_display(), callback_data=f"put_or_remove_ship/{i} {j}")
            line_buttons.append(button)
        keyboard.append(line_buttons)
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    for ship in ships:
        text = f"{ship.get('name')} - {ship.get('count')}"
        button = InlineKeyboardButton(text=text, callback_data=f"chose_ship/{ship.get('name')}")
        keyboard.inline_keyboard.append([button])
    turn_ship_button = InlineKeyboardButton(text="Turn", callback_data="turn_ship")
    keyboard.inline_keyboard.append([turn_ship_button])
    if not ships and not ship_for_putting:
        ready_button = InlineKeyboardButton(text="Ready", callback_data="ready_for_battleship")
        keyboard.inline_keyboard.append([ready_button])
    return keyboard
