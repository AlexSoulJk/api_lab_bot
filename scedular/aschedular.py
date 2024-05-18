from datetime import datetime

from aiogram import Bot
from sqlalchemy import select, null, update

from attachements.clock import Interval
from database.db import db
from database.models import Remind, User, Category, File
from attachements.message import get_remind_text_
from attachements import buttons as btn
from attachements import keyboard as kb
from filters.callback import ShowFilesSCCallBack, MaRCallBack


async def send_messages_interval_at_time(bot: Bot):
    curr_time = datetime.now().replace(second=0, microsecond=0)
    reminds = db.sql_query(
        query=select(Remind.id, Remind.name, Remind.text, User.user_id, Remind.date_deadline,
                     Remind.ones_month,
                     Remind.ones_years, Remind.interval).join(
            User,
            Remind.user_id == User.id).where(
            Remind.date_finish == null()).where(
            Remind.date_is_delete == null()).where(
            Remind.date_last_notificate == curr_time), is_single=False)
    if reminds:
        for remind in reminds:
            btn_file = [(btn.SHOW_FILES_TEXT, ShowFilesSCCallBack(id=remind[0]))]
            categories = db.sql_query(query=select(Category.category_name, Category.id).where(
                Category.remind_id == remind[0]), is_single=False)
            if remind[7] == null():
                await bot.send_message(chat_id=remind[3],
                                       text=get_remind_text_(remind={
                                           "name": remind[1],
                                           "description": remind[2],
                                           'date_last_notificate': remind[4],
                                           "categories": categories,
                                           "interval": None,
                                       }),
                                       reply_markup=kb.get_keyboard(btn.CLOSE_REMIND
                                                                        + btn_file),
                                       parse_mode="HTML")
                db.sql_query(
                    query=update(Remind).where(Remind.id == remind[0]).values(
                        date_finish=curr_time), is_update=True)
            else:
                new_time = curr_time + remind[7]
                new_time = new_time.replace(year=new_time.year + remind[6] + (new_time.month + remind[5]) // 12,
                                            month=(new_time.month + remind[5]) % 12)
                if new_time <= remind[4]:
                    await bot.send_message(chat_id=remind[3],
                                           text=get_remind_text_(remind={
                                               "name": remind[1],
                                               "description": remind[2],
                                               "date_deadline": remind[4],
                                               'date_last_notificate': new_time,
                                               'interval': Interval(days=remind[7].days,
                                                                    hours=remind[7].seconds // 3600,
                                                                    minutes=(remind[7].seconds % 3600) // 60,
                                                                    year=remind[6],
                                                                    month=remind[5]),
                                               "categories": categories
                                           }),
                                           reply_markup=kb.get_keyboard(btn.CLOSE_REMIND
                                                                        + btn_file),
                                           parse_mode="HTML")
                    db.sql_query(
                        query=update(Remind).where(Remind.id == remind[0]).values(
                            date_last_notificate=new_time), is_update=True)
                else:
                    await bot.send_message(chat_id=remind[3],
                                           text=get_remind_text_(remind={
                                               "name": remind[1],
                                               "description": remind[2],
                                               "date_deadline": remind[4],
                                               'date_last_notificate': remind[4],
                                               'interval': Interval(days=remind[7].days,
                                                                    hours=remind[7].seconds // 3600,
                                                                    minutes=(remind[7].seconds % 3600) // 60,
                                                                    year=remind[6],
                                                                    month=remind[5]),
                                               "categories": categories
                                           }),
                                           reply_markup=kb.get_keyboard(btn.CLOSE_REMIND
                                                                        + btn_file),
                                           parse_mode="HTML")
                    db.sql_query(
                        query=update(Remind).where(Remind.id == remind[0]).values(
                            date_finish=remind[4]), is_update=True)
