from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
import logging, asyncio
from telegram.management.commands.bot import router

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token="7562108093:AAHa6VdcQWx2DYtAn3T8FB7pCWHDScoc5xM")
dp = Dispatcher()

class Command(BaseCommand):
    help = "Запускает Telegram-бота"
    def handle(self, *args, **kwargs):
        async def main():
            dp.include_routers(router)
            await dp.start_polling(bot)

        asyncio.run(main())