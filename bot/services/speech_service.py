from pathlib import Path
from loader import config
import asyncio

import itertools
from schemas import RecognitionResult


def collect_misspelled_words(pronunciation_result) -> list:
    return [word for word in pronunciation_result.words if word.error_type is None]


class SpeechAI:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(subscription=config.speech_key, region=config.service_region)
        self.speech_config.set_property(speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, '5000')

        audio_filename = config.audio_dir / '835282186_audio.wav'
        audio_input = speechsdk.AudioConfig(filename=str(audio_filename))
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config,
                                                            audio_config=audio_input)

    async def speech_to_text(self, filename: Path) -> str:
        pass

    async def pronunciation_assessment_long(self, audio_path: Path,
                                            text: str = None, ) -> RecognitionResult:
        pass

    async def pronunciation_assessment(self, audio_path: Path,
                                       text: str = None):
        pass


