import asyncio
import time

from groq import AsyncGroq, Groq
from groq import BadRequestError, RateLimitError, APITimeoutError
from rest_framework.parsers import JSONParser
from django.conf import settings
from io import BytesIO
from celery.utils.log import get_task_logger

client = Groq(api_key=settings.GROQ_API_KEY)

logger = get_task_logger(__name__)


def score_floor(score: float) -> float:
    """IELTS like scoring system"""
    float_reminder = score % 1
    result = None
    if float_reminder < 0.25:
        result = int(score)
    elif 0.25 <= float_reminder < 0.75:
        result = int(score) + 0.5
    else:
        result = int(score) + 1
    return float(result)


def parser_model_answer(content: str, n=1) -> dict:
    """


    """
    base_response = {
        'feedback': '',
        'score': {
            'band': 0,
            'vocabulary': 0,
            'grammar': 0,
            'fluency': 0,
            'pronunciation': 0
        },
        'suggested_vocab': [],
        'used_topic_words': [],
        'token_usage': 0,
        'wait_time': 0,
        'raw_json': content,
        'parsed_json': {},
    }
    try:
        completion =  client.chat.completions.create(
            model=settings.GROQ_PARSER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": settings.GROQ_PARSER_SYSTEM_TEXT
                },
                {
                    "role": "user",
                    "content": content
                },

            ],
            temperature=0,
            max_tokens=10_000,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )

        buf = BytesIO()
        buf.write(completion.choices[0].message.content.encode())
        tokens_used = completion.usage.total_tokens
        wait_time = completion.usage.total_time
        buf.seek(0)
        data = JSONParser().parse(buf)
        data['token_usage'] = tokens_used
        data['raw_json'] = content
        data['wait_time'] = wait_time
        data['parsed_json'] = completion.choices[0].message.content
        if not data.get('ok', False):
            return base_response
        score = data['score']
        if score.get('band') is None:
            logger.info('Calculating band')
            if score.get('pronunciation') is None:
                score['pronunciation'] = 0
            data['score']['band'] = score_floor(round(sum(
                [data['score'][k] for k in data['score'].keys() if k != 'band']) / 4, 1))
    except BadRequestError as e:
        logger.error(f'Error in parsing: {e} returning empty json!')
        return base_response

    except (RateLimitError, APITimeoutError) as e:
        logger.error(f'Error in parsing: {e} retrying {n} time(s)')
        time.sleep(3)
        if n > 3:
            return base_response
        return parser_model_answer(content, n + 2)

    except Exception as e:
        logger.error(f'Error in parsing: {e} retrying {n} time(s)')
        time.sleep(3)
        if n > 3:
            return base_response
        return parser_model_answer(content, n + 1)
    return data
