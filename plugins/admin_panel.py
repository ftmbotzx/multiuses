from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from db import Database
from config import Config
import logging
import asyncio
from datetime import datetime, timedelta
import json
import os

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
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
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

@Client.on_callback_query(filters.regex("^admin_users$"))
async def admin_users_panel(client: Client, callback_query: CallbackQuery):
    """User management panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
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

@Client.on_callback_query(filters.regex("^admin_premium$"))
async def admin_premium_panel(client: Client, callback_query: CallbackQuery):
    """Premium management panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Get premium stats
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        expired_premium = await db.users.count_documents({
            "premium_until": {"$lt": datetime.now(), "$ne": None}
        }) if db.users is not None else 0
        
        text = f"""
💎 **ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**

📊 **sᴛᴀᴛɪsᴛɪᴄs:**
• **ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ:** {premium_users}
• **ᴇxᴘɪʀᴇᴅ ᴘʀᴇᴍɪᴜᴍ:** {expired_premium}

💰 **ᴘʀɪᴄɪɴɢ:**
• **ᴍᴏɴᴛʜʟʏ:** {Config.PREMIUM_PRICES['monthly']['credits']} ᴄʀᴇᴅɪᴛs ({Config.PREMIUM_PRICES['monthly']['days']} ᴅᴀʏs)
• **ʏᴇᴀʀʟʏ:** {Config.PREMIUM_PRICES['yearly']['credits']} ᴄʀᴇᴅɪᴛs ({Config.PREMIUM_PRICES['yearly']['days']} ᴅᴀʏs)
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ", callback_data="admin_add_premium"),
                InlineKeyboardButton("🎫 ᴄʀᴇᴀᴛᴇ ᴄᴏᴅᴇ", callback_data="admin_create_code")
            ],
            [
                InlineKeyboardButton("📋 ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs", callback_data="admin_premium_users"),
                InlineKeyboardButton("🎟️ ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇs", callback_data="admin_active_codes")
            ],
            [
                InlineKeyboardButton("⏰ ᴇxᴘɪʀɪɴɢ sᴏᴏɴ", callback_data="admin_expiring_premium"),
                InlineKeyboardButton("📊 ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛs", callback_data="admin_premium_stats")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin premium panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_stats$"))
async def admin_stats_panel(client: Client, callback_query: CallbackQuery):
    """Statistics panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
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

# Add missing callback handlers
@Client.on_callback_query(filters.regex("^admin_main$"))
async def admin_main_callback(client: Client, callback_query: CallbackQuery):
    """Return to admin main panel"""
    await admin_panel(client, callback_query.message)

@Client.on_callback_query(filters.regex("^admin_refresh$"))
async def admin_refresh_callback(client: Client, callback_query: CallbackQuery):
    """Refresh admin panel"""
    await admin_panel(client, callback_query.message)

