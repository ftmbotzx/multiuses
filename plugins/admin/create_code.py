from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging
import random
import string

logger = logging.getLogger(__name__)
db = Database()

def admin_only(func):
    """Decorator to restrict commands to admins only"""
    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id not in Config.ADMINS:
            await message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return
        return await func(client, message)
    return wrapper

@Client.on_message(filters.command("createcode") & filters.private)
@admin_only
async def create_premium_code_command(client: Client, message: Message):
    """Handle /createcode command"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ**\n\n"
                "**ᴜsᴀɢᴇ:** `/createcode <days>`\n"
                "**ᴇxᴀᴍᴘʟᴇ:** `/createcode 30`"
            )
            return
        
        try:
            days = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴅᴀʏs")
            return
        
        # Generate random code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Create code in database
        await db.create_premium_code(code, days, message.from_user.id)
        
        await message.reply_text(
            f"🎫 **ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ ᴄʀᴇᴀᴛᴇᴅ**\n\n"
            f"**ᴄᴏᴅᴇ:** `{code}`\n"
            f"**ᴅᴀʏs:** {days}\n"
            f"**ᴄʀᴇᴀᴛᴇᴅ ʙʏ:** {message.from_user.id}\n\n"
            f"ᴜsᴇʀs ᴄᴀɴ ʀᴇᴅᴇᴇᴍ ᴛʜɪs ᴄᴏᴅᴇ ᴜsɪɴɢ `/redeem {code}`"
        )
        
        # Log code creation
        if Config.LOG_CHANNEL_ID:
            try:
                log_text = f"🎫 **ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ ᴄʀᴇᴀᴛᴇᴅ**\n\n"
                log_text += f"**ᴄᴏᴅᴇ:** `{code}`\n"
                log_text += f"**ᴅᴀʏs:** {days}\n"
                log_text += f"**ᴄʀᴇᴀᴛᴇᴅ ʙʏ:** {message.from_user.id}"
                
                await client.send_message(Config.LOG_CHANNEL_ID, log_text)
            except Exception as e:
                logger.error(f"Failed to log code creation: {e}")
        
    except Exception as e:
        logger.error(f"Error in createcode command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴄʀᴇᴀᴛɪɴɢ ᴄᴏᴅᴇ.")