from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def payment_button(payment_url: str) -> InlineKeyboardMarkup:
    """
    Generate payment button for each order.
    """

    return InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Payme 🚀', url=payment_url),
                InlineKeyboardButton(text='Back', callback_data='back')
            ]
        ]
    )
