import os

from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from typing import List, Union
import io


class Converter:
    @staticmethod
    def to_wav(audio_raw: Union[str, os.PathLike]) -> str:
        """Converts audio to wav format in memory now use it in asyncio task with `to_thread`
        :param audio_raw: bytes : audio file in ogg format
        :return: file path audio file in wav format"""

        audio = AudioSegment.from_file(file=audio_raw, format="ogg")
        out_file = NamedTemporaryFile(delete=False, suffix=".wav")
        wav = audio.export(out_f=out_file.name, format="wav", codec='pcm_s16le')
        return out_file.name

    @staticmethod
    def to_mp3(audio_raw: io.BytesIO) -> str:
        """Converts audio(.ogg) to mp3 format in memory now use it in asyncio task with `to_thread`"""
        audio = AudioSegment.from_file(audio_raw, format="ogg")
        out_file = NamedTemporaryFile(delete=False, suffix=".mp3")
        to_mp3 = audio.export(out_f=out_file.name, format="mp3", bitrate="64k", codec="libmp3lame")
        return out_file.name
