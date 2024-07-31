import logging
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from loader import dp
from utils import textMessages
from utils.with_http import WithHttp
from keyboards.payment_button import payment_button
from keyboards.tariff_buttons import TariffButtons


@dp.callback_query_handler(lambda call: call.data.startswith('tariff:'), state='*')
async def tariff_handler(call: CallbackQuery, state: FSMContext):
    await call.answer('Please, wait a moment...', cache_time=0)
    tariff = call.data.split(':')[1]
    price = 0
    quantity = 0
    if tariff == 'trial':
        price = 10_000
        quantity = 1
    elif tariff == 'silver':
        price = 10_000
        quantity = 6
    elif tariff == 'gold':
        price = 9_900
        quantity = 10
    try:
        payment_url = await WithHttp.get_order_link(call.from_user.id, quantity, price)
    except ValueError as e:
        await call.message.delete()
        await call.message.answer(f'This service is not available now. Please, try again later. \n')
        logging.error(e)
        return
    await call.message.edit_text(text=textMessages.TARIFF_DESCRIPTIONS[tariff],
                                 reply_markup=payment_button(payment_url))


@dp.callback_query_handler(text='back', state='*')
async def back_handler(call: CallbackQuery, state: FSMContext):
    try:

        await call.message.edit_text(text=textMessages.BUY_SESSIONS, reply_markup=TariffButtons.get_tariff_buttons())
        await state.finish()
    except Exception as e:
        logging.error({'exc': str(e),
                       'call': call, })
        return
