import asyncio
import logging
from httpcore import NetworkError
from handlers import main_conversation_handler, main_menu_handler
from telegram.ext import Application
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
import asyncio
import logging
from httpcore import NetworkError
from handlers import main_conversation_handler, main_menu_handler
from telegram.ext import Application
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class RobustTelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = None

    def setup_application(self):
        """تنظیم Application با مدیریت بهتر Connection"""
        request = HTTPXRequest(
            connection_pool_size=4,
            read_timeout=15,
            write_timeout=15,
            connect_timeout=10,
            pool_timeout=5
        )

        self.application = (
            Application.builder()
            .token(self.token)
            .request(request)
            .get_updates_request(request)
            .build()
        )

        self.application.add_handler(main_conversation_handler)

    def start(self):
        """شروع ربات با مدیریت خطا و راه‌اندازی مجدد در صورت نیاز"""
        self.setup_application()
        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            try:
                logger.info(f"📡 Starting bot polling (attempt {retry_count + 1}/{max_retries})")
                self.application.run_polling(
                    allowed_updates=["message", "callback_query"],
                    close_loop=False,  # برای هماهنگی با asyncio.run()
                    drop_pending_updates=True
                )
                logger.info("✅ Bot stopped cleanly.")
                break  # بدون خطا متوقف شده
            except NetworkError as e:
                retry_count += 1
                logger.warning(f"🌐 Network error (retry {retry_count}/{max_retries}): {e}")
                asyncio.sleep(10 * retry_count)  # backoff
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Unexpected error (retry {retry_count}/{max_retries}): {e}")
                asyncio.sleep(30)
        
        if retry_count >= max_retries:
            logger.critical("🛑 Max retries reached, bot giving up.")

    async def stop(self):
        if self.application:
            await self.application.shutdown()
