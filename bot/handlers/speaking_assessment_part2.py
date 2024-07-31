import asyncio
import io
import time
from typing import Dict, List
from utils import textMessages
from config.config import Config

from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.dispatcher import FSMContext
from loader import dp, logger, cache, speaklish_api, bot
from keyboards.sections_keyboard import move_part3_keyboard
from keyboards.feedback_button import feedback_btn

from utils.transcript_helper import check_voice_message, format_voice_url


@dp.message_handler(content_types=ContentType.VOICE, state='part2')
@dp.async_task
async def process_voice(message: Message, state: FSMContext):
    if (await check_voice_message(message)) is False:
        return

    await cache.set(name=f'audio:part2_{message.from_user.id}', value=1, ex=60 * 60)
    await message.answer(textMessages.PART2_END,
                         reply_markup=move_part3_keyboard(message.from_user.id))

    data = await state.get_data()

    buffer = io.BytesIO()
    await message.voice.download(destination_file=buffer, seek=True)
    result = await speaklish_api.part2_create(session_id=data.get('session_id'),
                                              question_id=data.get('part2_id'),
                                              voice=buffer.getvalue())
    try:
        if result.get('ok') is not True:
            raise Exception(result.get('msg'))
    except Exception as e:
        logger.error(f"Error while sending voice to API: {e}")
        await message.answer("Some error occurred. Please, try again")
        await state.finish()
        return


@dp.callback_query_handler(text_contains='move_part3', state='part2')
async def move_part3(call: CallbackQuery, state: FSMContext):
    """move to part 3"""

    await call.message.delete()
    await call.message.answer("Ok, let's move to part 3, I will ask some questions based on your part 2 answer!")
    await state.set_state('part3')
    data = await state.get_data()

    part3_questions = data.get('part3_questions')
    await state.update_data(part3_questions_index=0)
    part3_txt = part3_questions[0]["question_txt"]
    question_voice = await format_voice_url(part3_questions[0]["voice_url"])

    question = f'Question :\n{part3_txt}'
    await call.message.answer_audio(audio=question_voice, caption=question, disable_notification=True)



@dp.message_handler(content_types=ContentType.VOICE, state='part3')
@dp.async_task
async def process_voice_part3(message: Message, state: FSMContext):
    """remove extra overhead of waiting for completion of part 3 so now with API it is easy
    """

    if (await check_voice_message(message)) is False:
        return
    data = await state.get_data()
    part3_questions: List[Dict] = data.get('part3_questions')
    part3_questions_index = data.get('part3_questions_index')
    session_id = data.get('session_id')
    current_question = part3_questions[part3_questions_index]
    if part3_questions is None or part3_questions_index is None:
        await message.answer("Some error occurred. Please, start the test again")
        await state.finish()

        logger.error(f'part3_questions or part3_questions_index is None cannot process voice')
        return
    buffer = io.BytesIO()
    await message.voice.download(destination_file=buffer, seek=True)

    row = len(part3_questions)
    if part3_questions_index >= row - 1:
        await message.answer("You have finished the test. Thank you! \n"
                             "You will get feedback for your answers in few minutes")
        await message.answer('⏳', disable_notification=True)
        await state.finish()
        s_time = time.time()

        result = await speaklish_api.part3_create(session_id=session_id,
                                                  question_id=current_question['id'],
                                                  voice=buffer.getvalue())
        try:
            if result.get('ok') is not True:
                raise Exception(result.get('msg'))
        except Exception as e:
            logger.error(f"Error while sending voice to API: {e}")
            await message.answer("Some error occurred. Please, try again")
            await bot.send_message(
                chat_id=Config.admins[0],
                text=f"Error while sending voice to API in part3: {e}"
                     f"\n\nUser ID: {message.from_user.id}"
                     f"\n\nSession ID: {session_id}"
                     f"\n\nQuestion ID: {current_question['id']}"
            )
            await state.finish()
            return
        logger.info(f"part3_create took {time.time() - s_time} seconds")
        await asyncio.sleep(30)

        await message.answer(textMessages.FEEDBACK_REQUEST, reply_markup=feedback_btn)
        await state.finish()
        await cache.delete(f'part1_{message.from_user.id}', f'part2_{message.from_user.id}',
                           f'part3_{message.from_user.id}', f'config:session:{message.from_user.id}')

        log_msg = f'session: {session_id} | part3 user: {message.from_user.id} '
        logger.info(log_msg)
        return

    next_question = part3_questions[part3_questions_index+1]

    question_txt = next_question['question_txt']
    question_audio = await format_voice_url(next_question["voice_url"])

    question = f'Question :\n{question_txt}'
    await message.answer_audio(audio=question_audio, caption=question)

    await state.update_data(part3_questions_index=part3_questions_index + 1)

    result = await speaklish_api.part3_create(session_id=session_id,
                                              question_id=current_question['id'],
                                              voice=buffer.getvalue())
    try:
        if result.get('ok') is not True:
            raise Exception(result.get('msg'))
    except Exception as e:
        logger.error(f"Error while sending voice to API: {e}")
        await bot.send_message(
            chat_id=Config.admins[0],
            text=f"Error while sending voice to API in part3: {e}"
                 f"\n\nUser ID: {message.from_user.id}"
                 f"\n\nSession ID: {session_id}"
                 f"\n\nQuestion ID: {current_question['id']}"
        )
        await message.answer("Some error occurred. Please, try again")
        await state.finish()
        return
