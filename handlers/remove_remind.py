import datetime

from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, RemoveRemind
from aiogram import Router, Bot, F
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, CloseCallBack
from aiogram.types import CallbackQuery
from database.db import db
from database.models import File, Remind, Category
from sqlalchemy import update


router = Router()

@router.callback_query(CheckRemind.check_remind,
                       CloseCallBack.filter(F.action == "remove_remind"))
async def accept_remove(query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(id_to_delete_msg=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.REMOVE_SHOORING_MSG,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.set_state(RemoveRemind.confirming)


@router.callback_query(RemoveRemind.confirming,
                       ConfirmCallback.filter(F.confirm == True))
async def accept_remove(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=(await state.get_data()).get("id_to_delete_msg"))
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    remind_id = (await state.get_data()).get("remind_id")
    db.sql_query(query=update(Remind).where(Remind.id == remind_id).values(date_is_delete=datetime.date.today()), is_update=True)
    await bot.send_message(chat_id=query.from_user.id, text=msg.REMOVE_CONFIRMED)
    await state.clear()


@router.callback_query(RemoveRemind.confirming,
                       ConfirmCallback.filter(F.confirm == False))
async def remove_canceled(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await state.set_state(CheckRemind.check_remind)


# DELETE SCENARIO FOR CLEANER OF DATA BASE
#     db.sql_query(query=delete(File).where(File.remind_id == remind_id), is_update=True)
#     db.sql_query(query=delete(Category).where(Category.remind_id == remind_id), is_update=True)
#     db.sql_query(query=delete(Remind).where(Remind.id == remind_id), is_update=True)