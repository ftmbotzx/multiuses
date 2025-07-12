from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_only, admin_callback_only
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
db = Database()

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
@admin_callback_only
async def admin_panel_refresh(client: Client, callback_query: CallbackQuery):
    """Refresh admin panel"""
    # Create a mock message object for admin_panel function
    class MockMessage:
        def __init__(self, callback_query):
            self.from_user = callback_query.from_user
            self.chat = callback_query.message.chat
        
        async def reply_text(self, text, reply_markup=None):
            return await callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    mock_message = MockMessage(callback_query)
    await admin_panel(client, mock_message)

# Add missing callback handlers
@Client.on_callback_query(filters.regex("^admin_codes$"))
@admin_callback_only
async def admin_codes_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin codes callback"""
    try:
        # Redirect to premium management
        from .premium_management import admin_premium_panel
        await admin_premium_panel(client, callback_query)
    except Exception as e:
        logger.error(f"Error in admin codes callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_security$"))
@admin_callback_only
async def admin_security_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin security callback"""
    try:
        text = """
🔐 **sᴇᴄᴜʀɪᴛʏ sᴇᴛᴛɪɴɢs**

**ᴀᴅᴍɪɴ ᴄᴏɴᴛʀᴏʟs:**
• **ᴀᴅᴍɪɴs:** {len(Config.ADMINS)}
• **ᴏᴡɴᴇʀ:** {Config.OWNER_ID}

**sᴇᴄᴜʀɪᴛʏ ғᴇᴀᴛᴜʀᴇs:**
• ᴀᴅᴍɪɴ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ ᴄʜᴇᴄᴋs
• ᴜsᴇʀ ʙᴀɴ sʏsᴛᴇᴍ
• ʀᴀᴛᴇ ʟɪᴍɪᴛɪɴɢ
• ᴄʀᴇᴅɪᴛ sʏsᴛᴇᴍ

**ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴀᴅᴍɪɴs:**
"""
        for admin_id in Config.ADMINS:
            text += f"• `{admin_id}`\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin security callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)