import logging
from openai import AsyncClient
from httpx import Timeout
from utils.logging import setup_logger
from config import Config
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from redis.asyncio import Redis
from postgres.db_client import Database
from services.api_manager import SpeaklishAPI

config = Config(
    mode='',

    voice_name='en-US-JennyNeural',
    open_ai_temp=0.2,

)

if not config.audio_dir.exists():
    config.audio_dir.mkdir(exist_ok=True)

if config.mode == 'dev':
    config.redis_host = 'localhost'
    config.redis_port = 6379
    config.redis_password = ''

# bot = Bot(token=config.bot_token, parse_mode='HTML')
# dp = Dispatcher(bot, storage=MemoryStorage())
cache = Redis(host=config.redis_host,
              port=config.redis_port,
              password=config.redis_password,
              ssl=True,
              decode_responses=True)

# speaklish_api = SpeaklishAPI()

logger = setup_logger(__name__, level=logging.DEBUG if config.debug else logging.DEBUG)

db = Database(config.postgres_url)



