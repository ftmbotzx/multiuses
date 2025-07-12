from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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

@Client.on_message(filters.command("admin") & filters.private)
@admin_only
async def admin_panel(client: Client, message: Message):
    """Main admin panel"""
    try:
        # Get quick stats
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        active_users = await db.users.count_documents({"last_activity": {"$gte": datetime.now() - timedelta(days=7)}}) if db.users is not None else 0
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        total_operations = await db.operations.count_documents({}) if db.operations is not None else 0
        
        panel_text = f"""
🔧 **ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ**

📊 **Qᴜɪᴄᴋ Sᴛᴀᴛs:**
• **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {total_users}
• **ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs:** {active_users}
• **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:** {premium_users}
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {total_operations}

🔑 **ᴀᴅᴍɪɴ ID:** {message.from_user.id}
⏰ **ᴛɪᴍᴇ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 ᴜsᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="admin_users"),
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="admin_premium")
            ],
            [
                InlineKeyboardButton("📊 sᴛᴀᴛɪsᴛɪᴄs", callback_data="admin_stats"),
                InlineKeyboardButton("📋 ʟᴏɢs", callback_data="admin_logs")
            ],
            [
                InlineKeyboardButton("📢 ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin_broadcast"),
                InlineKeyboardButton("🎫 ᴄᴏᴅᴇs", callback_data="admin_codes")
            ],
            [
                InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="admin_settings"),
                InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="admin_refresh")
            ],
            [
                InlineKeyboardButton("💾 ʙᴀᴄᴋᴜᴘ", callback_data="admin_backup"),
                InlineKeyboardButton("🔐 sᴇᴄᴜʀɪᴛʏ", callback_data="admin_security")
            ]
        ])
        
        await message.reply_text(panel_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ.")

@Client.on_callback_query(filters.regex("^admin_main$|^admin_refresh$"))
async def admin_panel_refresh(client: Client, callback_query: CallbackQuery):
    """Refresh admin panel"""
    await admin_panel(client, callback_query.message)