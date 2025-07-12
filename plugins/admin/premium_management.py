from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_premium$"))
@admin_callback_only
async def admin_premium_panel(client: Client, callback_query: CallbackQuery):
    """Premium management panel"""
    try:
            
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

@Client.on_callback_query(filters.regex("^admin_premium_users$"))
@admin_callback_only
async def admin_premium_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle premium users callback"""
    try:
            
        # Get premium users
        premium_users = await db.users.find({"premium_until": {"$gt": datetime.now()}}).sort("premium_until", -1).limit(10).to_list(None) if db.users is not None else []
        
        text = "📋 **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs**\n\n"
        
        if premium_users:
            for i, user in enumerate(premium_users, 1):
                user_id = user.get("user_id", "Unknown")
                first_name = user.get("first_name", "Unknown")
                premium_until = user.get("premium_until")
                
                if premium_until:
                    remaining_days = (premium_until - datetime.now()).days
                    text += f"`{i}.` **{first_name}** (ID: `{user_id}`)\n"
                    text += f"    ⏰ Expires in {remaining_days} days\n\n"
        else:
            text += "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in premium users callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_active_codes$"))
@admin_callback_only
async def admin_active_codes_callback(client: Client, callback_query: CallbackQuery):
    """Handle active codes callback"""
    try:
            
        # Get active codes
        active_codes = await db.premium_codes.find({"used": False}).sort("created_date", -1).limit(10).to_list(None) if db.premium_codes is not None else []
        
        text = "🎟️ **ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs**\n\n"
        
        if active_codes:
            for i, code in enumerate(active_codes, 1):
                code_text = code.get("code", "Unknown")
                days = code.get("days", 0)
                created_date = code.get("created_date", datetime.now())
                
                text += f"`{i}.` **{code_text}**\n"
                text += f"    💎 {days} days\n"
                text += f"    📅 {created_date.strftime('%d/%m/%Y')}\n\n"
        else:
            text += "ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in active codes callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Add missing premium management callbacks
@Client.on_callback_query(filters.regex("^admin_add_premium$"))
@admin_callback_only
async def admin_add_premium_callback(client: Client, callback_query: CallbackQuery):
    """Handle add premium callback"""
    try:
        text = """
➕ **ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ**

ᴛᴏ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ᴀ ᴜsᴇʀ, ᴛʏᴘᴇ:
`/addpremium <user_id> <days>`

**ᴇxᴀᴍᴘʟᴇ:**
`/addpremium 123456789 30`

ᴛʜɪs ᴡɪʟʟ ᴀᴅᴅ 30 ᴅᴀʏs ᴏꜰ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ.
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in add premium callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_create_code$"))
@admin_callback_only
async def admin_create_code_callback(client: Client, callback_query: CallbackQuery):
    """Handle create code callback"""
    try:
        text = """
🎫 **ᴄʀᴇᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ**

ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ, ᴛʏᴘᴇ:
`/createcode <days>`

**ᴇxᴀᴍᴘʟᴇ:**
`/createcode 30`

ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ ᴄᴏᴅᴇ ꜰᴏʀ 30 ᴅᴀʏs ᴏꜰ ᴘʀᴇᴍɪᴜᴍ.
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in create code callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_expiring_premium$"))
@admin_callback_only
async def admin_expiring_premium_callback(client: Client, callback_query: CallbackQuery):
    """Handle expiring premium callback"""
    try:
        # Get users with premium expiring soon (within 7 days)
        expiring_soon = datetime.now() + timedelta(days=7)
        expiring_users = await db.users.find({
            "premium_until": {"$gt": datetime.now(), "$lt": expiring_soon}
        }).sort("premium_until", 1).limit(10).to_list(None) if db.users is not None else []
        
        text = "⏰ **ᴇxᴘɪʀɪɴɢ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs**\n\n"
        
        if expiring_users:
            for i, user in enumerate(expiring_users, 1):
                user_id = user.get("user_id", "Unknown")
                first_name = user.get("first_name", "Unknown")
                premium_until = user.get("premium_until")
                
                if premium_until:
                    remaining_days = (premium_until - datetime.now()).days
                    text += f"`{i}.` **{first_name}** (ID: `{user_id}`)\n"
                    text += f"    ⏰ Expires in {remaining_days} days\n\n"
        else:
            text += "ɴᴏ ᴜsᴇʀs ᴡɪᴛʜ ᴇxᴘɪʀɪɴɢ ᴘʀᴇᴍɪᴜᴍ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in expiring premium callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_premium_stats$"))
@admin_callback_only
async def admin_premium_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle premium stats callback"""
    try:
        # Get premium statistics
        total_users = await db.users.count_documents({}) if db.users is not None else 0
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}}) if db.users is not None else 0
        expired_premium = await db.users.count_documents({
            "premium_until": {"$lt": datetime.now(), "$ne": None}
        }) if db.users is not None else 0
        
        unused_codes = await db.premium_codes.count_documents({"used": False}) if db.premium_codes is not None else 0
        used_codes = await db.premium_codes.count_documents({"used": True}) if db.premium_codes is not None else 0
        
        text = f"""
📊 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛɪsᴛɪᴄs**

👥 **ᴜsᴇʀs:**
• **ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ:** {premium_users}
• **ᴇxᴘɪʀᴇᴅ ᴘʀᴇᴍɪᴜᴍ:** {expired_premium}
• **ᴘʀᴇᴍɪᴜᴍ ʀᴀᴛᴇ:** {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%

🎫 **ᴄᴏᴅᴇs:**
• **ᴜɴᴜsᴇᴅ ᴄᴏᴅᴇs:** {unused_codes}
• **ᴜsᴇᴅ ᴄᴏᴅᴇs:** {used_codes}
• **ᴛᴏᴛᴀʟ ᴄᴏᴅᴇs:** {unused_codes + used_codes}

💰 **ᴘʀɪᴄɪɴɢ:**
• **ᴍᴏɴᴛʜʟʏ:** {Config.PREMIUM_PRICES['monthly']['credits']} ᴄʀᴇᴅɪᴛs
• **ʏᴇᴀʀʟʏ:** {Config.PREMIUM_PRICES['yearly']['credits']} ᴄʀᴇᴅɪᴛs
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_premium")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in premium stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)