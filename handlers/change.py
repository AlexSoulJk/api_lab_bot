import os
from copy import deepcopy
from aiogram import Router, Bot, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from googleapiclient.errors import HttpError
from sqlalchemy import update, delete, null, select
from attachements import buttons as btn
from attachements import keyboard as kb
from attachements import message as msg
from attachements import tools as t
from database.db import db
from database.models import File, Remind, Category
from filters.callback import EditRemindCallBack, EditOptionCallBack, BackButtonCallBack, \
    CheckSampleRemind, SkipCallback, EditFilesCallBack, EditOptionObject, ButLeftRightCallBack, ShowFilesCallBack, \
    ConfirmCallback
from filters.states import CheckRemind, ChangeRemind
from googledrive.helper import upload_file_to_drive, get_credentials
from googleapiclient.discovery import build

router = Router()


@router.callback_query(CheckRemind.check_remind,
                       EditRemindCallBack.filter(F.action == "edit"))
@router.callback_query(ChangeRemind.choose_to_edit,
                       EditRemindCallBack.filter(F.action == "edit_more"))
@router.callback_query(ChangeRemind.type,
                       ConfirmCallback.filter(F.confirm == False))
async def start_changing(query: CallbackQuery, state: FSMContext, bot: Bot):
    curr_state = await state.get_state()
    info = await state.get_data()

    if curr_state == ChangeRemind.type:
        await bot.delete_message(chat_id=query.from_user.id,
                                 message_id=query.message.message_id)

    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=(query.message.message_id,
                                                    info.get("msg_remind_id"))[curr_state == ChangeRemind.type],
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_keyboard(btn.EDIT_REMIND_LIST + btn.BACK_TO_REMIND))

    if curr_state == CheckRemind.check_remind:
        await state.update_data(remind_new=deepcopy(info["remind_tmp"]))
        await state.update_data(add_objects={"files": {-1: ""},
                                             "categories": []})
        await state.update_data(is_changing=True)
    await state.update_data(msg_remind_id=query.message.message_id)
    await state.set_state(ChangeRemind.start)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "name"))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "description"))
async def change_without_option_start(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=None)
    key = str(callback_data.action)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.CHANGE_DICT[key])
    await state.update_data(cur_change=key)
    await state.set_state(ChangeRemind.change_text)


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "time"))
async def time_changing_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    new_remind = (await state.get_data()).get("remind_new")

    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        inline_message_id=query.inline_message_id,
                                        reply_markup=kb.get_keyboard(btn.EDIT_REMIND_TIME[:(3, 1)[
                                            new_remind["type"] == "common"]] + btn.BACK_TO_REMIND))


@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "type"))
async def change_type(query: CallbackQuery, state: FSMContext, bot: Bot):
    new_remind = (await state.get_data()).get("remind_new")
    new_type = ("common", "periodic")[new_remind["type"] == "common"]

    await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                        message_id=query.message.message_id,
                                        reply_markup=None)

    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_TYPE_WARNING + ("периодическое.",
                                                                                       "обычное.")[
        new_type == "common"],
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))

    await state.update_data(remind_type=new_type)

    await state.set_state(ChangeRemind.type)


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


@router.callback_query(ChangeRemind.choose_option, EditFilesCallBack.filter(F.action == "add"))
async def process_optional_add_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    cur_change = (await state.get_data()).get("cur_change")
    await bot.send_message(chat_id=query.from_user.id, text=msg.CHANGE_DICT_ADDING_OBJ[cur_change])
    await state.update_data(is_one_add=True)
    await state.set_state(ChangeRemind.add_object)


@router.message(ChangeRemind.add_object)
async def process_optional_add_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    cur_change = (await state.get_data()).get("cur_change")
    list_to_add = (await state.get_data()).get("add_objects")
    is_add_one = (await state.get_data()).get("is_one_add")

    if cur_change == "files":
        cur_number_of_file = (await state.get_data()).get("last_id", -1)
        if query.document:
            file_name = query.document.file_name
            file_info = await query.bot.get_file(query.document.file_id)
            file_path = os.path.join("tmp", file_info.file_unique_id)
            url = query.document.file_id
            flag = True
        elif query.photo:
            file_info = await query.bot.get_file(query.photo[-1].file_id)
            file_name = f"photo_{file_info.file_unique_id}.jpg"
            file_path = os.path.join("tmp", file_name)
            url = query.photo[-1].file_id
            flag = False
        else:
            await bot.send_message(chat_id=query.from_user.id,
                                   text="Можно загрузить или фото, или документ. \nПопробуйте снова.")
            return

        await bot.download_file(file_info.file_path, file_path)

        list_to_add[cur_change][cur_number_of_file] = ((file_name,
                                                        file_path,
                                                        file_info.file_path,
                                                        url,
                                                        flag))

        await state.update_data(last_id=cur_number_of_file - 1)
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
    cur_chunk = (await state.get_data()).get("cur_chunk")
    list_of_btn = kb.update_delete_list(
        (await state.get_data()).get("list_to_delete"),
        callback_data.id)
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(list_of_btn,
                                                                       btn.SUBMIT_DELETE,
                                                                       cur_chunk))
    await state.update_data(list_to_delete=list_of_btn)


