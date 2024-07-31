import os
import dataclasses
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


@dataclasses.dataclass
class Config:
    admins: list[str] = dataclasses.field(default_factory=lambda: ['835282186'])
    # Path to the root of the project
    root: Path = Path(__file__).parent.parent

    system_text: str = ''
    system_text_short: str = ''
    free_system_text: str = ''

    # Telegram bot token
    bot_token: str = os.environ.get('BOT_TOKEN')



    postgres_url: str = os.environ.get('DATABASE_URL')

    redis_host: str = os.getenv('REDIS_HOST')

    redis_port: int = os.getenv('REDIS_PORT')
    redis_password: str = os.getenv('REDIS_PASSWORD')

    # Path to the directory with audio files
    audio_dir: Path = root / 'audio'


    questions_path: Path = root / 'questions.csv'

    max_questions: int = 5

    mode: str = 'prod'

    debug: bool = False

    essay_system_message: str = ""

    log_group_id: int = 1234

    free_sessions: int = 2

    payme_speaklish_url: str = 'https://api.speaklish.uz/payments/'

    speaklish_url: str = 'https://api.speaklish.uz/'

    api_username: str = os.getenv('API_USERNAME')

    api_password: str = os.getenv('API_PASSWORD')
