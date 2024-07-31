import io
import asyncio
from typing import List, Dict, Any

from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from keyboards.sections_keyboard import move_part2_keyboard
from keyboards.pre_test_btn import get_pre_test_btn
from loader import dp, logger, cache, config, speaklish_api, bot

from utils import textMessages
from utils.transcript_helper import check_voice_message, format_voice_url


@dp.message_handler(commands=['test'])
async def test_start(message: Message, state: FSMContext):
    """This handler is responsible for pre-test intro for candidate
     and give the one to choose to take a test or not """
    current_state = await state.get_state()
    # await message.answer("We are under maintenance, please, try again later")
    # return

    if current_state is None or current_state == '':
        await message.answer(textMessages.PRE_TEST, reply_markup=get_pre_test_btn())
    else:
        await message.answer("You are already in the test!!!")
        return


@dp.callback_query_handler(lambda call: call.data.startswith('pre_test'))
async def pre_test(call: CallbackQuery, state: FSMContext):
    test_decision = call.data
    if test_decision == 'pre_test-start_now':
        await start_part1(call.message, state)
        try:
            await call.message.delete()
        except Exception as e:
            logger.error(f"Error while deleting message in pre-part1 handled: {e}")
    elif test_decision == 'pre_test-later':
        await call.message.edit_text(textMessages.PRE_TEST_LATER)
    else:
        await call.message.edit_text('Something went wrong, please start again')
        logger.error(f"Error in pre_test callback: {call.data}")
        await state.finish()


async def start_part1(message: Message, state: FSMContext):
    current_state = await state.get_state()
    user_id = message.chat.id

    if current_state is None or current_state == '':
        await state.set_state('part1')
    else:
        await message.answer("You are already in the test!!!")
        return
    free_trial = await cache.get(f'free_trial:{user_id}')

    if free_trial is None:
        await cache.set(f'free_trial:{user_id}', config.free_sessions)
        free_trial = config.free_sessions
    free_trial = int(free_trial)
    if free_trial <= 0:
        paid_sessions = await cache.get(f'premium:{user_id}')
        if paid_sessions is None:
            await message.answer(textMessages.FREE_TRIAL_END)

            await state.finish()
            return
        else:
            if int(paid_sessions) <= 0:
                await message.answer(textMessages.FREE_TRIAL_END)
                await state.finish()
                return
            await cache.decrby(f'premium:{user_id}', 1)
    else:
        await cache.decrby(f'free_trial:{user_id}', 1)

    await message.answer(textMessages.PART1_START)
    await asyncio.sleep(2)
    user_referral = await cache.keys(match=f'referral:*:{user_id}')
    referral = None
    if len(user_referral) == 1:
        referral = user_referral[0].split(":")[1]
        logger.info(f"Referral found for user {user_id}: {referral}")

    test_session: Dict[str, Any] = await speaklish_api.create_session(user_id=user_id, referral_code=referral)

    part1_questions: List[Dict] = test_session.get('part1_questions')
    part2_question: Dict[str, str] = test_session.get('part2_question')
    part3_questions: List[Dict] = test_session.get('part3_questions')

    await state.update_data(part1_questions=part1_questions,
                            part1_questions_index=0,
                            ### add other parts here
                            part2_question=part2_question,
                            part3_questions=part3_questions,
                            session_id=test_session.get('session_id')
                            )
    first_qs_txt = part1_questions[0]['question_txt']
    qs_audio: str = await format_voice_url(voice_url=part1_questions[0]['voice_url'])

    question = f"Let's start the conversation with:\n{first_qs_txt}"
    await message.answer_audio(qs_audio, caption=question, disable_notification=True)
    await message.answer("Please, record your answer via Telegram microphone button and send it here.",
                         disable_notification=True)

    await cache.delete(f'part1_{user_id}', f'part3_{user_id}', f'part2_{user_id}', "audio:part2_{user_id}")


@dp.message_handler(content_types=ContentType.VOICE, state='part1')
async def process_voice_part1(message: Message, state: FSMContext):
    data = await state.get_data()
    valid_voice = await check_voice_message(message)
    if valid_voice is False:
        return

    part1_questions: List[Dict] = data.get('part1_questions')
    current_question = part1_questions[data.get('part1_questions_index')]
    session_id = data.get('session_id')
    buffer = io.BytesIO()
    await message.voice.download(destination_file=buffer, seek=True)
    part1_questions_index = data.get('part1_questions_index')
    if part1_questions is None or part1_questions_index is None:
        await message.answer("Some error occurred. Please, start the /test again")
        logger.error(f'part1_questions or part1_questions_index is None cannot process voice')
        await bot.send_message(config.admin_id, f"part1_questions or part1_questions_index is None cannot process voice")
        await state.finish()
    row = len(part1_questions)
    if part1_questions_index >= row - 1:
        await state.update_data(part1_questions_index=part1_questions_index + 1)  # to prevent multiple answers
        await message.answer(textMessages.PART1_END,
                             reply_markup=move_part2_keyboard(message.from_user.id))

        try:
            result = await speaklish_api.part1_create(session_id=session_id,
                                                      question_id=current_question['id'],
                                                      voice=buffer.getvalue())

            logger.info(
                f"Part 1 created for session {session_id}, question {current_question['id']}")

            if result.get('ok') is not True:
                raise Exception(result.get('msg'))
            return
        except Exception as e:
            logger.error(f"Error while sending voice to API: {e}")
            await message.answer("Some error occurred. Please, try again")
            await state.finish()
            return

    next_question = part1_questions[part1_questions_index + 1]

    question_txt = next_question['question_txt']
    question = f'Question:\n{question_txt}'
    question_audio = await format_voice_url(next_question['voice_url'])

    await state.update_data(part1_questions_index=part1_questions_index + 1)
    await message.answer_audio(audio=question_audio,
                               caption=question,
                               disable_notification=True)

    try:
        result = await speaklish_api.part1_create(session_id=session_id,
                                                  question_id=current_question['id'],
                                                  voice=buffer.getvalue())
        if result.get('ok') is not True:
            raise Exception(result.get('msg'))
        logger.info(f"Part 1 created for session {session_id}, question {part1_questions[part1_questions_index]['id']}")
    except Exception as e:
        logger.error(f"Error while sending voice to API: {e}")
        await message.answer("Some error occurred. Please, try again")
        await state.finish()
        return


@dp.callback_query_handler(text_contains='move_part2', state='part1')
@dp.async_task
async def move_part2(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(textMessages.PART2_INTRO)
    await state.set_state('part2')

    data = await state.get_data()

    part2_question = data.get('part2_question')
    question_txt = part2_question['question_txt']
    question_audio = await format_voice_url(part2_question['voice_url'])

    final_question = textMessages.PART2_PREPARE.format(question=question_txt)
    await call.message.answer_audio(audio=question_audio, caption=final_question)
    clock_emoji = await call.message.answer('⏳', disable_notification=True)
    await state.update_data(part2_id=part2_question['id'])
    await asyncio.sleep(60)
    sent_audio = await cache.exists(f'audio:part2_{call.from_user.id}')
    if sent_audio == 0:
        await cache.delete(f'audio:part2_{call.from_user.id}')
        return await clock_emoji.edit_text('Time is up! Please, start recording your answer')

    await cache.delete(f'audio:part2_{call.from_user.id}')
