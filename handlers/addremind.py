import os

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import AddRemind
from aiogram import Router, Bot, F
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, RemindTypeCallBack
from aiogram.types import Message, CallbackQuery
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, null
from googledrive.helper import get_credentials, upload_file_to_drive

router = Router()


# TODO: При добавлении напоминаний удалить сообщение с типом напоминания И подтверждение.
@router.message(Command(commands="add"))
async def start_adding(message: Message, state: FSMContext):
    user = db.sql_query(query=select(User.name, User.id).where(
        User.user_id == str(message.from_user.id)), is_single=False)
    await state.update_data(user_name=user[0][0])
    await state.update_data(user_id=user[0][1])
    await state.update_data(list_remind_files=[])
    await state.update_data(list_category=[])
    await state.update_data(is_changing=False)
    await message.answer(user[0][0] + ", " + msg.INPUT_REMIND_NAME)
    await state.set_state(AddRemind.add_name)


@router.message(AddRemind.add_name, F.text)
async def input_name(message: Message, state: FSMContext):
    info = await state.get_data()
    await message.answer(info["user_name"] + ", " + msg.INPUT_REMIND_TEXT)
    await state.update_data(remind_name=message.text)
    await state.set_state(AddRemind.add_description)


@router.message(AddRemind.add_description)
@router.callback_query(AddRemind.add_type, ConfirmCallback.filter(F.confirm == False))
async def add_category_finish(query: CallbackQuery, state: FSMContext, bot=Bot):

    if await state.get_state() == AddRemind.add_description:
        await state.update_data(remind_description=query.text)
    else:
        await bot.delete_message(chat_id=query.from_user.id,
                                 message_id=query.message.message_id)

    await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_TYPE_OF_REMIND,
                           reply_markup=kb.get_keyboard(btn.TYPE_REMIND))

    await state.set_state(AddRemind.add_type)


@router.callback_query(AddRemind.add_type, RemindTypeCallBack.filter())
async def confirming_adding_type(query: CallbackQuery, callback_data: RemindTypeCallBack, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.SHORING_MSG,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.update_data(remind_type=callback_data.type)
    await state.update_data(is_start_date=True)


## goto calendary handler


@router.callback_query(AddRemind.add_deadline_end, ConfirmCallback.filter(F.confirm == True))
async def date_confirmed(query: CallbackQuery, state: FSMContext, bot: Bot):
    id_to_del = (await state.get_data()).get("id_delete_msg")
    id_calendary = (await state.get_data()).get("id_msg_calendary")

    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.delete_message(chat_id=query.from_user.id, message_id=id_calendary)

    if id_to_del:
        await bot.delete_message(chat_id=query.from_user.id, message_id=id_to_del)

    date_deadline = (await state.get_data()).get("date_deadline")

    if date_deadline is None:
        date_deadline = (await state.get_data()).get("date_start")

    await bot.send_message(chat_id=query.from_user.id,
                           text=f'Вы выбрали в качестве дедлайна дату: {date_deadline.strftime("%Y-%m-%d %H:%M")}.')

    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.TRY_INPUT_REMIND_FILE,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.set_state(AddRemind.try_add_file)


@router.callback_query(AddRemind.try_add_file,
                       ConfirmCallback.filter(F.confirm == True))
async def start_input_file(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_REMIND_FILE)
    await state.update_data(is_one_add=True)
    await state.set_state(AddRemind.add_file)


@router.message(AddRemind.add_file)
async def input_file(query: CallbackQuery, state: FSMContext, bot: Bot):
    credentials = get_credentials()

    is_one_add = (await state.get_data()).get("is_one_add")

    file_path = file_name = file_info = None

    if query.document:
        file_info = await query.bot.get_file(query.document.file_id)
        file_path = os.path.join("tmp", file_info.file_unique_id)
        file_name = query.document.file_name
    elif query.photo:
        file_info = await query.bot.get_file(query.photo[-1].file_id)
        file_name = f"photo_{file_info.file_unique_id}.jpg"
        file_path = os.path.join("tmp", file_name)

    if file_path and file_name:

        try:
            await bot.download_file(file_info.file_path, file_path)
            drive_file_url = upload_file_to_drive(file_name, file_path, credentials)
            files_list = (await state.get_data()).get("list_remind_files")
            files_list.append((file_name, drive_file_url))
            await state.update_data(list_remind_files=files_list)

            await query.answer("Файл успешно загружен на Google Drive.")

        except Exception as e:
            await query.answer("Произошла ошибка при загрузке файла на Google Drive.")
            print(e)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

        if is_one_add:
            await state.update_data(is_one_add=False)
            await bot.send_message(chat_id=query.from_user.id,
                                   text=msg.TRY_INPUT_MORE_REMIND_FILE,
                                   reply_markup=kb.get_keyboard(btn.CONFIRMING))

    await state.set_state(AddRemind.try_add_file)


@router.callback_query(AddRemind.try_add_file,
                       ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.try_add_category, ConfirmCallback.filter(F.confirm == True))
async def input_pic(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.INPUT_REMIND_CATEGORY)
    await state.set_state(AddRemind.add_category)


@router.message(AddRemind.add_category)
async def start_add_category(query: CallbackQuery, state: FSMContext, bot=Bot):
    category_list = (await state.get_data()).get("list_category")
    curr_state = await state.get_state()

    if curr_state == AddRemind.add_category:
        category_list.append(query.text)
    else:
        category_list.append(query.message.text)

    await state.update_data(list_category=category_list)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.TRY_INPUT_REMIND_CATEGORY,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.set_state(AddRemind.try_add_category)


@router.callback_query(AddRemind.try_add_category, ConfirmCallback.filter(F.confirm == False))
async def adding_remind_end(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.ADDING_FINISH)
    info = await state.get_data()

    name_ = info["remind_name"]
    user_id_ = info["user_id"]
    interval_time = info.get("interval_time_")
    date_last_notificated = info.get("date_start")
    date_deadline = info.get("date_deadline")

    if not date_deadline:
        date_deadline = date_last_notificated

    if not interval_time:
        interval = null()
        year = null()
        month = null()
    else:
        year, month, interval = interval_time

    id = db.create_object(model=Remind(
        name=name_,
        text=info["remind_description"],
        date_deadline=date_deadline,
        user_id=user_id_,
        interval=interval,
        ones_month=month,
        ones_years=year,
        date_last_notificate=date_last_notificated
    ))

    db.create_objects([File(remind_id=id,
                            file_name=file_name_,
                            file_url=file_url_)
                       for file_name_, file_url_ in info["list_remind_files"]])

    db.create_objects([Category(remind_id=id,
                                category_name=category_name_) for category_name_ in info["list_category"]])
    await state.clear()
