from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, ChangeRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, EditRemindCallBack, EditOptionCallBack, BackButtonCallBack, CheckSampleRemind, SkipCallback
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from copy import deepcopy
from calendary import calendary as c
from calendary.common import get_user_locale
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc
import datetime

router = Router()


@router.callback_query(CheckRemind.check_remind,
                       EditRemindCallBack.filter(F.action == "edit"))
@router.callback_query(ChangeRemind.choose_to_edit,
                       EditRemindCallBack.filter(F.action == "edit_more"))
async def start_changing(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_keyboard(btn.EDIT_REMIND_LIST + btn.BACK_TO_REMIND))
    info = await state.get_data()
    if await state.get_state() == CheckRemind.check_remind:
        await state.update_data(remind_new=deepcopy(info["remind_tmp"]))
    await state.update_data(msg_remind_id=query.message.message_id)
    await state.set_state(ChangeRemind.start)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "name"))
async def change_name_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=None)
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_NAME)
    await state.set_state(ChangeRemind.change_name)


@router.message(ChangeRemind.change_name, F.text)
async def change_name_add(query: CallbackQuery, state: FSMContext, bot: Bot):
    remind = (await state.get_data()).get("remind_new")
    remind[0].name = query.text
    await state.update_data(remind_new=remind)
    await bot.send_message(chat_id=query.from_user.id, text=msg.SHOW_SAMPLE,
                           reply_markup=kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))
    await state.set_state(ChangeRemind.check_sample)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "description"))
async def change_description_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_DESCRIPTION)
    await state.set_state(ChangeRemind.change_description)


@router.message(ChangeRemind.change_description, F.text)
async def change_description_add(query: CallbackQuery, state: FSMContext, bot: Bot):
    remind = (await state.get_data()).get("remind_new")
    remind[0].text = query.text
    await state.update_data(remind_new=remind)
    await bot.send_message(chat_id=query.from_user.id, text=msg.SHOW_SAMPLE,
                           reply_markup=kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))
    await state.set_state(ChangeRemind.check_sample)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "deadline"))
async def change_deadline_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)
    await bot.send_message(chat_id=query.from_user.id,
        text=msg.CHANGE_DEADLINE,
        reply_markup=await c.DialogCalendar(
        locale=await get_user_locale(query.from_user)
        ).start_calendar()
    )
    await state.set_state(ChangeRemind.change_deadline)

@router.callback_query(ChangeRemind.change_deadline, c.DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await c.DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)

    if selected:
        await callback_query.message.answer(
            f'Вы выбрали {date.strftime("%Y-%m-%d")}.\n' + msg.SHOW_SAMPLE,
            reply_markup=kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT)
        )
        remind = (await state.get_data()).get("remind_new")
        remind[0].date_deadline = date
        await state.update_data(remind_new=remind)
        await state.update_data(id_delete_msg=callback_query.message.message_id)
        await state.set_state(ChangeRemind.check_sample)


@router.callback_query(ChangeRemind.check_sample, CheckSampleRemind.filter(F.action == "check"))
async def check_sample(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    remind, categories, files = info["remind_new"]
    await bot.delete_message(chat_id=query.from_user.id, message_id=info["msg_remind_id"])
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    id_to_delete = info.get("id_delete_msg")

    if id_to_delete is not None:
        await bot.delete_message(chat_id=query.from_user.id, message_id=id_to_delete)

    await bot.send_message(chat_id=query.from_user.id, text=msg.get_remind_text(remind, categories),
                           reply_markup=kb.get_keyboard(
                               btn.SHOW_FILES + btn.BACK_TO_EARLIER_REMIND + btn.EDIT_PART_OF_MENU))
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
                                    btn.SHOW_FILES + (btn.BACK_TO_EARLIER_REMIND,btn.BACK_TO_NEW_REMIND)[info["is_new"]]
                                    + btn.EDIT_PART_OF_MENU))
    await state.update_data(is_new=not info["is_new"])
