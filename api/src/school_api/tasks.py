import os

from celery import shared_task
from django.conf import settings
from django.db import models
from django.utils import timezone
from celery.utils.log import get_task_logger
from school_api.utils.telegrambot import send_message

from school_api.models import SchoolPart1Result, SchoolPart2Result, SchoolPart3Result, TestSessionSchool, \
    PronunciationResult
from api.utils.ai_tools import get_transcript, get_completion
from school_api.utils import groq_parser
from school_api.utils.pronunciation_service import pronunciation_assessment
from school_api.utils.audio_conversion import Converter
from pydub import AudioSegment
from api.utils.prompt_processor import PromptProcessor
import time

from school_api.serializers import ParsedSessionSerializer

logger = get_task_logger(__name__)


@shared_task()
def process_part1_result_task(result_id_pk: int):
    result = SchoolPart1Result.objects.get(id=result_id_pk)
    audio = AudioSegment.from_file(result.voice_audio)
    result.answer = get_transcript(result.voice_audio)
    result.voice_length = audio.duration_seconds
    result.finished_at = timezone.now()
    result.status = 'completed'
    result.session.finish_state = 'part1'

    logger.info(f'Part1 result {result.id} is {result.answer}')
    result.save(force_update=True)


@shared_task()
def process_part2_result_task(result_id_pk: int):
    result = SchoolPart2Result.objects.get(id=result_id_pk)
    logger.info(f'Processing part2 result {result.id}')
    audio = AudioSegment.from_file(result.voice_audio)
    result.answer = get_transcript(result.voice_audio)
    result.voice_length = audio.duration_seconds
    result.finished_at = timezone.now()
    result.status = 'completed'
    result.session.finish_state = 'part2'

    logger.info(f'Part2 result {result.id} is {result.answer}')
    result.save(force_update=True)

    process_pronunciation.delay(session_id_pk=result.session_id)


@shared_task()
def process_part3_result_task(result_id_pk: int):
    result = SchoolPart3Result.objects.get(id=result_id_pk)
    logger.info(f'Processing part3 result {result.id}')

    audio = AudioSegment.from_file(result.voice_audio)
    result.answer = get_transcript(result.voice_audio)
    result.voice_length = audio.duration_seconds
    result.finished_at = timezone.now()
    result.status = 'completed'
    result.session.finish_state = 'part3'

    logger.info(f'Part3 result {result.id} is {result.answer}')
    result.save(force_update=True)

    is_last = SchoolPart3Result.objects.filter(session_id=result.session_id).aggregate(
        qs=models.Max('question_id'))['qs']
    if result.question_id == is_last:
        logger.info(f'All part3 results are completed for session {result.session_id}')

        process_feedback_task.delay(session_id_pk=result.session_id)


@shared_task()
def process_feedback_task(session_id_pk: int, is_test=False):
    session = TestSessionSchool.objects.get(id=session_id_pk)
    part1_results = SchoolPart1Result.objects.filter(session_id=session).select_related('question').all()
    part2_result = SchoolPart2Result.objects.filter(session_id=session).select_related('question').first()
    part3_results = SchoolPart3Result.objects.filter(session_id=session).select_related('question').all()

    # pronunciation added
    pronunciation_wait_threshold = 30

    pronunciation_result = PronunciationResult.objects.filter(session_id=session)
    if not pronunciation_result.exists():
        logger.info(f'Pronunciation result not found for session {session_id_pk}')
        wait_time_s = time.time()
        while pronunciation_result.count() <= 1 and (time.time() - wait_time_s) < pronunciation_wait_threshold:
            time.sleep(5)
            pronunciation_result = PronunciationResult.objects.filter(session_id=session)
            logger.info(f'Waiting for pronunciation result for session {session_id_pk}')

        pronunciation_result = pronunciation_result.first()

    else:
        pronunciation_result: PronunciationResult = pronunciation_result.first()

    prompt_processor = PromptProcessor()
    prompt_processor.add_part_header(1)
    for result in part1_results:
        prompt_processor.set_messages(
            examiner_msg=result.question.question_txt, candidate_msg=result.answer)
    prompt_processor.add_part_header(2)
    prompt_processor.set_messages(
        examiner_msg=part2_result.question.question_txt, candidate_msg=part2_result.answer)
    pronunciation_json = pronunciation_result.score_details

    prompt_processor.add_part_header(3)
    for result in part3_results:
        prompt_processor.set_messages(
            examiner_msg=result.question.question_txt, candidate_msg=result.answer)
    wait_time_s = time.time()
    prompt_processor.add_pronunciation_assessment(pronunciation_json['pronunciation'],
                                                  pronunciation_json['mispronounced_words'])

    completion, tokens = get_completion(prompt_processor.prepared)
    logger.info(prompt_processor.prepared)
    session.wait_time = time.time() - wait_time_s
    session.result = completion
    session.used_tokens = tokens
    if is_test:
        session.is_test = True
    session.finished_at = timezone.now()
    session.finish_state = 'part3'
    session.model_name = settings.OPENAI_MODEL
    session.save()
    logger.info(f'Feedback for session {session.id}  in {session.wait_time:.2f} seconds')
    feedback_txt = completion + '\n' + '@SpeaklishBot' + '\n' + f'Session ID: {session.id}'
    if not is_test:
        send_message(feedback_txt, session.student_id)

    parse_model_answer.delay(session_id_pk=session.id)
    return completion


@shared_task()
def parse_model_answer(session_id_pk: int):
    s_time = time.time()
    logger.info(f'Parsing session {session_id_pk}')
    session = TestSessionSchool.objects.get(id=session_id_pk)
    if session.finish_state != 'part3':
        logger.error(f'Session {session_id_pk} is not finished')
        return
    parsed_session = groq_parser.parser_model_answer(session.result)

    parsed_session['session'] = session.id
    logger.info(f'Parsed session {session_id_pk} in {time.time() - s_time:.2f} seconds')
    try:
        serializer = ParsedSessionSerializer(data=parsed_session)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            logger.error(serializer.errors)
    except Exception as e:
        logger.error(e)


@shared_task()
def process_pronunciation(session_id_pk: int):
    session = TestSessionSchool.objects.get(id=session_id_pk)
    part2_result = SchoolPart2Result.objects.filter(session_id=session)
    if not part2_result.exists():
        logger.error(f'Part2 result for session {session_id_pk} not found')
        return
    part2_session: SchoolPart2Result = part2_result.first()
    wav_file = Converter.to_wav(part2_session.voice_audio.path)

    topic = part2_session.question.question_txt.split('\n')[0]
    logger.info(f'Pronunciation: session: {session_id_pk} | topic: {topic}')
    s_time = time.time()
    pronunciation_result = pronunciation_assessment(wav_file, topic=topic)
    logger.debug(pronunciation_result)
    e_time = time.time() - s_time

    pronunciation = PronunciationResult(
        session=session,
        score=pronunciation_result['pronunciation']['pronunciation_score'],
        score_details=pronunciation_result,
        time_taken=e_time
    )
    os.remove(wav_file)
    pronunciation.save()
