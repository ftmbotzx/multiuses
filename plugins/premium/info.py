from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^premium_info$"))
async def premium_info_callback(client: Client, callback_query: CallbackQuery):
    """Handle premium info callback"""
    try:
        premium_text = f"""
💎 **ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs**

**ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs:**

📅 **ᴍᴏɴᴛʜʟʏ ᴘʟᴀɴ**
• **ᴄʀᴇᴅɪᴛs:** {Config.PREMIUM_PRICES['monthly']['credits']}
• **ᴅᴜʀᴀᴛɪᴏɴ:** {Config.PREMIUM_PRICES['monthly']['days']} ᴅᴀʏs
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** ᴜɴʟɪᴍɪᴛᴇᴅ

🗓️ **ʏᴇᴀʀʟʏ ᴘʟᴀɴ**
• **ᴄʀᴇᴅɪᴛs:** {Config.PREMIUM_PRICES['yearly']['credits']}
• **ᴅᴜʀᴀᴛɪᴏɴ:** {Config.PREMIUM_PRICES['yearly']['days']} ᴅᴀʏs
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** ᴜɴʟɪᴍɪᴛᴇᴅ
• **ʙᴇsᴛ ᴠᴀʟᴜᴇ!** 💰

**ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛs:**
✅ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴀɪʟʏ ᴘʀᴏᴄᴇssɪɴɢ
✅ ᴘʀɪᴏʀɪᴛʏ ᴘʀᴏᴄᴇssɪɴɢ
✅ ʟᴀʀɢᴇʀ ꜰɪʟᴇ sɪᴢᴇ sᴜᴘᴘᴏʀᴛ
✅ ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs
✅ ᴘʀᴇᴍɪᴜᴍ sᴜᴘᴘᴏʀᴛ
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 ᴍᴏɴᴛʜʟʏ ᴘʟᴀɴ", callback_data="premium_monthly")],
            [InlineKeyboardButton("🗓️ ʏᴇᴀʀʟʏ ᴘʟᴀɴ", callback_data="premium_yearly")],
            [InlineKeyboardButton("🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", callback_data="redeem_code")],
            [InlineKeyboardButton("📊 ᴍʏ ᴘʟᴀɴ", callback_data="my_plan")]
        ])
        
        await callback_query.edit_message_text(premium_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in premium info callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘʀᴇᴍɪᴜᴍ ɪɴꜰᴏ", show_alert=True)