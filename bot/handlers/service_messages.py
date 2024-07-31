from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import Message, ReplyKeyboardRemove
from schemas import User, Session

from loader import dp, db, cache, bot, config, logger
from utils import textMessages
from keyboards import feedback_btn
from keyboards.pre_test_btn import get_phone_btn
from keyboards.tariff_buttons import TariffButtons
from aiogram.dispatcher.filters import Command


@dp.message_handler(Command('start'))
async def start(message: Message, state: FSMContext):
    await message.answer(textMessages.INTRO)
    referral = message.get_args()

    user = User(
        fullname=message.from_user.full_name,
        username=message.from_user.username,
        user_id=message.from_user.id,
        referral=referral
    )
    await db.insert_user(user)
    free_user = await cache.get(f'free_trial:{message.from_user.id}')
    if referral == '':
        if free_user is None:
            await cache.set(f'free_trial:{message.from_user.id}', config.free_sessions)
            await message.answer(textMessages.GET_PHONE, reply_markup=get_phone_btn())
            await state.update_data(referral=None)
            await state.set_state('phone_number_input')
            return

    ###### sh olimov
    if referral == 'sh-olimov':
        await message.answer(
            '<b>🎉 Congratulations! 🎉</b>\nYou have successfully joined the Speaklish family by Shoxruxbek Olimov. 🎉\n\nBut for further processing, please send your phone number. 📱',
            reply_markup=get_phone_btn())
        await state.set_state('phone_number_input')
        await state.update_data(referral=referral)
        return
    ###### sh olimov


