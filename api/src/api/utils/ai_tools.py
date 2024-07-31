from typing import List, Tuple

import openai
from openai import Client, InternalServerError
from django.conf import settings
from api.utils.logger import logged

from celery.utils.log import get_task_logger
from django.core.files import File

logger = get_task_logger(__name__)

openai_client = Client(api_key=settings.OPENAI_API_KEY)


def get_transcript(voice: File, n_tries: int = 0) -> str:
    """Transcribe audio file to text
    :param voice: audio file in named bytes io format
    :param n_tries: number of tries to get transcript   **optional**
    :return: txt of  audio file as string

    :exception: InvalidRequestError, APIError, OpenAIError, Exception"""

    try:
        response = openai_client.audio.transcriptions.create(model='whisper-1',
                                                             file=voice.file.file,
                                                             language='en')

        return response.text
    except Exception as e:
        logged({
            'error': e,
            'n_tries': n_tries
        })
        return 'Could not transcribe your audio, service unavailable, please retry later'


def get_completion(messages: List[dict], ) -> Tuple[str, int]:
    try:

        response = openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.OPENAI_TEMP,
            timeout=60,
            max_tokens=3600,
        )
        return response.choices[0].message.content, response.usage.total_tokens

    except InternalServerError as e:
        logger.error({
            'error': e,
            'type': 'Internal Server Error',
            'messages': messages,
        })

    except Exception as e:
        logger.error({
            'error': str(e),
            'type': 'Unknown Error',
            'messages': messages,
        })

        return 'Service unavailable, Please retry later, contact @Realm_AI to restore your sessions', 0


def check_writing_task1(essay: str, graph_url: str, configModel: object):
   pass