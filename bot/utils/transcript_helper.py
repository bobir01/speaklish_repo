from services.openAI_service import openAI

from pydub import AudioSegment
import aiogram.types
import io
from loader import cache, config
import time


class NamedBytesIO(io.BytesIO):
    def __init__(self, content=b'', name='telegram_voice.ogg', ):
        super().__init__(content)
        self._name = name

    @property
    def name(self):
        return self._name




async def get_transcript_from_voice(voices: aiogram.types.Voice, is_part2=False):
    """get transcript from voice message
    :param voices: voice message
    :param is_part2: bool : is part 2
    """
    ogg = NamedBytesIO()


async def check_voice_message(message: aiogram.types.Message, is_part2=False) -> bool:
    """checks voice message for validity, mime_type and duration max 2.5 min and size max 20 mb
    :param message: voice message
    :param is_part2: bool : is part 2
    :return: True if valid, False if not valid
    """

    if message.voice.duration < 5:
        await message.reply("Please, send me a voice message more than 5 seconds to get satisfying results")
        return False
    if message.voice.mime_type != 'audio/ogg':
        await message.reply("Please, send me a voice message through Telegram")
        return False
    if message.voice.duration > 240:
        await message.reply("Please, send me a voice message less than 4 minutes")
        return False
    if message.voice.file_size > 20 * 1024 * 1024:
        await message.reply("Please, send me a voice message less than 20 mb")
        return False
    if is_part2:
        if message.voice.duration > 120:
            await message.reply("Warning: You have exceeded the time limit for Part 2, only 2 minutes are considered.")

    return True


async def format_voice_url(voice_url: str) -> str:
    """format voice url with speaklishAPI url
    :param voice_url: voice url
    :return: formatted voice url
    """
    if voice_url.startswith('https://'):
        return voice_url
    return config.speaklish_url + voice_url
