from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, ChangeRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, EditRemindCallBack, EditOptionCallBack, BackButtonCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from copy import deepcopy
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc
import datetime

router = Router()


@router.callback_query(CheckRemind.check_remind,
                       EditRemindCallBack.filter(F.action == "edit"))
async def start_changing(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                             inline_message_id=query.inline_message_id,
                                             reply_markup=kb.get_keyboard(btn.EDIT_REMIND_LIST + btn.BACK_TO_REMIND))
    await state.update_data(msg_remind_id=query.message.message_id)
    await state.set_state(ChangeRemind.start)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "name"))
async def change_name_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_NAME)
    await state.set_state(ChangeRemind.change_name)


@router.message(ChangeRemind.change_name, F.text)
async def try_change_name(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    remind, categories, files = info["remind_tmp"]
    new_remind = deepcopy(remind)
    new_remind.name = query.text
    await bot.delete_message(chat_id=query.from_user.id, message_id=info["msg_remind_id"])
    await bot.send_message(chat_id=query.from_user.id, text=msg.get_remind_text(new_remind, categories),
                                reply_markup=kb.get_keyboard(
                                    btn.SHOW_FILES + btn.BACK_TO_EARLIER_REMIND + btn.EDIT_PART_OF_MENU))
    await state.update_data(remind_new=(new_remind, categories, files))
    await state.update_data(is_new=True)
    await state.set_state(ChangeRemind.choose_to_edit)


@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_into_early"))
@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_into_new"))
async def back_remind_switch(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    remind_tmp, categories, files = info["remind_" + ("new", "tmp")[info["is_new"]]]

    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id,
                                     text=msg.get_remind_text(remind_tmp, categories),
                                     reply_markup=kb.get_keyboard(
                                    btn.SHOW_FILES + btn.BACK_TO_NEW_REMIND + btn.EDIT_PART_OF_MENU))
    await state.update_data(is_new=not info["is_new"])
