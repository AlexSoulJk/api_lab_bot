from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import AddRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback, RemindTypeCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from database.db import db
from database.models import User
from sqlalchemy import select, update, null, desc
import datetime

router = Router()


@router.message(Command(commands="add"))
async def start_adding(message: Message, state: FSMContext):
    user_name = db.sql_query(query=select(User.name).where(
        User.user_id == str(message.from_user.id)), is_single=True)
    await state.update_data(user_name=user_name)
    await message.answer(user_name + ", " + msg.INPUT_REMIND_NAME)
    await state.set_state(AddRemind.add_name)


@router.message(AddRemind.add_name)
async def input_name(message: Message, state: FSMContext):
    info = await state.get_data()
    await message.answer(info["user_name"] + ", " + msg.INPUT_REMIND_TEXT)
    await state.update_data(remind_name=message.text)
    await state.set_state(AddRemind.add_description)


## goto calendary handler
@router.callback_query(AddRemind.try_add_file,
                       ConfirmCallback.filter(F.confirm == True))
async def start_input_file(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_REMIND_FILE)
    await state.set_state(AddRemind.add_file)


@router.message(AddRemind.add_file, F.document)
@router.callback_query(AddRemind.try_add_file,
                       ConfirmCallback.filter(F.confirm == False))
async def input_file(query: CallbackQuery, state: FSMContext, bot=Bot):
    if await state.get_state() == AddRemind.add_file:
        file_name = query.document.file_name
        print(file_name)
        await state.update_data(remind_photo=query.document.file_id)
    else:
        await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.TRY_INPUT_REMIND_PICTURE,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))

    await state.set_state(AddRemind.try_add_pic)


@router.callback_query(AddRemind.try_add_pic,
                       ConfirmCallback.filter(F.confirm == True))
async def start_input_pic(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_REMIND_PICTURE)
    await state.set_state(AddRemind.add_pic)


@router.callback_query(AddRemind.try_add_pic,
                       ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.try_add_category, ConfirmCallback.filter(F.confirm == True))
@router.message(AddRemind.add_pic, F.photo)
async def input_pic(query: CallbackQuery, state: FSMContext, bot=Bot):
    if await state.get_state() == AddRemind.add_pic:
        await state.update_data(remind_photo=query.photo[-1].file_id)
    else:
        await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.INPUT_REMIND_CATEGORY)

    await state.set_state(AddRemind.add_category)


@router.message(AddRemind.add_category)
async def start_add_category(query: CallbackQuery, state: FSMContext, bot=Bot):
    category_list = (await state.get_data()).get("list_category")
    curr_state = await state.get_state()

    if category_list is None:
        category_list = []

    if curr_state == AddRemind.add_category:
        category_list.append(query.text)
    else:
        category_list.append(query.message.text)

    await state.update_data(list_category=category_list)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.TRY_INPUT_REMIND_CATEGORY,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.set_state(AddRemind.try_add_category)


@router.callback_query(AddRemind.try_add_category,
                       ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.end, ConfirmCallback.filter(F.confirm == False))
async def add_category_finish(query: CallbackQuery, state: FSMContext, bot=Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id, text=msg.INPUT_TYPE_OF_REMIND,
                           reply_markup=kb.get_keyboard(btn.TYPE_REMIND))
    await state.set_state(AddRemind.add_type)


@router.callback_query(AddRemind.add_type, RemindTypeCallBack.filter(F.type))
async def confirming_adding_type(query: CallbackQuery, callback_data: RemindTypeCallBack, state: FSMContext, bot: Bot):
    await state.update_data(type_of_rimind=callback_data.type)
    await bot.send_message(chat_id=query.from_user.id, text=msg.SHORING_MSG,
                           reply_markup=kb.get_keyboard(btn.CONFIRMING))
    await state.set_state(AddRemind.end)


@router.callback_query(AddRemind.end, ConfirmCallback.filter(F.confirm == True))
async def adding_remind_end(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(chat_id=query.from_user.id, text=msg.ADDING_FINISH)
    # TODO: Добавление в бд.
    await state.clear()
