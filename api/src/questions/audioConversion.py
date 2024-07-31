from pydub import AudioSegment
import io
import asyncio


class Converter:
    @staticmethod
    async def to_ogg(audio_io: io.BytesIO, input_type='mp3') -> io.BytesIO:
        """Converts audio to ogg format in memory now use it in asyncio task with `to_thread`"""
        audio_raw = AudioSegment.from_file(audio_io, format=input_type)
        to_ogg = await asyncio.to_thread(audio_raw.export, format="ogg", bitrate="64k", codec="libopus")
        buffer = io.BytesIO(to_ogg.read())
        to_ogg.close()
        return buffer

    @staticmethod
    async def to_wav(audio_raw: io.BytesIO) -> io.BytesIO:
        """Converts audio to wav format in memory now use it in asyncio task with `to_thread`
        :param audio_raw: bytes : audio file in ogg format
        :return: io.BytesIO audio file in wav format"""

        audio = AudioSegment.from_file(audio_raw, format="ogg")
        wav = await asyncio.to_thread(audio.export, format="wav")
        buffer = io.BytesIO(wav.read())
        wav.close()
        return buffer

    @staticmethod
    async def to_mp3(audio_raw: io.BytesIO) -> io.BytesIO:
        """Converts audio(.ogg) to mp3 format in memory now use it in asyncio task with `to_thread`"""
        audio = AudioSegment.from_file(audio_raw, format="ogg")
        to_mp3 = await asyncio.to_thread(audio.export, format="mp3", bitrate="64k", codec="libmp3lame")
        buffer = io.BytesIO(to_mp3.read())
        to_mp3.close()
        return buffer


