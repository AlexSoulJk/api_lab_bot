from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, CloseUrgently
from aiogram import Router, Bot, F
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, CloseCallBack
from aiogram.types import CallbackQuery
from database.db import db
from database.models import Remind
from sqlalchemy import update
import datetime

router = Router()


@router.callback_query(CheckRemind.check_remind,
                       CloseCallBack.filter(F.action == "close_urgently"))
async def start_urgently_close(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(chat_id=query.from_user.id, text=msg.CLOSE_SHOORING_MSG,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.set_state(CloseUrgently.confirming)


@router.callback_query(CloseUrgently.confirming,
                       ConfirmCallback.filter(F.confirm == True))
async def accept_remove(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    remind_id = (await state.get_data()).get("remind_id")
    db.sql_query(query=update(Remind).where(Remind.id == remind_id).values(date_finish=datetime.date.today()),
                 is_update=True)
    await bot.send_message(chat_id=query.from_user.id, text=msg.CLOSE_CONFIRMED)
    await state.clear()


@router.callback_query(CloseUrgently.confirming,
                       ConfirmCallback.filter(F.confirm == False))
async def remove_canceled(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await state.set_state(CheckRemind.check_remind)
