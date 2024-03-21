import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.settings import settings
from app.utils.commands import set_commands
from app.handlers.handlers import router


async def start_bot(bot: Bot):
    await set_commands(bot)


async def main():
    bot = Bot(settings.bots.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход из бота!')
