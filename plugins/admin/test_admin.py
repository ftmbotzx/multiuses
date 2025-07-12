from pyrogram import Client, filters
from pyrogram.types import Message
from .admin_utils import admin_only
from info import Config
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("admintest") & filters.private)
@admin_only
async def admin_test_command(client: Client, message: Message):
    """Test admin functionality"""
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name or "Admin"
        
        if user_id in Config.ADMINS:
            await message.reply_text(
                f"✅ **ᴀᴅᴍɪɴ ᴛᴇsᴛ sᴜᴄᴄᴇssꜰᴜʟ**\n\n"
                f"👋 ʜᴇʟʟᴏ **{user_name}**!\n"
                f"🆔 **ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
                f"🔑 **ᴀᴅᴍɪɴ sᴛᴀᴛᴜs:** ✅ ᴄᴏɴꜰɪʀᴍᴇᴅ\n"
                f"🤖 **ʙᴏᴛ:** @{client.me.username}\n\n"
                f"ᴀʟʟ ᴀᴅᴍɪɴ ꜰᴜɴᴄᴛɪᴏɴs ᴀʀᴇ ᴡᴏʀᴋɪɴɢ ᴘʀᴏᴘᴇʀʟʏ!"
            )
            logger.info(f"Admin test successful for user {user_id}")
        else:
            await message.reply_text("❌ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ")
            
    except Exception as e:
        logger.error(f"Error in admin test: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ɪɴ ᴀᴅᴍɪɴ ᴛᴇsᴛ")