@router.callback_query(ChangeRemind.choose_delete,
                       ButLeftRightCallBack.filter(F.action == "past_chunk"))
@router.callback_query(ChangeRemind.choose_delete,
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
                               btn.SHOW_FILES + btn.BACK_TO_EARLIER_REMIND + btn.EDIT_PART_OF_MENU),
                           parse_mode="HTML")
    await state.update_data(is_new=True)
    await state.set_state(ChangeRemind.choose_to_edit)


@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_into_early"))
@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_into_new"))
@router.callback_query(ChangeRemind.choose_to_edit, BackButtonCallBack.filter(F.action == "back_to_remind"))
async def back_remind_switch(query: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id,
                                text=msg.get_remind_text_(info["remind_" + ("new", "tmp")[info["is_new"]]],
                                                          (info["add_objects"]["categories"], None)[info["is_new"]]),
                                reply_markup=kb.get_keyboard(
                                    btn.SHOW_FILES + (btn.BACK_TO_EARLIER_REMIND, btn.BACK_TO_NEW_REMIND)[
                                        info["is_new"]]
                                    + btn.EDIT_PART_OF_MENU),
                                parse_mode="HTML")
    await state.update_data(is_new=not info["is_new"])


@router.callback_query(ChangeRemind.choose_to_edit, ShowFilesCallBack.filter(F.action == "show"))
async def show_files(query: CallbackQuery, state: FSMContext, bot: Bot):
    is_new = (await state.get_data()).get("is_new")
    remind = (await state.get_data()).get("remind_" + ("new", "tmp")[not is_new])
    add_files = ((await state.get_data()).get("add_objects")["files"], None)[not is_new]
    await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        reply_markup=kb.get_smart_list(
                                            kb.get_files_list_of_btn(remind["files"], add_files)
                                            + kb.get_add_files_list_of_btn(add_files),
                                            btn.BACK_TO_REMIND))
    await state.update_data(is_new=not is_new)



@router.callback_query(ChangeRemind.choose_to_edit, EditRemindCallBack.filter(F.action == "end"))
@router.callback_query(ChangeRemind.check_sample, SkipCallback.filter(F.skip == True))
async def insert_changes(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    remind_id = (await state.get_data()).get("remind_id")
    remind_new = (await state.get_data()).get("remind_new")
    delete_list = (await state.get_data()).get("delete_dict")
    add_dict = (await state.get_data()).get("add_objects")
    interval_ = remind_new.get("interval")
    year = month = interval = null()
    if interval_ is not None:
        year, month, interval = interval_.to_database()

    db.sql_query(query=update(Remind).where(Remind.id == remind_id).values(name=remind_new["name"],
                                                                           text=remind_new["description"],
                                                                           date_deadline=remind_new["date_deadline"],
                                                                           date_last_notificate=
                                                                           remind_new["date_last_notificate"],
                                                                           interval=interval,
                                                                           ones_month=month,
                                                                           ones_years=year,
                                                                           ), is_single=True, is_update=True)
    if delete_list:
        delete_id_categories = delete_list.get("categories")
        delete_id_files = delete_list.get("files")
        if delete_id_categories:
            db.sql_query(query=delete(Category).where(Category.id.in_(delete_id_categories)), is_update=True)

        if delete_id_files:
            credentials = get_credentials()
            service = build('drive', 'v3', credentials=credentials)

            urls = db.sql_query(query=select(File.file_name, File.file_url).where(File.id.in_(delete_id_files)),
                                is_update=False, is_single=False)

            for name, url in urls:
                try:
                    service.files().delete(fileId=url).execute()
                    print(f"Файл {name} успешно удален.")
                except HttpError as error:
                    print(f'Не удалось удалить файл {name}.\nHTTP ошибка: {error}')

            db.sql_query(query=delete(File).where(File.id.in_(delete_id_files)), is_update=True)

    if len(add_dict["files"]) and add_dict["files"][-1] != "":
        drive_url = []
        credentials = get_credentials()
        for file_name, file_path, file_path_t, _, _ in add_dict["files"].values():
            if file_path and file_name:
                try:
                    await bot.download_file(file_path_t, file_path)
                    drive_url.append((file_name, upload_file_to_drive(file_name, file_path, credentials)))
                except Exception as e:
                    await query.answer("Произошла ошибка при загрузке файла на Google Drive.")
                    print(e)
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

        db.create_objects([File(remind_id=remind_id,
                                file_name=file_name_,
                                file_url=file_url_)
                           for file_name_, file_url_ in drive_url])

    if len(add_dict["categories"]):
        db.create_objects([Category(remind_id=remind_id,
                                    category_name=category_name_)
                           for category_name_ in add_dict["categories"]])

    if await state.get_state() == ChangeRemind.check_sample:
        id_delete_msg = (await state.get_data()).get("msg_remind_id")
        await bot.delete_message(chat_id=query.from_user.id, message_id=id_delete_msg)

    await bot.send_message(chat_id=query.from_user.id, text=msg.EDIT_FINISH)
    await state.clear()
