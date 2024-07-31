from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.callback_data import CallbackData

# all needed data for callback_data :params
# part - section of speaking assessment int 1, 2 or 3
# qs_num - number of question in part of speaking assessment int 1, 2, 3, 4, 5, 6, 7, 8, 9 or 10
# topic - topic of question in part of speaking assessment str
# len - length of question in part of speaking assessment int 1, 2, 3, 4, 5, 6, 7, 8, 9 or 10
next_question_callback = CallbackData("next_qs_data", "part", "qs_num", "topic", 'len', 'user_id')


async def make_callback_data(part: int, qs_num: int, topic: str, len_: int, user_id: int):
    return next_question_callback.new(part=part, qs_num=qs_num, topic=topic, len=len_, user_id=user_id)


async def get_next_question_keyboard(part: int, qs_num: int, topic: str, len_: int, user_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton(text="Next ➡️", callback_data=await make_callback_data(part, qs_num, topic, len_, user_id))
    keyboard.add(button)

    return keyboard
