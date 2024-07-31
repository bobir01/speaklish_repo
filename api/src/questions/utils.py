import asyncio
from edge_tts import Communicate
from pydub import AudioSegment
from django.conf import settings
from typing import List, Literal


def generate_audio(id_, question_txt, part_number, lang: Literal['en','ru'] = 'en',
                   gender: Literal['female', 'male'] = 'female'):
    """
    this function generates audio file from text using edge_tts library

    :param id_: question id
    :param question_txt: question text
    :param part_number: part number
    :param lang: language
    :param gender: gender
    :return: audio file path
Name: ru-RU-DmitryNeural
Gender: Male

Name: ru-RU-SvetlanaNeural
Gender: Female
"""
    if lang == 'en':
        if gender == 'female':
            communicate = Communicate(question_txt, voice='en-US-AriaNeural')
        else:
            communicate = Communicate(question_txt, voice='en-US-AndrewMultilingualNeural')
    else:
        if gender == 'female':
            communicate = Communicate(question_txt, voice='ru-RU-SvetlanaNeural')
        else:
            communicate = Communicate(question_txt, voice='ru-RU-DmitryNeural')



    audio_file_path = settings.MEDIA_ROOT / 'voices' / f"part{part_number}" / f"question_{id_}.ogg"

    asyncio.run(save_audio(communicate, audio_file_path))

    return f"{settings.MEDIA_URL}voices/part{part_number}/question_{id_}.ogg"


async def save_audio(communicate: Communicate, audio_file_path):
    await communicate.save(audio_file_path)
    mp3_audio = AudioSegment.from_file(audio_file_path, format="mp3")
    mp3_audio.export(audio_file_path, format="ogg", bitrate="64k", codec="libopus")
