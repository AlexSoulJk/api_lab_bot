from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import WellCome
from aiogram import Router, Bot, F
from attachements import message as msg
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from database.db import db
from database.models import User
import datetime

router = Router()


@router.message(Command(commands="start"))
async def start_using(message: Message, state: FSMContext):
    await message.answer(msg.WELCOME_MSG)
    await state.set_state(WellCome.start)


@router.message(WellCome.start)
async def get_name(message: Message, state: FSMContext):
    db.create_object(User(name=message.text, date_start=datetime.date.today(), user_id=message.from_user.id))
    await message.answer(text=msg.REMEMBER_YOU + message.text)
    await state.clear()
