from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def move_part2_keyboard(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Yes ✅", callback_data=f"move_part2:{user_id}")
    keyboard.add(button1)

    return keyboard


def move_part3_keyboard(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Yes ✅", callback_data=f"move_part3:{user_id}")
    keyboard.add(button1)

    return keyboard
