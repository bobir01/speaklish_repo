from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def get_pre_test_btn():
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text="Start now ✅", callback_data="pre_test-start_now")
    # later start
    button2 = InlineKeyboardButton(text="Later ❌", callback_data="pre_test-later")
    keyboard.add(button1, button2)
    return keyboard


def get_phone_btn():
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton(text="Send phone number 📱", request_contact=True)
    keyboard.add(button)
    return keyboard
