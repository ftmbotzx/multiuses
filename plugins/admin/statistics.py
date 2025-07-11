from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_stats$"))
async def admin_stats_panel(client: Client, callback_query: CallbackQuery):
    """Statistics panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Get comprehensive stats
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        active_users = await db.users.count_documents({
            "last_activity": {"$gte": datetime.now() - timedelta(days=7)}
        }) if db.users is not None else 0
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        banned_users = await db.users.count_documents({"banned": True}) if db.users is not None else 0
        
        total_operations = await db.operations.count_documents({}) if db.operations is not None else 0
        today_operations = await db.operations.count_documents({
            "date": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        }) if db.operations is not None else 0
        
        unused_codes = await db.premium_codes.count_documents({"used": False}) if db.premium_codes is not None else 0
        used_codes = await db.premium_codes.count_documents({"used": True}) if db.premium_codes is not None else 0
        
        new_users_today = await db.users.count_documents({
            "joined_date": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        }) if db.users is not None else 0
        
        text = f"""
📊 **ᴅᴇᴛᴀɪʟᴇᴅ sᴛᴀᴛɪsᴛɪᴄs**

👥 **ᴜsᴇʀs:**
• **ᴛᴏᴛᴀʟ:** {total_users}
• **ᴀᴄᴛɪᴠᴇ (7ᴅ):** {active_users}
• **ᴘʀᴇᴍɪᴜᴍ:** {premium_users}
• **ʙᴀɴɴᴇᴅ:** {banned_users}
• **ɴᴇᴡ ᴛᴏᴅᴀʏ:** {new_users_today}

⚡ **ᴏᴘᴇʀᴀᴛɪᴏɴs:**
• **ᴛᴏᴛᴀʟ:** {total_operations}
• **ᴛᴏᴅᴀʏ:** {today_operations}

🎫 **ᴄᴏᴅᴇs:**
• **ᴜɴᴜsᴇᴅ:** {unused_codes}
• **ᴜsᴇᴅ:** {used_codes}

⚙️ **sʏsᴛᴇᴍ:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs:** {Config.DEFAULT_CREDITS}
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ:** {Config.PROCESS_COST}
• **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs:** {Config.REFERRAL_BONUS}
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT}

📅 **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📈 ᴛʀᴇɴᴅs", callback_data="admin_trends"),
                InlineKeyboardButton("🔍 ᴅᴇᴛᴀɪʟs", callback_data="admin_detailed_stats")
            ],
            [
                InlineKeyboardButton("📊 ᴏᴘᴇʀᴀᴛɪᴏɴs", callback_data="admin_operation_stats"),
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="admin_premium_stats")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="admin_stats"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin stats panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)