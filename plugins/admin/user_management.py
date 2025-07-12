from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime, timedelta

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

# Add missing user management callbacks
@Client.on_callback_query(filters.regex("^admin_search_user$"))
@admin_callback_only
async def admin_search_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle search user callback"""
    try:
        text = """
🔍 **sᴇᴀʀᴄʜ ᴜsᴇʀ**

ᴛᴏ sᴇᴀʀᴄʜ ꜰᴏʀ ᴀ ᴜsᴇʀ, ᴛʏᴘᴇ:
`/searchuser <user_id>`

**ᴇxᴀᴍᴘʟᴇ:**
`/searchuser 123456789`

ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴜsᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ɪɴᴄʟᴜᴅɪɴɢ:
• ᴜsᴇʀ ᴅᴇᴛᴀɪʟs
• ᴄʀᴇᴅɪᴛ ʙᴀʟᴀɴᴄᴇ
• ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs
• ᴀᴄᴛɪᴠɪᴛʏ ʜɪsᴛᴏʀʏ
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in search user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_recent_users$"))
@admin_callback_only
async def admin_recent_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle recent users callback"""
    try:
        # Get recent users
        recent_users = await db.users.find({}).sort("joined_date", -1).limit(10).to_list(None) if db.users is not None else []
        
        text = "📋 **ʀᴇᴄᴇɴᴛ ᴜsᴇʀs**\n\n"
        
        if recent_users:
            for i, user in enumerate(recent_users, 1):
                user_id = user.get("user_id", "Unknown")
                first_name = user.get("first_name", "Unknown")
                joined_date = user.get("joined_date", datetime.now())
                credits = user.get("credits", 0)
                
                text += f"`{i}.` **{first_name}** (ID: `{user_id}`)\n"
                text += f"    💰 {credits} credits\n"
                text += f"    📅 {joined_date.strftime('%d/%m/%Y')}\n\n"
        else:
            text += "ɴᴏ ᴜsᴇʀs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in recent users callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_ban_user$"))
@admin_callback_only
async def admin_ban_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle ban user callback"""
    try:
        text = """
🚫 **ʙᴀɴ ᴜsᴇʀ**

ᴛᴏ ʙᴀɴ ᴀ ᴜsᴇʀ, ᴛʏᴘᴇ:
`/ban <user_id>`

**ᴇxᴀᴍᴘʟᴇ:**
`/ban 123456789`

⚠️ **ᴡᴀʀɴɪɴɢ:** ʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ!
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in ban user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_unban_user$"))
@admin_callback_only
async def admin_unban_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle unban user callback"""
    try:
        text = """
✅ **ᴜɴʙᴀɴ ᴜsᴇʀ**

ᴛᴏ ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ, ᴛʏᴘᴇ:
`/unban <user_id>`

**ᴇxᴀᴍᴘʟᴇ:**
`/unban 123456789`

ᴛʜɪs ᴡɪʟʟ ʀᴇsᴛᴏʀᴇ ᴛʜᴇɪʀ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ʙᴏᴛ.
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in unban user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_credits$"))
@admin_callback_only
async def admin_add_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle add credits callback"""
    try:
        text = """
💰 **ᴀᴅᴅ ᴄʀᴇᴅɪᴛs**

ᴛᴏ ᴀᴅᴅ ᴄʀᴇᴅɪᴛs ᴛᴏ ᴀ ᴜsᴇʀ, ᴛʏᴘᴇ:
`/addcredits <user_id> <amount>`

**ᴇxᴀᴍᴘʟᴇ:**
`/addcredits 123456789 500`

ᴛʜɪs ᴡɪʟʟ ᴀᴅᴅ 500 ᴄʀᴇᴅɪᴛs ᴛᴏ ᴛʜᴇ ᴜsᴇʀ's ᴀᴄᴄᴏᴜɴᴛ.
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in add credits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_user_stats$"))
@admin_callback_only
async def admin_user_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle user stats callback"""
    try:
        # Get detailed user stats
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        active_users = await db.users.count_documents({"last_activity": {"$gte": datetime.now() - timedelta(days=7)}}) if db.users is not None else 0
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        banned_users = await db.users.count_documents({"banned": True}) if db.users is not None else 0
        new_users_today = await db.users.count_documents({
            "joined_date": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        }) if db.users is not None else 0
        
        text = f"""
📊 **ᴅᴇᴛᴀɪʟᴇᴅ ᴜsᴇʀ sᴛᴀᴛɪsᴛɪᴄs**

👥 **ᴜsᴇʀ ᴄᴏᴜɴᴛs:**
• **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {total_users}
• **ᴀᴄᴛɪᴠᴇ (7ᴅ):** {active_users}
• **ᴘʀᴇᴍɪᴜᴍ:** {premium_users}
• **ʙᴀɴɴᴇᴅ:** {banned_users}
• **ɴᴇᴡ ᴛᴏᴅᴀʏ:** {new_users_today}

📈 **ᴘᴇʀᴄᴇɴᴛᴀɢᴇs:**
• **ᴀᴄᴛɪᴠᴇ ʀᴀᴛᴇ:** {(active_users/total_users*100) if total_users > 0 else 0:.1f}%
• **ᴘʀᴇᴍɪᴜᴍ ʀᴀᴛᴇ:** {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%
• **ʙᴀɴ ʀᴀᴛᴇ:** {(banned_users/total_users*100) if total_users > 0 else 0:.1f}%
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in user stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)