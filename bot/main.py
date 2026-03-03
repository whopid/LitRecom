import asyncio
from aiogram import Bot, Dispatcher

from env import BOT_TOKEN
from bot.handlers import start, recommend, feedback


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(recommend.router)
    dp.include_router(feedback.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
