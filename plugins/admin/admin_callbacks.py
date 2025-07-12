from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

# Missing callback handlers for admin panel buttons

@Client.on_callback_query(filters.regex("^admin_create_broadcast$"))
@admin_callback_only
async def admin_create_broadcast_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin create broadcast callback"""
    try:
        text = """
📝 **ᴄʀᴇᴀᴛᴇ ʙʀᴏᴀᴅᴄᴀsᴛ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴇɴᴅ ᴀ ʙʀᴏᴀᴅᴄᴀsᴛ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/broadcast <message>`
**ᴇxᴀᴍᴘʟᴇ:** `/broadcast Hello everyone! New features are coming soon!`

**ꜰᴇᴀᴛᴜʀᴇs:**
• sᴜᴘᴘᴏʀᴛs ᴍᴀʀᴋᴅᴏᴡɴ ꜰᴏʀᴍᴀᴛᴛɪɴɢ
• ᴀᴜᴛᴏᴍᴀᴛɪᴄ ʀᴀᴛᴇ ʟɪᴍɪᴛɪɴɢ
• ʀᴇᴀʟ-ᴛɪᴍᴇ ᴘʀᴏɢʀᴇss ᴛʀᴀᴄᴋɪɴɢ
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_broadcast")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin create broadcast callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_user_count$"))
@admin_callback_only
async def admin_user_count_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin user count callback"""
    try:
        # Get user counts for different categories
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({
            "last_activity": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}})
        banned_users = await db.users.count_documents({"banned": True})
        
        text = f"""
📊 **ᴜsᴇʀ ᴄᴏᴜɴᴛ**

**ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴀʀɢᴇᴛs:**
• **ᴀʟʟ ᴜsᴇʀs:** {total_users}
• **ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs:** {active_users}
• **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:** {premium_users}
• **ʙᴀɴɴᴇᴅ ᴜsᴇʀs:** {banned_users}

**ɴᴏᴛᴇ:** ʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴡɪʟʟ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ʙʀᴏᴀᴅᴄᴀsᴛs.

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_user_count")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_broadcast")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin user count callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_broadcast_active$"))
@admin_callback_only
async def admin_broadcast_active_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin broadcast active users callback"""
    try:
        text = """
📈 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs**

**ꜰᴇᴀᴛᴜʀᴇ ɴᴏᴛ ʏᴇᴛ ɪᴍᴘʟᴇᴍᴇɴᴛᴇᴅ**

ᴜsᴇ ᴛʜᴇ ʀᴇɢᴜʟᴀʀ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴍᴀɴᴅ ꜰᴏʀ ɴᴏᴡ:
`/broadcast <message>`

ᴛʜɪs ᴡɪʟʟ sᴇɴᴅ ᴛᴏ ᴀʟʟ ᴜsᴇʀs (ᴇxᴄʟᴜᴅɪɴɢ ʙᴀɴɴᴇᴅ).
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_broadcast")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin broadcast active callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_broadcast_premium$"))
@admin_callback_only
async def admin_broadcast_premium_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin broadcast premium users callback"""
    try:
        text = """
💎 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs**

**ꜰᴇᴀᴛᴜʀᴇ ɴᴏᴛ ʏᴇᴛ ɪᴍᴘʟᴇᴍᴇɴᴛᴇᴅ**

ᴜsᴇ ᴛʜᴇ ʀᴇɢᴜʟᴀʀ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴍᴀɴᴅ ꜰᴏʀ ɴᴏᴡ:
`/broadcast <message>`

ᴛʜɪs ᴡɪʟʟ sᴇɴᴅ ᴛᴏ ᴀʟʟ ᴜsᴇʀs (ɪɴᴄʟᴜᴅɪɴɢ ᴘʀᴇᴍɪᴜᴍ).
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_broadcast")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin broadcast premium callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_premium$"))
@admin_callback_only
async def admin_add_premium_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin add premium callback"""
    try:
        text = """
➕ **ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/addpremium <user_id> <days>`
**ᴇxᴀᴍᴘʟᴇ:** `/addpremium 123456789 30`

**ʙᴇɴᴇꜰɪᴛs:**
• ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴀɪʟʏ ᴏᴘᴇʀᴀᴛɪᴏɴs
• ᴘʀɪᴏʀɪᴛʏ ᴘʀᴏᴄᴇssɪɴɢ
• ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin add premium callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_create_code$"))
@admin_callback_only
async def admin_create_code_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin create code callback"""
    try:
        text = """
