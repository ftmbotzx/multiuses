from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^premium_(monthly|yearly)$"))
async def premium_plan_callback(client: Client, callback_query: CallbackQuery):
    """Handle premium plan callbacks"""
    try:
        plan_type = callback_query.data.split("_")[1]
        plan_info = Config.PREMIUM_PRICES[plan_type]
        
        plan_text = f"""
💎 **{plan_type.title()} ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ**

**ᴅᴇᴛᴀɪʟs:**
• **ᴄʀᴇᴅɪᴛs:** {plan_info['credits']}
• **ᴅᴜʀᴀᴛɪᴏɴ:** {plan_info['days']} ᴅᴀʏs
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** ᴜɴʟɪᴍɪᴛᴇᴅ

**ɪɴᴄʟᴜᴅᴇᴅ ʙᴇɴᴇꜰɪᴛs:**
✅ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴀɪʟʏ ᴘʀᴏᴄᴇssɪɴɢ
✅ ᴘʀɪᴏʀɪᴛʏ ᴘʀᴏᴄᴇssɪɴɢ
✅ ʟᴀʀɢᴇʀ ꜰɪʟᴇ sɪᴢᴇ sᴜᴘᴘᴏʀᴛ
✅ ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs
✅ ᴘʀᴇᴍɪᴜᴍ sᴜᴘᴘᴏʀᴛ

**ᴛᴏ ᴘᴜʀᴄʜᴀsᴇ ᴛʜɪs ᴘʟᴀɴ:**
1. ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ꜰᴏʀ ᴘᴀʏᴍᴇɴᴛ ᴅᴇᴛᴀɪʟs
2. ᴍᴀᴋᴇ ᴘᴀʏᴍᴇɴᴛ ᴀɴᴅ sᴇɴᴅ ᴘʀᴏᴏꜰ
3. ᴀᴅᴍɪɴ ᴡɪʟʟ ᴀᴄᴛɪᴠᴀᴛᴇ ʏᴏᴜʀ ᴘʟᴀɴ

**ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇʟʏ:**
ᴜsᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ɢɪꜰᴛ ᴄᴏᴅᴇ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url=f"tg://user?id={Config.OWNER_ID}")],
            [InlineKeyboardButton("🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", callback_data="redeem_code")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_info")]
        ])
        
        await callback_query.edit_message_text(plan_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in premium plan callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘʟᴀɴ ɪɴꜰᴏ", show_alert=True)