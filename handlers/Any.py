from datetime import datetime

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, null

from attachements.message import get_remind_text_
from database.db import db
from database.models import Remind, User, Category
from attachements import buttons as btn
from attachements import keyboard as kb

router = Router()

@router.message(Command("test"))
async def test(message: Message, bot: Bot):
    curr_time = datetime.now().replace(second=0, microsecond=0)
    print(curr_time)
    reminds = db.sql_query(
        query=select(Remind.id, Remind.name, Remind.text, User.user_id, Remind.date_deadline).join(User,
                                                                                                   Remind.user_id == User.id).where(
            Remind.is_at_time == False).where(
            Remind.date_finish == null()).where(
            Remind.date_is_delete == null()), is_single=False)
    print(reminds)
    if reminds:

        for remind in reminds:
            categories = db.sql_query(query=select(Category.category_name, Category.id).where(
                Category.remind_id == remind[0]), is_single=False)

            await bot.send_message(chat_id=remind[3],
                                   text=get_remind_text_(remind={
                                       "name": remind[1],
                                       "description": remind[2],
                                       "date_deadline": remind[4],
                                       "categories": categories
                                   }),
                                   reply_markup=kb.get_keyboard(btn.MARKED_AS_READ))

@router.message()
async def any_types(message: Message):
    await message.answer('You are durila')
