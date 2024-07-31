import asyncio
import logging
from typing import Union

from aiogram import Bot
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated, RetryAfter, TelegramAPIError
from aiogram.types import InlineKeyboardMarkup


async def send_message(
        bot: Bot,
        user_id: Union[int, str],
        text: str,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None,
) -> bool:
    """
    Safe messages sender

    :param bot: Bot instance.
    :param user_id: user id. If str - must contain only digits.
    :param text: text of the message.
    :param disable_notification: disable notification or not.
    :param reply_markup: reply markup.
    :return: success.
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification, reply_markup=reply_markup)
    except BotBlocked:
        logging.error(f"Target [ID:{user_id}]: got BotBlocked")
    except ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: got ChatNotFound")
    except UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: got ChatNotFound")
    except RetryAfter as e:
        logging.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(bot, user_id, text, disable_notification, reply_markup)  # Recursive call
    except TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcast(
        bot: Bot,
        users: list[Union[str, int]],
        text: str,
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None,
) -> int:
    """
    Simple broadcaster.
    :param bot: Bot instance.
    :param users: List of users.
    :param text: Text of the message.
    :param disable_notification: Disable notification or not.
    :param reply_markup: Reply markup.
    :return: Count of messages.
    """
    count = 0
    try:
        for user_id in users:
            if await send_message(bot, user_id, text, disable_notification, reply_markup):
                count += 1
            await asyncio.sleep(0.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count


async def main():
    from loader import bot, db
    # users = await User.all().values_list('id', flat=True)
    # await broadcast(bot, users, 'test')
    pass
