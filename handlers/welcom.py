from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import WellCome
from aiogram import Router, Bot, F
from attachements import message as msg
from attachements import buttons as btn
from attachements import keyboard as kb
from aiogram.types import Message, CallbackQuery
from database.db import db
from database.models import User
from filters.callback import ConfirmCallback
from sqlalchemy import select, update

router = Router()


@router.message(Command(commands="start"))
@router.message(Command(commands="name"))
async def start_using(message: Message, state: FSMContext):
    name = db.sql_query(query=select(User.name).where(User.user_id == str(message.from_user.id)))
    if name:
        await message.answer(text=name + msg.WANNA_CHANGE_NAME, reply_markup=kb.get_keyboard(btn.CONFIRMING))
    else:
        await message.answer(msg.WELCOME_MSG)
    await state.set_state(WellCome.start)


@router.message(WellCome.start)
async def get_name(message: Message, state: FSMContext):
    db.create_object(User(name=message.text, user_id=message.from_user.id))
    await message.answer(text=msg.REMEMBER_YOU + message.text)
    await state.clear()


@router.callback_query(WellCome.start, ConfirmCallback.filter(F.confirm == True))
async def change_name(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.INPUT_NEW_NAME)
    await state.set_state(WellCome.change_name)


@router.message(WellCome.change_name)
async def get_new_name(message: Message, state: FSMContext):
    db.sql_query(query=update(User).where(User.user_id == str(message.from_user.id)).values(name=message.text),
                 is_update=True)
    await message.answer(text=msg.REMEMBER_YOU + message.text)
    await state.clear()


@router.callback_query(WellCome.start, ConfirmCallback.filter(F.confirm == False))
async def change_name_cancel(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=query.from_user.id,
                             message_id=query.message.message_id)
    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.CANCEL_CHANGING)
    await state.clear()
