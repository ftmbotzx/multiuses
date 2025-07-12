from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_users$"))
@admin_callback_only
async def admin_users_panel(client: Client, callback_query: CallbackQuery):
    """User management panel"""
    try:
            
        # Get user stats
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        banned_users = await db.users.count_documents({"banned": True}) if db.users is not None else 0
        new_users_today = await db.users.count_documents({
            "joined_date": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        }) if db.users is not None else 0
        
        text = f"""
👥 **ᴜsᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**

📊 **sᴛᴀᴛɪsᴛɪᴄs:**
• **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {total_users}
• **ʙᴀɴɴᴇᴅ ᴜsᴇʀs:** {banned_users}
• **ɴᴇᴡ ᴜsᴇʀs ᴛᴏᴅᴀʏ:** {new_users_today}

🔧 **ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴄᴛɪᴏɴs:**
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔍 sᴇᴀʀᴄʜ ᴜsᴇʀ", callback_data="admin_search_user"),
                InlineKeyboardButton("📋 ʀᴇᴄᴇɴᴛ ᴜsᴇʀs", callback_data="admin_recent_users")
            ],
            [
                InlineKeyboardButton("🚫 ʙᴀɴ ᴜsᴇʀ", callback_data="admin_ban_user"),
                InlineKeyboardButton("✅ ᴜɴʙᴀɴ ᴜsᴇʀ", callback_data="admin_unban_user")
            ],
            [
                InlineKeyboardButton("💰 ᴀᴅᴅ ᴄʀᴇᴅɪᴛs", callback_data="admin_add_credits"),
                InlineKeyboardButton("📊 ᴜsᴇʀ sᴛᴀᴛs", callback_data="admin_user_stats")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin users panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)