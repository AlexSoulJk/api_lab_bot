from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, ChangeRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from attachements import tools as t
from filters.callback import ConfirmCallback, ButLeftRightCallBack, RemindListCallBack, ShowFilesCallBack, \
    BackButtonCallBack, FilesListCallBack, CloseCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc
import datetime

router = Router()


@router.message(Command(commands="check_daily"))
async def check_ended_start(message: Message, state: FSMContext):
    user = db.sql_query(query=select(User.name, User.id).where(
        User.user_id == str(message.from_user.id)), is_single=False)

    user_id_ = user[0][1]

    remind_list = db.sql_query(query=select(Remind).where(
        Remind.user_id == user_id_).where(
        Remind.date_deadline - datetime.datetime.now() < datetime.timedelta(days=1)).where(
        Remind.date_finish == null()), is_single=False)

    remind_list_btn = kb.get_remind_list_of_btn(remind_list)

    await state.update_data(user_name=user[0][0])
    await state.update_data(cur_chunk=1)
    await state.update_data(reminds=remind_list_btn)
    await state.update_data(list_info="reminds")
    await message.answer(text=user[0][0] + ", " + msg.CHECK_DAILY_START,
                         reply_markup=kb.get_smart_list(remind_list_btn, btn.CLOSE_REMIND_LIST))
    await state.set_state(CheckRemind.start)
