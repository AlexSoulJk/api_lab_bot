from io import BytesIO

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

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

from googledrive.helper import get_credentials

router = Router()


@router.message(Command(commands="check"))
@router.message(Command(commands="check_daily"))
async def start_adding(message: Message, state: FSMContext):

    user = db.sql_query(query=select(User.name, User.id).where(
        User.user_id == str(message.from_user.id)), is_single=False)

    user_id_ = user[0][1]
    remind_list = []
    if message.text == "/check":
        remind_list = db.sql_query(query=select(Remind.name, Remind.id).where(
            Remind.user_id == user_id_).where(Remind.date_finish == null()).where(
            Remind.date_is_delete == null()).order_by(Remind.date_last_notificate), is_single=False)

    elif message.text == "/check_daily":
        remind_list = db.sql_query(query=select(Remind.name, Remind.id).where(
            Remind.user_id == user_id_).where(
            Remind.date_last_notificate - datetime.datetime.now() < datetime.timedelta(days=1)).where(
            Remind.date_finish == null()), is_single=False)

    remind_list_btn = kb.get_remind_list_of_btn(remind_list)
    await state.update_data(user_name=user[0][0])
    await state.update_data(cur_chunk=1)
    await state.update_data(reminds=remind_list_btn)
    await state.update_data(list_info="reminds")
    await message.answer(text=user[0][0] + ", " + msg.CHECK_START,
                         reply_markup=kb.get_smart_list(remind_list_btn, btn.CLOSE_REMIND_LIST))
    await state.set_state(CheckRemind.start)

@router.callback_query(CheckRemind.check_remind,
                       BackButtonCallBack.filter(F.action == "back_to_remind_list"))
async def back_to_list(query: CallbackQuery, state: FSMContext, bot: Bot):
    user_info = await state.get_data()
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=user_info["user_name"] + ", " + msg.CHECK_START,
    reply_markup=kb.get_smart_list(user_info["reminds"], btn.CLOSE_REMIND_LIST))
    await state.update_data(list_info="reminds")
    await state.set_state(CheckRemind.start)

@router.callback_query(CheckRemind.start,
                       ButLeftRightCallBack.filter(F.action == "past_chunk"))
@router.callback_query(CheckRemind.start,
                       ButLeftRightCallBack.filter(F.action == "next_chunk"))
@router.callback_query(CheckRemind.check_files_list,
                       ButLeftRightCallBack.filter(F.action == "past_chunk"))
@router.callback_query(CheckRemind.check_files_list,
                       ButLeftRightCallBack.filter(F.action == "next_chunk"))
async def wish_list_move(query: CallbackQuery, callback_data: ButLeftRightCallBack,
                         state: FSMContext, bot: Bot):

    user_info = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_smart_list(user_info[user_info["list_info"]], btn.LIST_MOVES[user_info["list_info"]],
                                                                       callback_data.new_chunk))
    await state.update_data(cur_chunk=callback_data.new_chunk)


@router.callback_query(CheckRemind.start, RemindListCallBack.filter())
async def check_remind(query: CallbackQuery, callback_data: RemindListCallBack,
                       state: FSMContext, bot: Bot):

    remind = db.sql_query(query=select(Remind).where(Remind.id == callback_data.remind_id), is_single=True)
    categories_ = db.sql_query(query=select(Category.category_name, Category.id).where(Category.remind_id == remind.id),
                              is_single=False)

    files_ = db.sql_query(query=select(File.file_name, File.id).where(File.remind_id == remind.id), is_single=False)
    files_btn = kb.get_files_list_of_btn(files_)
    obj = t.create_tmp(remind, files_, categories_)
    await state.update_data(remind_tmp=obj)
    await state.update_data(remind_id=callback_data.remind_id)
    await state.update_data(file_btn=files_btn)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.get_remind_text_(obj),
                           reply_markup=kb.get_keyboard(btn.REMIND_MENU_BAR), parse_mode="HTML")
    await state.set_state(CheckRemind.check_remind)


@router.callback_query(CheckRemind.check_remind, ShowFilesCallBack.filter())
async def show_file_list(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = (await state.get_data()).get("file_btn")
    await state.update_data(list_info="file_btn")
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(info, btn.BACK_TO_REMIND))
    await state.set_state(CheckRemind.check_files_list)


@router.callback_query(CheckRemind.check_files_list, BackButtonCallBack.filter(F.action == "back_to_remind"))
@router.callback_query(ChangeRemind.start, BackButtonCallBack.filter(F.action == "back_to_remind"))
async def back_to_remind(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=kb.get_keyboard(btn.REMIND_MENU_BAR))
    await state.set_state(CheckRemind.check_remind)





@router.callback_query(CheckRemind.start, CloseCallBack.filter(F.action=="close_list"))
async def close(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.update_data()
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHECK_END + info["user_name"])
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await state.clear()