from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from filters.states import AddRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, RemindTypeCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc

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
async def add_category_finish(query: CallbackQuery, state: FSMContext, bot=Bot):
    await state.update_data(remind_description=query.text)
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


@router.callback_query(AddRemind.add_deadline_time, ConfirmCallback.filter(F.confirm == True))
async def date_confirmed(query: CallbackQuery, state: FSMContext, bot: Bot):
    id_to_del = (await state.get_data()).get("id_delete_msg")
    remind_type = (await state.get_data()).get("remind_type")
    is_start_date = (await state.get_data()).get("is_start_date")
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    if id_to_del:
        await bot.delete_message(chat_id=query.from_user.id, message_id=id_to_del)

    if remind_type == "common":
        await bot.send_message(chat_id=query.from_user.id,
                               text=msg.TRY_INPUT_REMIND_FILE,
                               reply_markup=kb.get_keyboard(btn.CONFIRMING))
        await state.set_state(AddRemind.try_add_file)
    elif remind_type != "common" and not is_start_date:
        start_date = (await state.get_data()).get("start_date")
        await bot.send_message(chat_id=query.from_user.id,
                               text=msg.MSG_SHOORING_IN_PERIODIC_START_DATE + start_date.strftime("%d-%m-%y %H:%M"),
                               reply_markup=kb.get_keyboard(btn.BACK_TO_START_DATE_OR_START_INTERVAL))
        await state.set_state(AddRemind.interval_start)

    elif remind_type != "common" and is_start_date:

    else:
        await state.update_data(is_start_date=False)




@router.callback_query(AddRemind.try_add_file,
                       ConfirmCallback.filter(F.confirm == True))
async def start_input_file(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_REMIND_FILE)
    await state.update_data(is_one_add=True)
    await state.set_state(AddRemind.add_file)


@router.message(AddRemind.add_file, F.document)
async def input_file(query: CallbackQuery, state: FSMContext, bot: Bot):
    # await bot.delete_message(chat_id=query.from_user.id, message_id=query.message_id)
    files_list = (await state.get_data()).get("list_remind_files")
    is_one_add = (await state.get_data()).get("is_one_add")
    file_name = query.document.file_name
    files_list.append((file_name, query.document.file_id))
    if is_one_add:
        await state.update_data(is_one_add=False)
        await bot.send_message(chat_id=query.from_user.id,
                               text=msg.TRY_INPUT_REMIND_FILE,
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


# @router.callback_query(AddRemind.try_add_category,
#                        ConfirmCallback.filter(F.confirm == False))
# @router.callback_query(AddRemind.end, ConfirmCallback.filter(F.confirm == False))
# async def add_category_finish(query: CallbackQuery, state: FSMContext, bot=Bot):
#     await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
#     await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_TYPE_OF_REMIND,
#                            reply_markup=kb.get_keyboard(btn.TYPE_REMIND))
#     await state.set_state(AddRemind.add_type)


@router.callback_query(AddRemind.try_add_category, ConfirmCallback.filter(F.confirm ==  False))
async def adding_remind_end(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.ADDING_FINISH)
    # TODO: Добавление в бд.
    info = await state.get_data()

    name_ = info["remind_name"]
    user_id_ = info["user_id"]
    interval_time = info.get("interval_time_")
    is_at_time = info.get("is_at_time")
    date_last_notificated = info.get("test_date_curr")

    if not interval_time:
        interval = null()
        year = null()
        month = null()
        is_at_time = null()
        date_last_notificated = null()
    else:
        year, month, interval = interval_time

    id = db.create_object(model=Remind(
        name=name_,
        text=info["remind_description"],
        date_deadline=info["choosed_data"],
        user_id=user_id_,
        interval=interval,
        ones_month=month,
        ones_years=year,
        is_at_time=is_at_time,
        date_last_notificate=date_last_notificated
    ))

    db.create_objects([File(remind_id=id,
                            file_name=file_name_,
                            file_url=file_url_)
                       for file_name_, file_url_ in info["list_remind_files"]])

    db.create_objects([Category(remind_id=id,
                                category_name=category_name_) for category_name_ in info["list_category"]])
    await state.clear()
