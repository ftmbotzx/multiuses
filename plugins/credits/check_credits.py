from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^check_credits$"))
async def check_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle check credits callback"""
    try:
        user_id = callback_query.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return
        
        credits = user.get("credits", 0)
        daily_usage = user.get("daily_usage", 0)
        
        # Check if premium
        is_premium = await db.is_user_premium(user_id)
        premium_text = "💎 ᴘʀᴇᴍɪᴜᴍ" if is_premium else "🆓 ꜰʀᴇᴇ"
        
        credits_text = f"""
💰 **ʏᴏᴜʀ ᴄʀᴇᴅɪᴛs**

**ᴀᴠᴀɪʟᴀʙʟᴇ:** {credits} ᴄʀᴇᴅɪᴛs
**ᴘʟᴀɴ:** {premium_text}
**ᴛᴏᴅᴀʏ's ᴜsᴀɢᴇ:** {daily_usage}/{Config.DAILY_LIMIT if not is_premium else "∞"}
**ᴇsᴛɪᴍᴀᴛᴇᴅ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {credits // Config.PROCESS_COST}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 ᴇᴀʀɴ ᴍᴏʀᴇ", callback_data="earn_credits")],
            [InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_info")]
        ])
        
        await callback_query.edit_message_text(credits_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in check credits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴄʀᴇᴅɪᴛs", show_alert=True)