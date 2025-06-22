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
class RobustTelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = None
        self.is_running = False
        self.setup_application()
    
    def setup_application(self):
        """تنظیم Application با مدیریت بهتر Connection"""
        from telegram.request import HTTPXRequest
        
        # تنظیمات محافظانه
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
    
    async def cleanup(self):
        """پاک‌سازی منابع"""
        try:
            if self.application and self.application.updater:
                await self.application.updater.stop()
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def restart_on_error(self):
        """راه‌اندازی مجدد در صورت خطا"""
        logger.info("Restarting bot...")
        await self.cleanup()
        await asyncio.sleep(5)
        self.setup_application()
        
    async def start(self):
        """شروع ربات با مدیریت خطا"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Starting bot (attempt {retry_count + 1}/{max_retries})")
                
                # Initialize application
                await self.application.initialize()
                await self.application.start()
                self.application.add_handler(main_conversation_handler)
                # Check if updater exists
                if not hasattr(self.application, 'updater') or self.application.updater is None:
                    logger.error("Application updater is None")
                    raise Exception("Updater not available")
                
                # Start polling
                await self.application.updater.start_polling(
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query"]
                )
                
                logger.info("Bot started successfully!")
                self.is_running = True
                retry_count = 0
                
                # Keep the bot running
                try:
                    while self.is_running:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Received KeyboardInterrupt, stopping bot...")
                    self.is_running = False
                    break
                
            except NetworkError as e:
                retry_count += 1
                logger.error(f"Network error (retry {retry_count}/{max_retries}): {e}")
                
                if retry_count >= max_retries:
                    logger.critical("Max retries reached, stopping bot")
                    break
                
                await asyncio.sleep(10 * retry_count)  # تاخیر تصاعدی
                await self.restart_on_error()
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                retry_count += 1
                
                if retry_count >= max_retries:
                    logger.critical("Max retries reached, stopping bot")
                    break
                    
                await asyncio.sleep(30)
                await self.restart_on_error()
        
        # Final cleanup
        await self.cleanup()
    
    async def stop(self):
        """توقف ربات"""
        logger.info("Stopping bot...")
        self.is_running = False
        await self.cleanup()