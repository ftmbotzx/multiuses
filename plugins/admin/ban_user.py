from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging

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

@Client.on_message(filters.command("ban") & filters.private)
@admin_only
async def ban_user_command(client: Client, message: Message):
    """Handle /ban command"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ**\n\n"
                "**ᴜsᴀɢᴇ:** `/ban <user_id>`\n"
                "**ᴇxᴀᴍᴘʟᴇ:** `/ban 123456789`"
            )
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ")
            return
        
        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            return
        
        # Ban user
        await db.ban_user(user_id)
        
        await message.reply_text(
            f"🚫 **ᴜsᴇʀ ʙᴀɴɴᴇᴅ**\n\n"
            f"**ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
            f"**ɴᴀᴍᴇ:** {user.get('first_name', 'Unknown')}"
        )
        
        # Log ban
        if Config.LOG_CHANNEL_ID:
            try:
                log_text = f"🚫 **ᴜsᴇʀ ʙᴀɴɴᴇᴅ**\n\n"
                log_text += f"**ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
                log_text += f"**ɴᴀᴍᴇ:** {user.get('first_name', 'Unknown')}\n"
                log_text += f"**ʙᴀɴɴᴇᴅ ʙʏ:** {message.from_user.id}"
                
                await client.send_message(Config.LOG_CHANNEL_ID, log_text)
            except Exception as e:
                logger.error(f"Failed to log ban: {e}")
        
    except Exception as e:
        logger.error(f"Error in ban command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ.")