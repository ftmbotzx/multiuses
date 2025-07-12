from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_premium$"))
async def admin_premium_panel(client: Client, callback_query: CallbackQuery):
    """Premium management panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
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
async def admin_premium_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle premium users callback"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
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
async def admin_active_codes_callback(client: Client, callback_query: CallbackQuery):
    """Handle active codes callback"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
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