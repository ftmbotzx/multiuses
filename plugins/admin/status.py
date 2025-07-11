from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging
from datetime import datetime

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

@Client.on_message(filters.command("status") & filters.private)
@admin_only
async def bot_status_command(client: Client, message: Message):
    """Handle /status command"""
    try:
        # Get user stats
        stats = await db.get_user_stats()
        
        # Get operations count
        operations_count = await db.operations.count_documents({})
        
        # Get premium codes count
        unused_codes = await db.premium_codes.count_documents({"used": False})
        used_codes = await db.premium_codes.count_documents({"used": True})
        
        status_text = f"""
📊 **ʙᴏᴛ sᴛᴀᴛᴜs**

**ᴜsᴇʀ sᴛᴀᴛs:**
• **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {stats['total_users']}
• **ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs:** {stats['active_users']}
• **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:** {stats['premium_users']}

**ᴏᴘᴇʀᴀᴛɪᴏɴs:**
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {operations_count}

**ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs:**
• **ᴜɴᴜsᴇᴅ ᴄᴏᴅᴇs:** {unused_codes}
• **ᴜsᴇᴅ ᴄᴏᴅᴇs:** {used_codes}

**sʏsᴛᴇᴍ ɪɴꜰᴏ:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs:** {Config.DEFAULT_CREDITS}
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ:** {Config.PROCESS_COST}
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT}
• **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs:** {Config.REFERRAL_BONUS}

**ᴜᴘᴛɪᴍᴇ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        await message.reply_text(status_text)
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ sᴛᴀᴛᴜs.")