@Client.on_callback_query(filters.regex("^admin_search_user$"))
async def admin_search_user_callback(client: Client, callback_query: CallbackQuery):
    """Search user callback"""
    await callback_query.answer("💡 Use /userinfo <user_id> command to search user", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_ban_user$"))
async def admin_ban_user_callback(client: Client, callback_query: CallbackQuery):
    """Ban user callback"""
    await callback_query.answer("💡 Use /ban <user_id> command to ban user", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_unban_user$"))
async def admin_unban_user_callback(client: Client, callback_query: CallbackQuery):
    """Unban user callback"""
    await callback_query.answer("💡 Use /unban <user_id> command to unban user", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_credits$"))
async def admin_add_credits_callback(client: Client, callback_query: CallbackQuery):
    """Add credits callback"""
    await callback_query.answer("💡 Use /addcredits <user_id> <amount> command", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_broadcast$"))
async def admin_broadcast_callback(client: Client, callback_query: CallbackQuery):
    """Broadcast callback"""
    await callback_query.answer("💡 Use /broadcast <message> command", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_"))
async def admin_generic_callback(client: Client, callback_query: CallbackQuery):
    """Handle other admin callbacks"""
    action = callback_query.data.replace("admin_", "")
    await callback_query.answer(f"ℹ️ {action.replace('_', ' ').title()} feature coming soon!", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_logs$"))
async def admin_logs_panel(client: Client, callback_query: CallbackQuery):
    """Logs panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Get recent operations
        recent_ops = await db.operations.find({}).sort("date", -1).limit(10).to_list(None) if db.operations is not None else []
        
        text = "📋 **ʀᴇᴄᴇɴᴛ ᴀᴄᴛɪᴠɪᴛʏ**\n\n"
        
        if recent_ops:
            for i, op in enumerate(recent_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                status = op.get("status", "Unknown")
                date = op.get("date", datetime.now())
                
                status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                
                text += f"`{i}.` {status_emoji} **{operation_type}** - ᴜsᴇʀ: `{user_id}`\n"
                text += f"    📅 {date.strftime('%d/%m %H:%M')}\n\n"
        else:
            text += "ɴᴏ ʀᴇᴄᴇɴᴛ ᴀᴄᴛɪᴠɪᴛʏ ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 ꜰᴜʟʟ ʟᴏɢs", callback_data="admin_full_logs"),
                InlineKeyboardButton("🔍 ꜰɪʟᴛᴇʀ", callback_data="admin_filter_logs")
            ],
            [
                InlineKeyboardButton("❌ ᴇʀʀᴏʀs", callback_data="admin_error_logs"),
                InlineKeyboardButton("✅ sᴜᴄᴄᴇss", callback_data="admin_success_logs")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="admin_logs"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin logs panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

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

@Client.on_callback_query(filters.regex("^admin_settings$"))
async def admin_settings_panel(client: Client, callback_query: CallbackQuery):
    """Settings panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
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

@Client.on_callback_query(filters.regex("^admin_backup$"))
async def admin_backup_panel(client: Client, callback_query: CallbackQuery):
    """Backup panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        text = f"""
💾 **ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ**

ᴄʀᴇᴀᴛᴇ ᴀɴᴅ ᴍᴀɴᴀɢᴇ ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘs.

**ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:**
• ʙᴀᴄᴋᴜᴘs ɪɴᴄʟᴜᴅᴇ ᴀʟʟ ᴜsᴇʀ ᴅᴀᴛᴀ
• ᴏᴘᴇʀᴀᴛɪᴏɴ ʜɪsᴛᴏʀʏ ɪs ɪɴᴄʟᴜᴅᴇᴅ
• ꜰɪʟᴇs ᴀʀᴇ ɴᴏᴛ ʙᴀᴄᴋᴇᴅ ᴜᴘ
• ʙᴀᴄᴋᴜᴘs ᴀʀᴇ ɪɴ ᴊsᴏɴ ꜰᴏʀᴍᴀᴛ

⏰ **ʟᴀsᴛ ᴜᴘᴅᴀᴛᴇ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📥 ᴄʀᴇᴀᴛᴇ ʙᴀᴄᴋᴜᴘ", callback_data="admin_create_backup"),
                InlineKeyboardButton("📊 ʙᴀᴄᴋᴜᴘ ɪɴꜰᴏ", callback_data="admin_backup_info")
            ],
            [
                InlineKeyboardButton("🔄 ᴀᴜᴛᴏ ʙᴀᴄᴋᴜᴘ", callback_data="admin_auto_backup"),
                InlineKeyboardButton("📋 ᴇxᴘᴏʀᴛ ᴜsᴇʀs", callback_data="admin_export_users")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin backup panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_refresh$|^admin_main$"))
async def admin_refresh(client: Client, callback_query: CallbackQuery):
    """Refresh admin panel"""
    await admin_panel(client, callback_query.message)

# Add more callback handlers for specific actions...
@Client.on_callback_query(filters.regex("^admin_create_backup$"))
async def admin_create_backup(client: Client, callback_query: CallbackQuery):
    """Create database backup"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        await callback_query.answer("🔄 ᴄʀᴇᴀᴛɪɴɢ ʙᴀᴄᴋᴜᴘ...")
        
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Create backup
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "users": [],
            "operations": [],
            "premium_codes": []
        }
        
        # Export users
        users = await db.users.find({}).to_list(None) if db.users is not None else []
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            backup_data["users"].append(user)
        
        # Export operations (last 1000)
        operations = await db.operations.find({}).sort("date", -1).limit(1000).to_list(None) if db.operations is not None else []
        for op in operations:
            op['_id'] = str(op['_id'])
            backup_data["operations"].append(op)
        
        # Export premium codes
        codes = await db.premium_codes.find({}).to_list(None) if db.premium_codes is not None else []
        for code in codes:
            code['_id'] = str(code['_id'])
            backup_data["premium_codes"].append(code)
        
        # Save backup file
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(Config.TEMP_DIR, backup_filename)
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        # Send backup file
        await client.send_document(
            callback_query.from_user.id,
            backup_path,
            caption=f"💾 **ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ**\n\n"
                   f"**ᴜsᴇʀs:** {len(backup_data['users'])}\n"
                   f"**ᴏᴘᴇʀᴀᴛɪᴏɴs:** {len(backup_data['operations'])}\n"
                   f"**ᴄᴏᴅᴇs:** {len(backup_data['premium_codes'])}\n"
                   f"**ᴄʀᴇᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        # Clean up
        os.remove(backup_path)
        
        await callback_query.answer("✅ ʙᴀᴄᴋᴜᴘ ᴄʀᴇᴀᴛᴇᴅ!")
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        await callback_query.answer("❌ ʙᴀᴄᴋᴜᴘ ꜰᴀɪʟᴇᴅ", show_alert=True)

# Add all missing admin callback handlers
@Client.on_callback_query(filters.regex("^admin_search_user$"))
async def admin_search_user(client: Client, callback_query: CallbackQuery):
    """Search user"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        await callback_query.edit_message_text(
            "🔍 **sᴇᴀʀᴄʜ ᴜsᴇʀ**\n\n"
            "sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴏʀ ᴜsᴇʀɴᴀᴍᴇ ᴛᴏ sᴇᴀʀᴄʜ:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in search user: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_recent_users$"))
async def admin_recent_users(client: Client, callback_query: CallbackQuery):
    """Show recent users"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Get recent users
        recent_users = await db.users.find({}).sort("joined_date", -1).limit(10).to_list(None) if db.users is not None else []
        
        text = "📋 **ʀᴇᴄᴇɴᴛ ᴜsᴇʀs**\n\n"
        
        if recent_users:
            for i, user in enumerate(recent_users, 1):
                user_id = user.get("user_id", "Unknown")
                username = user.get("username", "No username")
                credits = user.get("credits", 0)
                joined = user.get("joined_date", "Unknown")
                
                text += f"{i}. **ɪᴅ:** `{user_id}`\n"
                text += f"   **ᴜsᴇʀɴᴀᴍᴇ:** @{username}\n"
                text += f"   **ᴄʀᴇᴅɪᴛs:** {credits}\n"
                text += f"   **ᴊᴏɪɴᴇᴅ:** {joined}\n\n"
        else:
            text += "ɴᴏ ᴜsᴇʀs ꜰᴏᴜɴᴅ."
        
        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in recent users: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_ban_user$"))
async def admin_ban_user(client: Client, callback_query: CallbackQuery):
    """Ban user"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        await callback_query.edit_message_text(
            "🚫 **ʙᴀɴ ᴜsᴇʀ**\n\n"
            "sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴛᴏ ʙᴀɴ:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in ban user: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_unban_user$"))
async def admin_unban_user(client: Client, callback_query: CallbackQuery):
    """Unban user"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        await callback_query.edit_message_text(
            "✅ **ᴜɴʙᴀɴ ᴜsᴇʀ**\n\n"
            "sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴜɴʙᴀɴ:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in unban user: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_credits$"))
async def admin_add_credits(client: Client, callback_query: CallbackQuery):
    """Add credits to user"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        await callback_query.edit_message_text(
            "💰 **ᴀᴅᴅ ᴄʀᴇᴅɪᴛs**\n\n"
            "sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴀɴᴅ ᴄʀᴇᴅɪᴛs ᴀᴍᴏᴜɴᴛ:\n"
            "ᴇxᴀᴍᴘʟᴇ: `123456789 500`",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in add credits: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_user_stats$"))
async def admin_user_stats(client: Client, callback_query: CallbackQuery):
    """Show user statistics"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Get detailed user stats
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        active_users = await db.users.count_documents({
            "last_activity": {"$gte": datetime.now() - timedelta(days=7)}
        }) if db.users is not None else 0
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        banned_users = await db.users.count_documents({"banned": True}) if db.users is not None else 0
        
        # Top users by credits
        top_users = await db.users.find({}).sort("credits", -1).limit(5).to_list(None) if db.users is not None else []
        
        text = f"📊 **ᴅᴇᴛᴀɪʟᴇᴅ ᴜsᴇʀ sᴛᴀᴛɪsᴛɪᴄs**\n\n"
        text += f"**ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {total_users}\n"
        text += f"**ᴀᴄᴛɪᴠᴇ (7ᴅ):** {active_users}\n"
        text += f"**ᴘʀᴇᴍɪᴜᴍ:** {premium_users}\n"
        text += f"**ʙᴀɴɴᴇᴅ:** {banned_users}\n\n"
        
        if top_users:
            text += "🏆 **ᴛᴏᴘ ᴜsᴇʀs ʙʏ ᴄʀᴇᴅɪᴛs:**\n"
            for i, user in enumerate(top_users, 1):
                text += f"{i}. `{user.get('user_id', 'Unknown')}` - {user.get('credits', 0)} ᴄʀᴇᴅɪᴛs\n"
        
        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in user stats: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_premium$"))
async def admin_add_premium(client: Client, callback_query: CallbackQuery):
    """Add premium to user"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        await callback_query.edit_message_text(
            "➕ **ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ**\n\n"
            "sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴀɴᴅ ᴅᴀʏs:\n"
            "ᴇxᴀᴍᴘʟᴇ: `123456789 30`",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in add premium: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_create_code$"))
async def admin_create_code(client: Client, callback_query: CallbackQuery):
    """Create premium code"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        await callback_query.edit_message_text(
            "🎫 **ᴄʀᴇᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ**\n\n"
            "sᴇɴᴅ ᴅᴀʏs ꜰᴏʀ ᴛʜᴇ ᴄᴏᴅᴇ:\n"
            "ᴇxᴀᴍᴘʟᴇ: `30` (ꜰᴏʀ 30 ᴅᴀʏs ᴘʀᴇᴍɪᴜᴍ)",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in create code: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_premium_users$"))
async def admin_premium_users(client: Client, callback_query: CallbackQuery):
    """Show premium users"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Get premium users
        premium_users = await db.users.find({"premium_until": {"$gt": datetime.now()}}).sort("premium_until", -1).limit(10).to_list(None) if db.users is not None else []
        
        text = "📋 **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs**\n\n"
        
        if premium_users:
            for i, user in enumerate(premium_users, 1):
                user_id = user.get("user_id", "Unknown")
                username = user.get("username", "No username")
                premium_until = user.get("premium_until", "Unknown")
                
                text += f"{i}. **ɪᴅ:** `{user_id}`\n"
                text += f"   **ᴜsᴇʀɴᴀᴍᴇ:** @{username}\n"
                text += f"   **ᴇxᴘɪʀᴇs:** {premium_until}\n\n"
        else:
            text += "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ꜰᴏᴜɴᴅ."
        
        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in premium users: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_active_codes$"))
async def admin_active_codes(client: Client, callback_query: CallbackQuery):
    """Show active premium codes"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        # Get active codes
        active_codes = await db.premium_codes.find({"used": False}).sort("created_date", -1).limit(10).to_list(None) if db.premium_codes is not None else []
        
        text = "🎟️ **ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs**\n\n"
        
        if active_codes:
            for i, code in enumerate(active_codes, 1):
                code_str = code.get("code", "Unknown")
                days = code.get("days", 0)
                created_by = code.get("created_by", "Unknown")
                
                text += f"{i}. **ᴄᴏᴅᴇ:** `{code_str}`\n"
                text += f"   **ᴅᴀʏs:** {days}\n"
                text += f"   **ᴄʀᴇᴀᴛᴇᴅ ʙʏ:** `{created_by}`\n\n"
        else:
            text += "ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇs ꜰᴏᴜɴᴅ."
        
        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in active codes: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_security$"))
async def admin_security(client: Client, callback_query: CallbackQuery):
    """Security panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        text = "🔐 **sᴇᴄᴜʀɪᴛʏ ᴘᴀɴᴇʟ**\n\n"
        text += "ᴍᴀɴᴀɢᴇ sᴇᴄᴜʀɪᴛʏ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴀᴄᴄᴇss ᴄᴏɴᴛʀᴏʟ.\n\n"
        text += f"**ᴄᴜʀʀᴇɴᴛ ᴀᴅᴍɪɴs:** {len(Config.ADMINS)}\n"
        text += f"**ᴏᴡɴᴇʀ:** `{Config.OWNER_ID}`\n\n"
        text += "**sᴇᴄᴜʀɪᴛʏ ꜰᴇᴀᴛᴜʀᴇs:**\n"
        text += "• ᴀᴅᴍɪɴ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅs\n"
        text += "• ᴀᴜᴛᴏᴍᴀᴛɪᴄ ʙᴀɴ sʏsᴛᴇᴍ\n"
        text += "• ᴏᴘᴇʀᴀᴛɪᴏɴ ʟᴏɢɢɪɴɢ"
        
        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in security panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)