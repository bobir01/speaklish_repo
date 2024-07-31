from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_pronunciation_form(user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="Yes ✅, Let's go", callback_data=f"pronunciation:{user_id}")
    button2 = InlineKeyboardButton(text="No ❌, I am not at quite place", callback_data=f"pronunciation_cancel:{user_id}")
    keyboard.add(button1, button2)

    return keyboard