@dp.message_handler(state='phone_number_input', content_types=types.ContentType.CONTACT)
async def phone_number_input(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if phone[0] != '+':
        phone = '+' + phone
    logger.info(f'Phone number: {phone} for user: {message.from_user.id}')
    await db.update_phone_number(message.from_user.id, phone)
    await message.answer("Thank you! 🎉\nYou have successfully joined the Speaklish family. 🎉")
    data = await state.get_data()
    referral = data.get('referral')
    if referral is not None:
        in_cache = await cache.get(f'referral:olimov:{message.from_user.id}')  # check if user is already in cache
        if in_cache is not None:
            await message.answer('Unfortunately, you have already used the referral link. 🤔',
                                 reply_markup=ReplyKeyboardRemove())
            logger.info(f'User {message.from_user.id} has already used the referral link')
            await state.finish()
            return

        await cache.set(f'referral:olimov:{message.from_user.id}', phone)  # track olimov referrals
        olimov_phones = await cache.get(f'referral:olimov:{phone}')  # track olimov referrals if user is not in db
        if olimov_phones is None:
            await message.answer(
                'But we could not find any user with this phone number in our list. 🤔, contact with @Realm_AI for more information.',
                reply_markup=ReplyKeyboardRemove())
            logger.info(f'User {message.from_user.id} has entered the phone number of another user')
            await state.finish()
            return
        # check if it is first time

        await message.answer('Now you can start the test using /test command. Good luck on your MOCK 🚀',
                             reply_markup=ReplyKeyboardRemove())
        logger.info(f'User {message.from_user.id} has successfully passed the referral link sh-olimov')
        await cache.set(f'premium:{message.from_user.id}', 1)
        await cache.incr(f'referral:olimov:count', 1)
        await state.finish()
    await state.finish()


@dp.message_handler(commands=['help'], state='*')
async def help_handler(message: Message):
    await message.answer(textMessages.HELP, reply_markup=feedback_btn)


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_session(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
        await message.answer(textMessages.CANCEL, reply_markup=feedback_btn)
        config_session_json = await cache.get(f'config:session:{message.from_user.id}')
        if config_session_json:
            config_session = Session.model_validate_json(config_session_json)

            config_session.bulk_update(
                finish_state=current_state[:10],
                stop_reason='user_cancel')

            await db.update_session(config_session)
            await cache.delete(f'config:session:{message.from_user.id}', f'part1_{message.from_user.id}',
                               f'part2_{message.from_user.id}', f'part3_{message.from_user.id}')
    else:
        await message.answer(textMessages.NO_ACTIVE_TEST)


@dp.message_handler(commands=['buy_sessions'], state='*')
async def buy_sessions(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await message.answer(textMessages.ACTIVE_TEST_GOING)
        return
    await message.answer(textMessages.BUY_SESSIONS, reply_markup=TariffButtons.get_tariff_buttons())


@dp.message_handler(commands=['profile'], state='*')
async def profile_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    msg = 'You have\n'
    if current_state:
        await message.answer(textMessages.ACTIVE_TEST_GOING)
        return
    premium_sessions = await cache.get(f'premium:{message.from_user.id}')
    free_sessions = await cache.get(f'free_trial:{message.from_user.id}')
    if premium_sessions is None:
        premium_sessions = 0
        if free_sessions is None:
            free_sessions = config.free_sessions
            await cache.set(f'free_trial:{message.from_user.id}', free_sessions)
            await message.answer('You have {0} free sessions left. \n'
                                 'You can buy more sessions using /buy_sessions command\n'
                                 'Check out the new offers in /buy_sessions 🙂'.format(free_sessions))
            return
        if int(free_sessions) <= 0:
            free_sessions = 0
            await cache.set(f'free_trial:{message.from_user.id}', free_sessions)

    msg += '✨ {free_sessions} sessions left. \n'
    if free_sessions is None:
        free_sessions = 0

    await message.answer(msg.format(free_sessions=int(free_sessions) + int(premium_sessions)) +
                         'You can buy more sessions using /buy_sessions command 🙂')


@dp.my_chat_member_handler(lambda chat_member: True)
async def on_chat_member(event: types.ChatMemberUpdated):
    msg = 'Status: {0}'
    msg += f'\nUser id: {event.from_user.id}'
    msg += f'\nFullname: {event.from_user.full_name}'
    msg += f'\nUsername: @{event.from_user.username}'
    msg += f'\nurl: <a href="tg://user?id={event.from_user.id}">link</a>'
    if event.new_chat_member.status == 'kicked':
        msg = msg.format('false 🚫')
        user = await db.get_user(event.from_user.id)
        if user is not None:
            msg += f'\nJoined at: {user.joined_at.strftime("%d.%m.%Y %H:%M")}'
            try:
                await bot.send_message(config.log_group_id,
                                       msg,
                                       parse_mode='HTML')
            except Exception as e:
                logger.error(f"Error while sending message to log group: {e}")
            await db.update_user_status(user.user_id)
            return
        else:
            try:
                await bot.send_message(config.log_group_id,
                                       msg,
                                       parse_mode='HTML')
            except Exception as e:
                logger.error(f"Error while sending message to log group: {e}")
            await db.insert_user(User(
                fullname=event.from_user.full_name,
                username=event.from_user.username,
                user_id=event.from_user.id,
                joined_at=datetime.now(),
                is_active=False
            ))
            return

    else:
        user = await db.get_user(event.from_user.id)
        msg = msg.format('true ✅')

        if user is not None:
            if user.is_active is False:
                await db.update_user_status(user.user_id)
                msg += f'\nJoined at: {user.joined_at.strftime("%d.%m.%Y %H:%M")}'
                try:
                    await bot.send_message(config.log_group_id,
                                           msg,
                                           parse_mode='HTML')
                except Exception as e:
                    logger.error(f"Error while sending message to log group: {e}")
                return
            else:
                return
        else:
            try:
                await bot.send_message(config.log_group_id,
                                       msg,
                                       parse_mode='HTML')
            except Exception as e:
                logger.error(f"Error while sending message to log group: {e}")

            await db.insert_user(User(
                fullname=event.from_user.full_name,
                username=event.from_user.username,
                user_id=event.from_user.id,
                joined_at=datetime.now(),
                is_active=True
            ))
            return
