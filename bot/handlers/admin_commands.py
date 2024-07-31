import aiogram.utils.exceptions
from aiogram.types import Message
import asyncio
import logging
from datetime import datetime

import requests
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from loader import dp, config, cache, bot, db


@dp.message_handler(commands=['temp'], user_id=config.admins[0])
async def temp(message: Message):
    args = message.get_args()
    if args:
        await message.answer(f'temp {config.open_ai_temp} -> {args}')
        config.open_ai_temp = float(args)
    else:
        await message.answer(f'temp {config.open_ai_temp} -> 0.5')
        config.open_ai_temp = 0.5


