from pyrogram import Client, filters
from pyrogram.types import Message
from info import Config
from .admin_utils import admin_only
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("admintest") & filters.private)
@admin_only
async def admin_test_command(client: Client, message: Message):
    """Test command to verify admin access"""
    try:
        user_id = message.from_user.id
        admin_list = ', '.join(map(str, Config.ADMINS))
        
        text = f"""
🔧 **ᴀᴅᴍɪɴ ᴛᴇsᴛ sᴜᴄᴄᴇssꜰᴜʟ!**

**ʏᴏᴜʀ ɪᴅ:** `{user_id}`
**ᴀᴅᴍɪɴ ʟɪsᴛ:** `{admin_list}`

✅ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ᴀᴄᴄᴇss!
ᴀʟʟ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs sʜᴏᴜʟᴅ ᴡᴏʀᴋ ɴᴏᴡ.

**ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**
• `/admin` - Main admin panel
• `/searchuser <id>` - Search user
• `/ban <id>` - Ban user
• `/unban <id>` - Unban user
• `/status` - Bot status
• `/logs` - View logs
• `/broadcast` - Send broadcast
"""
        
        await message.reply_text(text)
        
    except Exception as e:
        logger.error(f"Error in admin test: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ɪɴ ᴀᴅᴍɪɴ ᴛᴇsᴛ")