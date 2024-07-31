import asyncio
import io
from typing import List, Tuple

# import openai as ai
from openai import APIError, BadRequestError, InternalServerError

from loader import config, logger, openai_client


# ai.api_key = config.open_ai_key


class openAI:

    @staticmethod
    async def get_completion(messages: List[dict], ) -> Tuple[str, int]:
        try:

            response = await openai_client.chat.completions.create(
                model=config.open_ai_model,
                messages=messages,
                temperature=config.open_ai_temp,
                timeout=60
            )
            return response.choices[0].message.content, response.usage.total_tokens

        except InternalServerError as e:
            logger.error({
                'error': e,
                'type': 'Internal Server Error',
                'messages': messages,
            })

            return 'Service unavailable, Please retry later, contact @Realm_AI to restore your sessions', 0

    @staticmethod
    async def get_transcript(voice: io.BytesIO, n_tries: int = 0) -> str:
        """Transcribe audio file to text
        :param voice: audio file in ogg format
        :param n_tries: number of tries to get transcript   **optional**
        :return:  of audio file as string

        :exception: InvalidRequestError, APIError, OpenAIError, Exception"""

        try:
            response = await openai_client.audio.transcriptions.create(model='whisper-1',
                                                                       file=voice,
                                                                       language='en')

            return response.text
        except Exception as e:
            logger.error({
                'error': e,
                'n_tries': n_tries
            })
            return 'Could not transcribe your audio, service unavailable, please retry later'

