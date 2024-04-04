from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, ChangeRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from attachements import tools as t
from filters.callback import ConfirmCallback, EditRemindCallBack, EditOptionCallBack, BackButtonCallBack, \
    CheckSampleRemind, SkipCallback, EditFilesCallBack, EditOptionObject, ButLeftRightCallBack, ShowFilesCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from copy import deepcopy
from calendary import calendary as c
from calendary.common import get_user_locale
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc, delete
import datetime

router = Router()


# TODO: Debug list_add key??????
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
        await state.update_data(add_objects={"files": [],
                                             "categories": []})
    await state.update_data(msg_remind_id=query.message.message_id)
    await state.set_state(ChangeRemind.start)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "name"))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "description"))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "date_deadline"))
async def change_without_option_start(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=None)
    key = str(callback_data.action)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.CHANGE_DICT[key],
                           reply_markup=(await c.DialogCalendar(locale=await get_user_locale(query.from_user)
                                                                ).start_calendar(), None)[
                               key != "date_deadline"]
                           )
    await state.update_data(cur_change=key)
    await state.set_state(
        (ChangeRemind.change_text, ChangeRemind.change_deadline)[callback_data.action == "date_deadline"])


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "files"))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "categories"))
async def change_with_option_start(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=None)
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_OPTION,
                           reply_markup=kb.get_keyboard(btn.ADD_OR_DELETE))
    await state.update_data(cur_change=callback_data.action)
    await state.set_state(ChangeRemind.choose_option)


@router.message(ChangeRemind.change_text, F.text)
async def change_text(query: CallbackQuery, state: FSMContext, bot: Bot):
    remind = (await state.get_data()).get("remind_new")
    cur_change = (await state.get_data()).get("cur_change")
    remind[cur_change] = query.text
    await state.update_data(remind_new=remind)
    await bot.send_message(chat_id=query.from_user.id, text=msg.SHOW_SAMPLE,
                           reply_markup=kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))
    await state.set_state(ChangeRemind.check_sample)


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
        cur_change = (await state.get_data()).get("cur_change")
        remind[cur_change] = date
        await state.update_data(remind_new=remind)
        await state.update_data(id_delete_msg=callback_query.message.message_id)
        await state.set_state(ChangeRemind.check_sample)


@router.callback_query(ChangeRemind.choose_option, EditFilesCallBack.filter(F.action == "add"))
async def process_optional_add_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    cur_change = (await state.get_data()).get("cur_change")
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_DICT_ADDING_OBJ[cur_change])
    await state.update_data(is_one_add=True)
    await state.set_state(ChangeRemind.add_object)


@router.message(ChangeRemind.add_object, F.document)
@router.message(ChangeRemind.add_object, F.text)
async def process_optional_add_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    cur_change = (await state.get_data()).get("cur_change")
    list_to_add = (await state.get_data()).get("add_objects")
    is_add_one = (await state.get_data()).get("is_one_add")
    if cur_change == "files":
        list_to_add[cur_change].append((query.document.file_name, query.document.file_id))
    elif cur_change == "categories":
        list_to_add[cur_change].append(query.text)

    await state.update_data(add_objects=list_to_add)

    if is_add_one:
        await state.update_data(is_one_add=False)
        await bot.send_message(chat_id=query.from_user.id, text=msg.SHOW_SAMPLE,
                               reply_markup=kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))

    await state.set_state(ChangeRemind.check_sample)


@router.callback_query(ChangeRemind.choose_option, EditFilesCallBack.filter(F.action == "delete"))
async def process_optional_start_delete(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    cur_change = (await state.get_data()).get("cur_change")
    list_of_btn = kb.get_optional_object_btn((await state.get_data()).get("remind_tmp")[cur_change])
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_DICT_OPTIONAL_OBJ[cur_change],
                           reply_markup=kb.get_smart_list(list_of_btn, btn.SUBMIT_DELETE))
    await state.update_data(list_to_delete=list_of_btn)
    await state.set_state(ChangeRemind.choose_delete)


@router.callback_query(ChangeRemind.choose_delete, EditOptionObject.filter(F.id != -1))
async def process_optional_choose_delete_obj(query: CallbackQuery,
                                             callback_data: CallbackData,
                                             state: FSMContext,
                                             bot: Bot):
    list_of_btn = kb.update_delete_list(
        (await state.get_data()).get("list_to_delete"),
        callback_data.id)
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(list_of_btn, btn.SUBMIT_DELETE))
    await state.update_data(list_to_delete=list_of_btn)


@router.callback_query(CheckRemind.check_files_list,
                       ButLeftRightCallBack.filter(F.action == "past_chunk"))
@router.callback_query(CheckRemind.check_files_list,
                       ButLeftRightCallBack.filter(F.action == "next_chunk"))
