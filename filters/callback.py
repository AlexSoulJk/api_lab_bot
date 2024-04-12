from dataclasses import dataclass
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class SkipCallback(CallbackData, prefix='skip'):
    skip: bool = False


class ConfirmCallback(CallbackData, prefix='confirm'):
    confirm: bool = False


class RemindTypeCallBack(CallbackData, prefix='remind_type'):
    type: str = "common"


class ButLeftRightCallBack(CallbackData, prefix='left_right_but'):
    action: str
    new_chunk: int


class RemindListCallBack(CallbackData, prefix='remind_list'):
    remind_id: int


class ShowFilesCallBack(CallbackData, prefix="show_files_btn"):
    action: str = "show"


class FilesListCallBack(CallbackData, prefix="files"):
    file_id: int


class BackButtonCallBack(CallbackData, prefix="back"):
    action: str = "back"


class EditRemindCallBack(CallbackData, prefix="edit"):
    action: str = "edit"


class EditOptionCallBack(CallbackData, prefix="edit_option"):
    action: str


class EditFilesCallBack(CallbackData, prefix="edit_files"):
    action: str


class CloseCallBack(CallbackData, prefix="close"):
    action: str


class CheckSampleRemind(CallbackData, prefix="check"):
    action: str


class EditOptionObject(CallbackData, prefix="edit_option_obj"):
    is_touched: bool = False
    id: int = -1


class ClockCallback(CallbackData, prefix='inline_timepicker'):
    action: Optional[str] = None
    typo: Optional[str] = None
    data: Optional[int] = None


class RemindPeriodicType(CallbackData, prefix="type_period"):
    is_at_time: bool = False
