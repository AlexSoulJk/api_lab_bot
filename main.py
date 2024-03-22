import logging
import os

import aiogram
import asyncio

from dotenv import load_dotenv
from handlers import Any, welcom, info, addremind, calendary_ex, checkremindlist, change, remove_remind, urgently_finish
load_dotenv()
tg_token = os.getenv("TG_TOKEN")

bot = aiogram.Bot(token=tg_token)
dp = aiogram.Dispatcher()


# Auth branches of the scenario
dp.include_routers(welcom.router, addremind.router, checkremindlist.router, change.router, urgently_finish.router,
                   remove_remind.router, info.router, calendary_ex.router, Any.router)
# UI branches of the scenario
#dp.include_routers()



async def main():
    try:
        # db.connect()
        await asyncio.wait([asyncio.create_task(dp.start_polling(bot))], return_when=asyncio.FIRST_COMPLETED)
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    asyncio.run(main())
