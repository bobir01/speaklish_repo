import os
from handlers import *

from aiogram import executor, types
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from loader import dp, logger, bot, config, cache, db

# webhook settings
WEBHOOK_HOST = ''
WEBHOOK_PATH = '/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.environ.get('PORT')


async def on_startup(dp: dp):
    await bot.send_message(config.admins[0], "I am alive!")
    await db.create()
    await db.user_table_migrate()
    await bot.set_my_commands(
        [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help"),
            BotCommand("profile", "Profile and sessions info"),
            BotCommand("buy_sessions", "Buy sessions"),
            BotCommand("test", "Start speaking mock test"),
            BotCommand("cancel", "cancel current operation"),
        ],
        scope=BotCommandScopeAllPrivateChats()
    )
    # set admin commands
    await bot.set_my_commands(
        [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help"),
            BotCommand("cancel", "cancel current operation"),
            BotCommand("temp", "change temp / Admin only"),
            BotCommand("mode", "change mode / Admin only"),
            BotCommand("profile", "Profile and sessions info"),
            BotCommand("buy_sessions", "Buy sessions"),
            BotCommand("test", "Start speaking mock test"),

        ],
        scope=types.BotCommandScopeChat(chat_id=config.admins[0])
    )

    if not config.audio_dir.exists():
        config.audio_dir.mkdir()
    if config.debug or config.mode == 'dev':
        return logger.info("Bot started in polling mode")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f'starting webhook {WEBHOOK_URL}')


async def on_shutdown(dp):
    logger.warning('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close() if dp.storage is not None else None
    await dp.storage.wait_closed() if dp.storage is not None else None
    await db.pool.close() if db.pool is not None else None
    await cache.close()

    logger.warning('Bye!')
    if config.debug:
        await cache.flushdb()


if __name__ == '__main__':
    if config.mode == 'dev':
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    else:
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
