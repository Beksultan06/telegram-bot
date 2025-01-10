from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
import logging, asyncio
from telegram.management.commands.bot import router as business_router
from telegram.management.commands.client import router as client_router

logging.basicConfig(level=logging.DEBUG)

bot_business = Bot(token="7562108093:AAHa6VdcQWx2DYtAn3T8FB7pCWHDScoc5xM")
bot_client = Bot(token="7209363206:AAE0ol7YE8cWrNnx2L-nJCLz_nBl3RaeQtU")
dp_business = Dispatcher()
dp_client = Dispatcher()

class Command(BaseCommand):
    help = "Запускает Telegram-ботов"

    def handle(self, *args, **kwargs):
        async def main():
            dp_business.include_router(business_router)
            dp_client.include_router(client_router)

            await asyncio.gather(
                dp_business.start_polling(bot_business),
                dp_client.start_polling(bot_client),
            )

        asyncio.run(main())
