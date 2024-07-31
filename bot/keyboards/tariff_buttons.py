from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from enum import Enum


class TariffButtons(Enum):
    TRIAL = InlineKeyboardButton(text="Trial Package", callback_data="tariff:trial")
    SILVER = InlineKeyboardButton(text="Silver package", callback_data="tariff:silver")

    GOLD = InlineKeyboardButton(text="Gold package", callback_data="tariff:gold")

    @staticmethod
    def get_tariff_buttons(full: bool = True, tariff: 'TariffButtons' = None):
        keyboard = InlineKeyboardMarkup(row_width=1)
        if full:
            keyboard.add(TariffButtons.TRIAL.value, TariffButtons.SILVER.value,
                         TariffButtons.GOLD.value
                         )
        else:
            if tariff == TariffButtons.TRIAL:
                keyboard.add(TariffButtons.TRIAL.value)
            elif tariff == TariffButtons.SILVER:
                keyboard.add(TariffButtons.SILVER.value)
            elif tariff == TariffButtons.GOLD:
                keyboard.add(TariffButtons.GOLD.value)

        return keyboard
