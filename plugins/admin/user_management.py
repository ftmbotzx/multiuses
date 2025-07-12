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
    """Handle admin search user callback"""
    try:
        text = """
🔍 **sᴇᴀʀᴄʜ ᴜsᴇʀ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴇᴀʀᴄʜ ꜰᴏʀ ᴀ ᴜsᴇʀ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/searchuser <user_id>`
**ᴇxᴀᴍᴘʟᴇ:** `/searchuser 123456789`

ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴄᴏᴍᴘʟᴇᴛᴇ ᴜsᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ɪɴᴄʟᴜᴅɪɴɢ:
• ᴜsᴇʀ ᴅᴇᴛᴀɪʟs ᴀɴᴅ sᴛᴀᴛᴜs
• ᴄʀᴇᴅɪᴛ ʙᴀʟᴀɴᴄᴇ ᴀɴᴅ ᴜsᴀɢᴇ
• ᴘʀᴇᴍɪᴜᴍ ᴀɴᴅ ʀᴇꜰᴇʀʀᴀʟ ɪɴꜰᴏ
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin search user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_recent_users$"))
@admin_callback_only
async def admin_recent_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin recent users callback"""
    try:
        # Get recent users (last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now() - timedelta(days=1)
        
        recent_users = []
        if db.users is not None:
            cursor = db.users.find({
                "joined_date": {"$gte": recent_cutoff}
            }).sort("joined_date", -1).limit(10)
            
            async for user in cursor:
                recent_users.append(user)
        
        text = f"📋 **ʀᴇᴄᴇɴᴛ ᴜsᴇʀs (ʟᴀsᴛ 24ʜ)**\n\n"
        
        if recent_users:
            for i, user in enumerate(recent_users, 1):
                text += f"{i}. **{user.get('first_name', 'Unknown')}** (`{user.get('user_id')}`)\n"
                text += f"   ᴊᴏɪɴᴇᴅ: {user.get('joined_date', 'Unknown')}\n"
                text += f"   ᴄʀᴇᴅɪᴛs: {user.get('credits', 0)}\n\n"
        else:
            text += "ɴᴏ ɴᴇᴡ ᴜsᴇʀs ɪɴ ᴛʜᴇ ʟᴀsᴛ 24 ʜᴏᴜʀs."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_recent_users")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin recent users callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_ban_user$"))
@admin_callback_only
async def admin_ban_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin ban user callback"""
    try:
        text = """
🚫 **ʙᴀɴ ᴜsᴇʀ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʙᴀɴ ᴀ ᴜsᴇʀ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/ban <user_id>`
**ᴇxᴀᴍᴘʟᴇ:** `/ban 123456789`

⚠️ **ᴡᴀʀɴɪɴɢ:** ʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ!
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin ban user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_unban_user$"))
@admin_callback_only
async def admin_unban_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin unban user callback"""
    try:
        text = """
✅ **ᴜɴʙᴀɴ ᴜsᴇʀ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/unban <user_id>`
**ᴇxᴀᴍᴘʟᴇ:** `/unban 123456789`

✅ **ɴᴏᴛᴇ:** ᴜɴʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ᴀɢᴀɪɴ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin unban user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_credits$"))
@admin_callback_only
async def admin_add_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin add credits callback"""
    try:
        text = """
💰 **ᴀᴅᴅ ᴄʀᴇᴅɪᴛs**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴀᴅᴅ ᴄʀᴇᴅɪᴛs:

**ᴄᴏᴍᴍᴀɴᴅ:** `/addcredits <user_id> <amount>`
**ᴇxᴀᴍᴘʟᴇ:** `/addcredits 123456789 500`

💡 **ɴᴏᴛᴇ:** ᴄʀᴇᴅɪᴛs ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ ᴛᴏ ᴜsᴇʀ's ᴄᴜʀʀᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin add credits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_user_stats$"))
@admin_callback_only
async def admin_user_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin user stats callback"""
    try:
        # Get comprehensive user statistics
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        
        # Users by status
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        banned_users = await db.users.count_documents({"banned": True}) if db.users is not None else 0
        
        # Users by activity
        from datetime import timedelta
        active_today = await db.users.count_documents({
            "last_activity": {"$gte": datetime.now() - timedelta(days=1)}
        }) if db.users is not None else 0
        
        active_week = await db.users.count_documents({
            "last_activity": {"$gte": datetime.now() - timedelta(days=7)}
        }) if db.users is not None else 0
        
        # Credit statistics
        total_credits_pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$credits"}}}
        ]
        credit_result = await db.users.aggregate(total_credits_pipeline).to_list(1) if db.users is not None else []
        total_credits = credit_result[0]["total"] if credit_result else 0
        
        text = f"""
📊 **ᴅᴇᴛᴀɪʟᴇᴅ ᴜsᴇʀ sᴛᴀᴛɪsᴛɪᴄs**

**ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {total_users}

**ᴜsᴇʀ sᴛᴀᴛᴜs:**
• **ᴘʀᴇᴍɪᴜᴍ:** {premium_users} ({premium_users/total_users*100:.1f}% ᴏꜰ ᴛᴏᴛᴀʟ)
• **ʙᴀɴɴᴇᴅ:** {banned_users} ({banned_users/total_users*100:.1f}% ᴏꜰ ᴛᴏᴛᴀʟ)
• **ʀᴇɢᴜʟᴀʀ:** {total_users - premium_users - banned_users}

**ᴀᴄᴛɪᴠɪᴛʏ:**
• **ᴀᴄᴛɪᴠᴇ ᴛᴏᴅᴀʏ:** {active_today}
• **ᴀᴄᴛɪᴠᴇ ᴛʜɪs ᴡᴇᴇᴋ:** {active_week}

**ᴇᴄᴏɴᴏᴍʏ:**
• **ᴛᴏᴛᴀʟ ᴄʀᴇᴅɪᴛs ɪɴ sʏsᴛᴇᴍ:** {total_credits:,}
• **ᴀᴠᴇʀᴀɢᴇ ᴄʀᴇᴅɪᴛs ᴘᴇʀ ᴜsᴇʀ:** {total_credits/total_users:.1f if total_users > 0 else 0}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_user_stats")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin user stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)