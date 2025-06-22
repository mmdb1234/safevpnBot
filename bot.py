
import asyncio
from telegram.ext import (
    Application,
)


from local_setting import TOKEN
from botManager import RobustTelegramBot

async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([('start', 'شروع کار ربات')])


if __name__ == "__main__":
    botmanegaer = RobustTelegramBot(TOKEN)
    asyncio.run(botmanegaer.start())
