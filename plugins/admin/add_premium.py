from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging
from datetime import datetime, timedelta

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

@Client.on_message(filters.command("addpremium") & filters.private)
@admin_only
async def add_premium_command(client: Client, message: Message):
    """Handle /addpremium command"""
    try:
        if len(message.command) < 3:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ**\n\n"
                "**ᴜsᴀɢᴇ:** `/addpremium <user_id> <days>`\n"
                "**ᴇxᴀᴍᴘʟᴇ:** `/addpremium 123456789 30`"
            )
            return
        
        try:
            user_id = int(message.command[1])
            days = int(message.command[2])
        except ValueError:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ ᴏʀ ᴅᴀʏs")
            return
        
        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            return
        
        # Add premium time
        success = await db.add_premium_time(user_id, days)
        
        if success:
            await message.reply_text(
                f"💎 **ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ**\n\n"
                f"**ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
                f"**ɴᴀᴍᴇ:** {user.get('first_name', 'Unknown')}\n"
                f"**ᴅᴀʏs ᴀᴅᴅᴇᴅ:** {days}"
            )
            
            # Notify user
            try:
                await client.send_message(
                    user_id,
                    f"🎉 **ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴀᴛᴇᴅ**\n\n"
                    f"ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!\n\n"
                    f"**ᴅᴜʀᴀᴛɪᴏɴ:** {days} ᴅᴀʏs\n"
                    f"**ᴇxᴘɪʀᴇs:** {(datetime.now() + timedelta(days=days)).strftime('%d/%m/%Y')}\n\n"
                    f"ᴇɴᴊᴏʏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssɪɴɢ!"
                )
            except Exception as e:
                logger.error(f"Failed to notify user: {e}")
            
            # Log premium addition
            if Config.LOG_CHANNEL_ID:
                try:
                    log_text = f"💎 **ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ**\n\n"
                    log_text += f"**ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
                    log_text += f"**ɴᴀᴍᴇ:** {user.get('first_name', 'Unknown')}\n"
                    log_text += f"**ᴅᴀʏs:** {days}\n"
                    log_text += f"**ᴀᴅᴅᴇᴅ ʙʏ:** {message.from_user.id}"
                    
                    await client.send_message(Config.LOG_CHANNEL_ID, log_text)
                except Exception as e:
                    logger.error(f"Failed to log premium addition: {e}")
        else:
            await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ")
        
    except Exception as e:
        logger.error(f"Error in addpremium command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴀᴅᴅɪɴɢ ᴘʀᴇᴍɪᴜᴍ.")