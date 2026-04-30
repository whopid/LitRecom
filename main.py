import asyncio
from aiogram import Bot, Dispatcher

from env import BOT_TOKEN
from bot.handlers import start, recommend, feedback, questionnaire, random_book, request_title, search, settings, \
    username, reset_feedbacks


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(recommend.router)
    dp.include_router(feedback.router)
    dp.include_router(questionnaire.router)
    dp.include_router(random_book.router)
    dp.include_router(request_title.router)
    dp.include_router(search.router)
    dp.include_router(settings.router)
    dp.include_router(username.router)
    dp.include_router(reset_feedbacks.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
