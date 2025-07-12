from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_settings$"))
@admin_callback_only
async def admin_settings_panel(client: Client, callback_query: CallbackQuery):
    """Settings panel"""
    try:
            
        text = f"""
⚙️ **sʏsᴛᴇᴍ sᴇᴛᴛɪɴɢs**

**ᴄᴜʀʀᴇɴᴛ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs:** {Config.DEFAULT_CREDITS}
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ:** {Config.PROCESS_COST}
• **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs:** {Config.REFERRAL_BONUS}
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT}

**ᴀᴅᴍɪɴs:** {len(Config.ADMINS)}
**ᴏᴡɴᴇʀ:** {Config.OWNER_ID}

**ꜰɪʟᴇ ᴅɪʀᴇᴄᴛᴏʀɪᴇs:**
• **ᴅᴏᴡɴʟᴏᴀᴅs:** {Config.DOWNLOADS_DIR}
• **ᴜᴘʟᴏᴀᴅs:** {Config.UPLOADS_DIR}
• **ᴛᴇᴍᴘ:** {Config.TEMP_DIR}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 ᴄʀᴇᴅɪᴛ sᴇᴛᴛɪɴɢs", callback_data="admin_credit_settings"),
                InlineKeyboardButton("🔧 sʏsᴛᴇᴍ ɪɴꜰᴏ", callback_data="admin_system_info")
            ],
            [
                InlineKeyboardButton("🧹 ᴄʟᴇᴀɴᴜᴘ", callback_data="admin_cleanup"),
                InlineKeyboardButton("📁 ꜰɪʟᴇs", callback_data="admin_file_manager")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ", callback_data="admin_restart"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin settings panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)