async def delete_list_move(query: CallbackQuery, callback_data: ButLeftRightCallBack,
                           state: FSMContext, bot: Bot):
    list_btn = (await state.get_data()).get("list_to_delete")
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_smart_list(list_btn,
                                                                       btn.SUBMIT_DELETE,
                                                                       callback_data.new_chunk))
    await state.update_data(cur_chunk=callback_data.new_chunk)


@router.callback_query(ChangeRemind.choose_delete, EditOptionObject.filter(F.id == -1))
async def process_optional_finish(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.SHOW_SAMPLE,
                           reply_markup=kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))

    list_btn = (await state.get_data()).get("list_to_delete")
    cur_change = (await state.get_data()).get("cur_change")
    remind_new = (await state.get_data()).get("remind_new")
    delete_dict = (await state.get_data()).get("delete_dict")

    ids_to_delete = t.check_to_delete(list_btn)
    remind_new[cur_change] = t.get_current_items(remind_new[cur_change], ids_to_delete)

    if delete_dict is None:
        delete_dict = {}
    delete_dict[cur_change] = ids_to_delete

    await state.update_data(remind_new=remind_new)
    await state.update_data(delete_dict=delete_dict)
    await state.set_state(ChangeRemind.check_sample)


@router.callback_query(ChangeRemind.check_sample, CheckSampleRemind.filter(F.action == "check"))
async def check_sample(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    await bot.delete_message(chat_id=query.from_user.id, message_id=info["msg_remind_id"])
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    id_to_delete = info.get("id_delete_msg")

    if id_to_delete is not None:
        await bot.delete_message(chat_id=query.from_user.id, message_id=id_to_delete)

    await bot.send_message(chat_id=query.from_user.id, text=msg.get_remind_text_(info["remind_new"],
                                                                                 info["add_objects"]["categories"]),
                           reply_markup=kb.get_keyboard(
                               btn.SHOW_FILES + btn.BACK_TO_EARLIER_REMIND + btn.EDIT_PART_OF_MENU))
    await state.update_data(is_new=True)
    await state.set_state(ChangeRemind.choose_to_edit)


@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_into_early"))
@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_into_new"))
@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_to_remind"))
async def back_remind_switch(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id,
                                text=msg.get_remind_text_(info["remind_" + ("new", "tmp")[info["is_new"]]]),
                                reply_markup=kb.get_keyboard(
                                    btn.SHOW_FILES + (btn.BACK_TO_EARLIER_REMIND, btn.BACK_TO_NEW_REMIND)[
                                        info["is_new"]]
                                    + btn.EDIT_PART_OF_MENU))
    await state.update_data(is_new=not info["is_new"])


@router.callback_query(ChangeRemind.choose_to_edit, ShowFilesCallBack.filter(F.action == "show"))
async def show_files(query: CallbackQuery, state: FSMContext, bot: Bot):
    is_new = (await state.get_data()).get("is_new")
    remind = (await state.get_data()).get("remind_" + ("new", "tmp")[not is_new])
    add_files = ((await state.get_data()).get("add_list")["files"], None)[not is_new]
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(
                                            kb.get_files_list_of_btn(remind["files"], add_files),
                                            btn.BACK_TO_REMIND))
    await state.update_data(is_new=not is_new)


@router.callback_query(ChangeRemind.choose_to_edit, EditRemindCallBack.filter(F.action == "end"))
@router.callback_query(ChangeRemind.check_sample, SkipCallback.filter(F.skip == True))
async def insert_changes(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    remind_id = (await state.get_data()).get("remind_id")
    remind_new = (await state.get_data()).get("remind_new")
    delete_list = (await state.get_data()).get("delete_dict")
    id_delete_msg = (await state.get_data()).get("msg_remind_id")
    add_dict = (await state.get_data()).get("add_objects")

    db.sql_query(query=update(Remind).where(Remind.id == remind_id).values(name=remind_new["name"],
                                                                           text=remind_new["description"],
                                                                           date_deadline=remind_new["date_deadline"],
                                                                           ), is_single=True, is_update=True)
    if delete_list:
        delete_id_categories = delete_list.get("categories")
        delete_id_files = delete_list.get("files")
        if delete_id_categories:
            db.sql_query(query=delete(Category).where(Category.id.in_(delete_id_categories)), is_update=True)

        if delete_id_files:
            db.sql_query(query=delete(File).where(File.id.in_(delete_id_files)), is_update=True)

    if len(add_dict["files"]):
        db.create_objects([File(remind_id=remind_id,
                                file_name=file_name_,
                                file_url=file_url_)
                           for file_name_, file_url_ in add_dict["files"]])

    if len(add_dict["categories"]):
        db.create_objects([Category(remind_id=remind_id,
                                    category_name=category_name_)
                           for category_name_ in add_dict["categories"]])

    #await bot.delete_message(chat_id=query.from_user.id, message_id=id_delete_msg)

    await bot.send_message(chat_id=query.from_user.id, text=msg.EDIT_FINISH)
    await state.clear()