🎫 **ᴄʀᴇᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ᴄᴏᴅᴇ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/createcode <days>`
**ᴇxᴀᴍᴘʟᴇ:** `/createcode 30`

**ꜰᴇᴀᴛᴜʀᴇs:**
• ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛɪᴏɴ
• ᴇxᴘɪʀᴀᴛɪᴏɴ ᴛʀᴀᴄᴋɪɴɢ
• ᴏɴᴇ-ᴛɪᴍᴇ ᴜsᴇ ᴏɴʟʏ
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin create code callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_premium_users$"))
@admin_callback_only
async def admin_premium_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin premium users callback"""
    try:
        # Get premium users
        premium_users = await db.users.find({
            "premium_until": {"$gt": datetime.now()}
        }).sort("premium_until", -1).limit(20).to_list(None)
        
        text = "💎 **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs**\n\n"
        
        if premium_users:
            for i, user in enumerate(premium_users, 1):
                user_id = user.get("user_id")
                first_name = user.get("first_name", "Unknown")
                premium_until = user.get("premium_until")
                days_left = (premium_until - datetime.now()).days if premium_until else 0
                
                text += f"`{i}.` **{first_name}**\n"
                text += f"   ɪᴅ: `{user_id}`\n"
                text += f"   ᴇxᴘɪʀᴇs: {premium_until.strftime('%d/%m/%Y') if premium_until else 'Never'}\n"
                text += f"   ᴅᴀʏs ʟᴇꜰᴛ: {days_left}\n\n"
        else:
            text += "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_premium_users")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin premium users callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_active_codes$"))
@admin_callback_only
async def admin_active_codes_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin active codes callback"""
    try:
        # Get active codes
        active_codes = await db.premium_codes.find({
            "used": False
        }).sort("created_date", -1).limit(20).to_list(None)
        
        text = "🎟️ **ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇs**\n\n"
        
        if active_codes:
            for i, code in enumerate(active_codes, 1):
                code_str = code.get("code")
                days = code.get("days", 0)
                created_date = code.get("created_date", datetime.now())
                created_by = code.get("created_by")
                
                text += f"`{i}.` **{code_str}**\n"
                text += f"   ᴅᴀʏs: {days}\n"
                text += f"   ᴄʀᴇᴀᴛᴇᴅ: {created_date.strftime('%d/%m/%Y')}\n"
                text += f"   ʙʏ: `{created_by}`\n\n"
        else:
            text += "ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_active_codes")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin active codes callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_expiring_premium$"))
@admin_callback_only
async def admin_expiring_premium_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin expiring premium callback"""
    try:
        from datetime import timedelta
        
        # Get users with premium expiring in next 7 days
        expiring_soon = await db.users.find({
            "premium_until": {
                "$gt": datetime.now(),
                "$lt": datetime.now() + timedelta(days=7)
            }
        }).sort("premium_until", 1).to_list(None)
        
        text = "⏰ **ᴇxᴘɪʀɪɴɢ sᴏᴏɴ (ɴᴇxᴛ 7 ᴅᴀʏs)**\n\n"
        
        if expiring_soon:
            for i, user in enumerate(expiring_soon, 1):
                user_id = user.get("user_id")
                first_name = user.get("first_name", "Unknown")
                premium_until = user.get("premium_until")
                days_left = (premium_until - datetime.now()).days if premium_until else 0
                
                text += f"`{i}.` **{first_name}**\n"
                text += f"   ɪᴅ: `{user_id}`\n"
                text += f"   ᴇxᴘɪʀᴇs: {premium_until.strftime('%d/%m/%Y')}\n"
                text += f"   ᴅᴀʏs ʟᴇꜰᴛ: {days_left}\n\n"
        else:
            text += "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴇxᴘɪʀɪɴɢ ɪɴ ɴᴇxᴛ 7 ᴅᴀʏs."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_expiring_premium")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin expiring premium callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_premium_stats$"))
@admin_callback_only
async def admin_premium_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin premium stats callback"""
    try:
        # Get comprehensive premium stats
        total_premium = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}})
        expired_premium = await db.users.count_documents({
            "premium_until": {"$lt": datetime.now(), "$ne": None}
        })
        
        total_codes = await db.premium_codes.count_documents({})
        used_codes = await db.premium_codes.count_documents({"used": True})
        unused_codes = await db.premium_codes.count_documents({"used": False})
        
        text = f"""
📊 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛɪsᴛɪᴄs**

**ᴜsᴇʀs:**
• **ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ:** {total_premium}
• **ᴇxᴘɪʀᴇᴅ ᴘʀᴇᴍɪᴜᴍ:** {expired_premium}

**ᴄᴏᴅᴇs:**
• **ᴛᴏᴛᴀʟ ᴄᴏᴅᴇs:** {total_codes}
• **ᴜsᴇᴅ ᴄᴏᴅᴇs:** {used_codes}
• **ᴜɴᴜsᴇᴅ ᴄᴏᴅᴇs:** {unused_codes}

**ᴘʀɪᴄɪɴɢ:**
• **ᴍᴏɴᴛʜʟʏ:** {Config.PREMIUM_PRICES['monthly']['credits']} ᴄʀᴇᴅɪᴛs
• **ʏᴇᴀʀʟʏ:** {Config.PREMIUM_PRICES['yearly']['credits']} ᴄʀᴇᴅɪᴛs

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_premium_stats")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin premium stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)