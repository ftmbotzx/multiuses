from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_broadcast$"))
async def admin_broadcast_panel(client: Client, callback_query: CallbackQuery):
    """Broadcast panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        text = f"""
📢 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**

ᴄʀᴇᴀᴛᴇ ᴀɴᴅ sᴇɴᴅ ᴍᴇssᴀɢᴇs ᴛᴏ ᴀʟʟ ᴜsᴇʀs.

**ɪɴsᴛʀᴜᴄᴛɪᴏɴs:**
• ᴛʏᴘᴇ `/broadcast <message>` ᴛᴏ sᴇɴᴅ ᴛᴏ ᴀʟʟ ᴜsᴇʀs
• ᴜsᴇ ᴍᴀʀᴋᴅᴏᴡɴ ꜰᴏʀᴍᴀᴛᴛɪɴɢ
• ᴍᴇssᴀɢᴇs ᴀʀᴇ sᴇɴᴛ ᴡɪᴛʜ ʀᴀᴛᴇ ʟɪᴍɪᴛɪɴɢ

⚠️ **ᴡᴀʀɴɪɴɢ:** ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇs ᴀʀᴇ sᴇɴᴛ ᴛᴏ ᴀʟʟ ᴜsᴇʀs!
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📝 ᴄʀᴇᴀᴛᴇ ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin_create_broadcast"),
                InlineKeyboardButton("📊 ᴜsᴇʀ ᴄᴏᴜɴᴛ", callback_data="admin_user_count")
            ],
            [
                InlineKeyboardButton("📈 ᴀᴄᴛɪᴠᴇ ᴏɴʟʏ", callback_data="admin_broadcast_active"),
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴏɴʟʏ", callback_data="admin_broadcast_premium")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin broadcast panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)