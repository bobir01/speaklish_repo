from celery import shared_task
from django.conf import settings

from .models import UserPart1Result, UserPart2Result, UserPart3Result, TestSession
from .utils.ai_tools import get_transcript, get_completion, logger
from pydub import AudioSegment
from .utils.prompt_processor import PromptProcessor
import time


@shared_task()
def process_part1_result_task(result_id: int):
    result = UserPart1Result.objects.get(id=result_id)

    audio = AudioSegment.from_file(result.voice_audio)
    result.answer = get_transcript(result.voice_audio)
    result.tts_name = 'whisper-1'
    result.voice_length = audio.duration_seconds
    result.save()


@shared_task()
def process_part2_result_task(result_id: int):
    result = UserPart2Result.objects.get(id=result_id)

    audio = AudioSegment.from_file(result.voice_audio)
    result.answer = get_transcript(result.voice_audio)
    result.tts_name = 'whisper-1'
    result.voice_length = audio.duration_seconds
    result.save()


@shared_task()
def process_part3_result_task(result_id: int):
    result = UserPart3Result.objects.get(id=result_id)

    audio = AudioSegment.from_file(result.voice_audio)
    result.answer = get_transcript(result.voice_audio)
    result.tts_name = 'whisper-1'
    result.voice_length = audio.duration_seconds
    result.save()


@shared_task()
def process_feedback_task(session_id: int):
    session = TestSession.objects.get(id=session_id)
    part1_results = UserPart1Result.objects.filter(session_id=session).all()
    part2_result = UserPart2Result.objects.filter(session_id=session).first()
    part3_results = UserPart3Result.objects.filter(session_id=session).all()
    if part3_results.filter(answer__isnull=True).exists():
        logger.info('Waiting for part3 results')
        while part3_results.filter(answer__isnull=True).exists():
            time.sleep(3)
            part3_results = UserPart3Result.objects.filter(session_id=session).all()
    prompt_processor = PromptProcessor()
    prompt_processor.add_part_header(1)
    for result in part1_results:
        prompt_processor.set_messages(
            examiner_msg=result.question.question_txt, candidate_msg=result.answer)
    prompt_processor.add_part_header(2)
    prompt_processor.set_messages(
        examiner_msg=part2_result.question.question_txt, candidate_msg=part2_result.answer)
    prompt_processor.add_part_header(3)
    for result in part3_results:
        prompt_processor.set_messages(
            examiner_msg=result.question.question_txt, candidate_msg=result.answer)
    start = time.time()
    if settings.IN_TEST:
        completion_txt, tokens_used = 'Candidate is good and performed well', 1000
        logger.info(prompt_processor.prepared)
    else:
        completion_txt, tokens_used = get_completion(prompt_processor.prepared)
    end = time.time()
    session.result = completion_txt
    session.used_tokens = tokens_used
    session.model_name = settings.OPENAI_MODEL
    session.wait_time = (end - start)
    session.finish_state = 'part_3'
    session.stop_reason = 'success'

    logger.info(f"Completion time: {(end - start):.2f} seconds")
    session.save()
