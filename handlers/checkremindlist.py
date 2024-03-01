from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, ButLeftRightCallBack, RemindListCallBack, ShowFilesCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc
import datetime

router = Router()


@router.message(Command(commands="check"))
async def start_adding(message: Message, state: FSMContext):

    user = db.sql_query(query=select(User.name, User.id).where(
        User.user_id == str(message.from_user.id)), is_single=False)

    user_id_ = user[0][1]

    remind_list = db.sql_query(query=select(Remind.name, Remind.id).where(
        Remind.user_id == user_id_).where(Remind.date_finish == null()), is_single=False)
    remind_list_btn = kb.get_remind_list_of_btn(remind_list)
    await state.update_data(user_name=user[0][0])
    await state.update_data(cur_chunk=1)
    await state.update_data(reminds=remind_list_btn)
    await message.answer(text=user[0][0] + ", " + msg.CHECK_START, reply_markup=kb.get_smart_list(remind_list_btn))
    await state.set_state(CheckRemind.start)


@router.callback_query(CheckRemind.start,
                       ButLeftRightCallBack.filter(F.action == "past_chunk"))
@router.callback_query(CheckRemind.start,
                       ButLeftRightCallBack.filter(F.action == "next_chunk"))
async def wish_list_move(query: CallbackQuery, callback_data: ButLeftRightCallBack,
                         state: FSMContext, bot: Bot):

    user_info = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_smart_list(user_info["reminds"], callback_data.new_chunk))
    await state.update_data(cur_chunk=callback_data.new_chunk)


@router.callback_query(CheckRemind.start, RemindListCallBack.filter())
async def check_remind(query: CallbackQuery, callback_data: RemindListCallBack,
                       state: FSMContext, bot: Bot):

    remind = db.sql_query(query=select(Remind).where(Remind.id == callback_data.remind_id), is_single=True)
    categories = db.sql_query(query=select(Category.category_name).where(Category.remind_id == remind.id),
                              is_single=False)

    files_ = db.sql_query(query=select(File.file_name, File.id).where(File.remind_id == remind.id), is_single=False)
    files_btn = kb.get_files_list_of_btn(files_)
    await state.update_data(remind_tmp=remind)
    await state.update_data(files=files_btn)
    await bot.send_message(chat_id=query.from_user.id, text=msg.get_remind_text(remind, categories),
                           reply_markup=kb.get_keyboard(btn.SHOW_FILES + btn.BACK_TO_REMIND_LIST))
    await state.set_state(CheckRemind.check_remind)


@router.callback_query(CheckRemind.check_remind, ShowFilesCallBack.filter())
async def show_file_list(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = (await state.get_data()).get("files")
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(info))
    await state.set_state(CheckRemind.check_files_list)


@router.callback_query(CheckRemind.check_files_list,
                       ButLeftRightCallBack.filter(F.action == "past_chunk"))
@router.callback_query(CheckRemind.check_files_list,
                       ButLeftRightCallBack.filter(F.action == "next_chunk"))
async def wish_list_move(query: CallbackQuery, callback_data: ButLeftRightCallBack,
                         state: FSMContext, bot: Bot):

    user_info = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_smart_list(user_info["files"], callback_data.new_chunk))
    await state.update_data(cur_chunk=callback_data.new_chunk)