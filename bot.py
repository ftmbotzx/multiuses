import asyncio
import logging
import os
import pytz
from datetime import datetime, date

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from info import Config
from database.db import Database
from plugins import web_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 8080))

class TelegramBot(Client):
    def __init__(self):
        super().__init__(
            name=Config.SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=1000,
            sleep_threshold=10,
            max_concurrent_transmissions=6,
            plugins={"root": "plugins"}
        )
        self.db = Database()
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        await super().start()
        me = await self.get_me()
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)

        logger.info(f"🤖 {me.first_name} (@{me.username}) running on Pyrogram v{__version__} (Layer {layer})")

        # Send log startup message
        if Config.LOG_CHANNEL:
            try:
                await self.send_message(
                    chat_id=Config.LOG_CHANNEL,
                    text=f"✅ Bot Restarted!\n📅 {date.today()} 🕒 {now.strftime('%I:%M:%S %p')}"
                )
                logger.info("Startup message sent to log channel")
            except Exception as e:
                logger.warning(f"Failed to send startup message to log channel: {e}")

        # Connect DB
        await self.db.connect()

        # Broadcast startup to all users
        await self._send_startup_broadcast()

        # Start web server (Render/Heroku compatibility)
        try:
            app = await web_server()
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", PORT)
            await site.start()
            logger.info(f"🌐 Web Server Running on 0.0.0.0:{PORT}")
            
            # Small delay to ensure server is fully up
            await asyncio.sleep(1)
            
            # Test server accessibility
            import aiohttp
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"http://localhost:{PORT}/health") as resp:
                        if resp.status == 200:
                            logger.info("✅ Web server health check passed")
                        else:
                            logger.warning(f"⚠️ Web server health check failed: {resp.status}")
                except Exception as e:
                    logger.error(f"❌ Web server health check error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            # Continue without web server if it fails
            pass

        # Start scheduler
        self.scheduler.start()

    async def stop(self, *args):
        await self.db.close()
        await super().stop()
        logger.info("🛑 Bot Stopped")

    async def _send_startup_broadcast(self):
        try:
            if not self.db._connected:
                await self.db.connect()

            users_cursor = self.db.users.find({}, {"_id": 1})
            user_count = 0
            success_count = 0
            msg = (
                "🚀 **ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴏʀ ʙᴏᴛ ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ!**\n\n"
                "✅ **ʟᴀᴛᴇsᴛ ᴜᴘᴅᴀᴛᴇs:**\n"
                "• 🔧 ꜰɪxᴇᴅ ᴄᴜsᴛᴏᴍ ᴛʀɪᴍ ᴛɪᴍᴇ ɪɴᴘᴜᴛ\n"
                "• 💧 ꜰɪxᴇᴅ ᴄᴜsᴛᴏᴍ ᴡᴀᴛᴇʀᴍᴀʀᴋ ꜰᴇᴀᴛᴜʀᴇs\n"
                "• 🎵 sɪᴍᴘʟɪꜰɪᴇᴅ ʀᴇᴘʟᴀᴄᴇ ᴀᴜᴅɪᴏ ᴡᴏʀᴋꜰʟᴏᴡ\n"
                "• ⚡ ɪᴍᴘʀᴏᴠᴇᴅ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ & sᴛᴀʙɪʟɪᴛʏ\n\n"
                "📋 **ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴇᴀᴛᴜʀᴇs:**\n"
                "• ✂️ ᴛʀɪᴍ ᴠɪᴅᴇᴏ (ɪɴᴄʟ. ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇ)\n"
                "• 🗜️ ᴄᴏᴍᴘʀᴇss & 🔄 ʀᴏᴛᴀᴛᴇ\n"
                "• 💧 ᴡᴀᴛᴇʀᴍᴀʀᴋ (ᴛᴇxᴛ & ɪᴍᴀɢᴇ)\n"
                "• 📸 sᴄʀᴇᴇɴsʜᴏᴛ & 🎵 ᴀᴜᴅɪᴏ ᴇxᴛʀᴀᴄᴛ\n"
                "• 📏 ᴄʜᴀɴɢᴇ ʀᴇsᴏʟᴜᴛɪᴏɴ\n"
                "• 🔗 ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏs & 📝 sᴜʙᴛɪᴛʟᴇs\n\n"
                "🎯 Send a video to get started!\n\n**Powered by Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ**"
            )

            async for user_doc in users_cursor:
                user_count += 1
                try:
                    await self.send_message(user_doc["_id"], msg)
                    success_count += 1
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.debug(f"Failed to send to {user_doc['_id']}: {e}")

            logger.info(f"✅ Broadcast done: {success_count}/{user_count} users")

        except Exception as e:
            logger.error(f"Broadcast failed: {e}")

# Run the bot
if __name__ == "__main__":
    app = TelegramBot()
    app.run()