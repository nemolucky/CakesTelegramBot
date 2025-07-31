import os
import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.handlers import router
from app.db.models import get_db
from app.call_handlers import call_router


async def main():
    await get_db()

    load_dotenv()
    bot = Bot(token=os.getenv("TOKEN"))

    dp = Dispatcher()
    dp.include_routers(router, call_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print('Exit', ex)
