
import logging

from telegram import  Update
from telegram.ext import (
    Application,
)

from handlers import main_conversation_handler, main_menu_handler
from local_setting import TOKEN
from db_config import *
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([('start', 'شروع کار ربات')])


def main() -> None:
    """Run the bot."""
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).post_init(post_init=post_init).build()
    application.add_handler(main_conversation_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
