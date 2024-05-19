import logging
import os

import aiogram
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scedular import aschedular as sc
from dotenv import load_dotenv
from handlers import Any, welcom, info, addremind, calendary_ex, \
    checkremindlist, change, remove_remind, urgently_finish, scedular_reminds, files_h
from handlers import timepicker
load_dotenv()
tg_token = os.getenv("TG_TOKEN")

bot = aiogram.Bot(token=tg_token)
dp = aiogram.Dispatcher()


# Auth branches of the scenario
dp.include_routers(welcom.router, addremind.router, checkremindlist.router, files_h.router, change.router, urgently_finish.router,
                   remove_remind.router, info.router, calendary_ex.router, timepicker.router,
                   scedular_reminds.router, Any.router)
# UI branches of the scenario
#dp.include_routers()

commands = [
    {"command": "name", "description": "Изменить имя"},
    {"command": "add", "description": "Добавить напоминание"},
    {"command": "check", "description": "Просмотреть список напоминаний"},
    {"command": "check_daily", "description": "Просмотреть список напоминаний на этот день"},
    {"command": "check_ended", "description": "Просмотреть список, недавно завершённых, напоминаний"},
]
async def main():

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(sc.send_messages_interval_at_time, trigger="interval",
                      seconds=60, kwargs={"bot": bot})
    scheduler.start()
    # Устанавливаем команды для бота
    await bot.set_my_commands(commands)
    try:
        # db.connect()
        await asyncio.wait([asyncio.create_task(dp.start_polling(bot))], return_when=asyncio.FIRST_COMPLETED)
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    asyncio.run(main())
