from datetime import datetime

from aiogram import Bot
from sqlalchemy import select, null, update

from database.db import db
from database.models import Remind, User, Category, File
from attachements.message import get_remind_text_
from attachements import buttons as btn
from attachements import keyboard as kb


async def send_messages_interval_at_time(bot: Bot):
    curr_time = datetime.now().replace(second=0, microsecond=0)
    reminds = db.sql_query(
        query=select(Remind.id, Remind.name, Remind.text, User.user_id, Remind.date_deadline,
                     Remind.ones_month,
                     Remind.ones_years, Remind.interval).join(
                            User,
                            Remind.user_id == User.id).where(
                            Remind.is_at_time == False).where(
                            Remind.date_finish == null()).where(
                            Remind.date_is_delete == null()).where(
                            Remind.date_last_notificate == curr_time), is_single=False)
    if reminds:
        curr_day = curr_time.day
        curr_year = curr_time.year
        curr_month = curr_time.month
        curr_hours = curr_time.hour
        curr_minute = curr_time.minute
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
                                   reply_markup=kb.get_keyboard(btn.MARKED_AS_READ),
                                   parse_mode="HTML")
            db.sql_query(
                query=update(Remind).where(Remind.id == remind[0]).values(
                    date_last_notificate=curr_time.replace(year=curr_year + remind[6],
                                                           month=(curr_month + remind[5]) % 12,
                                                           day=curr_day,
                                                           minute=curr_minute,
                                                           hour=curr_hours)), is_update=True)


async def send_messages_interval_not_at_time(bot: Bot):
    curr_time = datetime.now().replace(second=0, microsecond=0)
    reminds = db.sql_query(
        query=select(Remind.id, Remind.name, Remind.text, User.user_id, Remind.date_deadline,
                     Remind.ones_month,
                     Remind.ones_years, Remind.interval).join(
                            User,
                            Remind.user_id == User.id).where(
                            Remind.is_at_time == True).where(
                            Remind.date_finish == null()).where(
                            Remind.date_is_delete == null()).where(
                            Remind.date_last_notificate == curr_time), is_single=False)
    if reminds:
        curr_day = curr_time.day
        curr_year = curr_time.year
        curr_month = curr_time.month
        curr_hours = curr_time.hour
        curr_minute = curr_time.minute
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
                                   reply_markup=kb.get_keyboard(btn.MARKED_AS_READ),
                                   parse_mode="HTML")
            db.sql_query(
                query=update(Remind).where(Remind.id == remind[0]).values(
                    date_last_notificate=curr_time.replace(year=curr_year + remind[6],
                                                           month=(curr_month + remind[5]) % 12,
                                                           day=curr_day + remind[7].days,
                                                           minute=curr_minute + (remind[7].seconds % 3600) // 60,
                                                           hour=curr_hours + remind[7].seconds // 3600)), is_update=True)



