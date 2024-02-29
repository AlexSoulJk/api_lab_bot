from dataclasses import dataclass
from aiogram.filters.callback_data import CallbackData

class SkipCallback(CallbackData, prefix='skip'):
    skip: bool = False

class ConfirmCallback(CallbackData, prefix='confirm'):
    confirm: bool = False

class RemindTypeCallBack(CallbackData, prefix='remind_type'):
    type: str = "common"