from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select

from attachements import buttons as btn
from attachements import keyboard as kb
from database.db import db
from database.models import File
from attachements import message as msg
from filters.callback import ShowFilesSCCallBack, BackSCCallBack, \
    FilesListCallBack, CloseCallBack, MaRCallBack

router = Router()


@router.callback_query(ShowFilesSCCallBack.filter())
async def show_files_from_schedular_remind(query: CallbackQuery, callback_data: ShowFilesSCCallBack,
                                           state: FSMContext, bot=Bot):
    current_reply = query.message.reply_markup
    current_id = callback_data.id
    files_sc = (await state.get_data()).get("schedular_files")
    past_replies = (await state.get_data()).get("past_replies")

    if past_replies is None:
        past_replies = {}

    past_replies[current_id] = current_reply
    await state.update_data(past_replies=past_replies)

    if files_sc is None:

        files_ = db.sql_query(query=select(File.file_name, File.id).where(File.remind_id == current_id),
                              is_single=False)
        files_sc = {current_id: files_}
    else:
        files_ = files_sc.get(callback_data.id)
        if files_ is None:
            files_ = db.sql_query(query=select(File.file_name, File.id).where(File.remind_id == current_id),
                                  is_single=False)

    files_btn = kb.get_files_list_of_btn(files_)

    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(files_btn,
                                                                       [(btn.BACK_TO_REMIND_SC,
                                                                         BackSCCallBack(id=current_id))]))
    await state.update_data(schedular_files=files_sc)


@router.callback_query(BackSCCallBack.filter())
async def back_to_remind(query: CallbackQuery, callback_data: BackSCCallBack,
                         state: FSMContext, bot: Bot):
    past_replies = (await state.get_data()).get("past_replies")
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=past_replies[callback_data.id])


@router.callback_query(FilesListCallBack.filter())
async def check_file(query: CallbackQuery, callback_data: FilesListCallBack,
                     state: FSMContext, bot: Bot):
    url = db.sql_query(query=select(File.file_url).where(File.id == callback_data.file_id), is_single=True)
    await bot.send_document(chat_id=query.from_user.id, document=url)


@router.callback_query(CloseCallBack.filter(F.action == "close_remind_sc"))
async def close_remind(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)


# @router.callback_query(MaRCallBack.filter())
# async def close_remind(query: CallbackQuery, callback_data: MaRCallBack,
#                        state: FSMContext, bot: Bot):
#
#     await bot.edit_message_text(chat_id=query.from_user.id,
#                                 message_id=query.message.message_id,
#                                 text=msg.MSG_WANNA_CHANGE_DATE_DEADLINE)
#
#     await bot.edit_message_reply_markup(chat_id=query.from_user.id,
#                                         message_id=query.message.message_id,
#                                         reply_markup=btn.CONFIRM_SC)
#
#     await state.update_data(date_start_sc=)