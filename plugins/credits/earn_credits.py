from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^earn_credits$"))
async def earn_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle earn credits callback"""
    earn_text = f"""
📊 **ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴄʀᴇᴅɪᴛs**

**ꜰʀᴇᴇ ᴡᴀʏs:**
🎁 **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs**
• ɪɴᴠɪᴛᴇ ꜰʀɪᴇɴᴅs: +{Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs
• ɴᴏ ʟɪᴍɪᴛ ᴏɴ ʀᴇꜰᴇʀʀᴀʟs!

**ᴘʀᴇᴍɪᴜᴍ ᴡᴀʏs:**
💎 **ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs**
• ᴍᴏɴᴛʜʟʏ: {Config.PREMIUM_PRICES['monthly']['credits']} ᴄʀᴇᴅɪᴛs
• ʏᴇᴀʀʟʏ: {Config.PREMIUM_PRICES['yearly']['credits']} ᴄʀᴇᴅɪᴛs

🎫 **ɢɪꜰᴛ ᴄᴏᴅᴇs**
• ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ ᴄᴏɴᴛᴇsᴛs
• ꜰᴏʟʟᴏᴡ ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛs
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 ɢᴇᴛ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ", callback_data="referral_info")],
        [InlineKeyboardButton("💎 ᴠɪᴇᴡ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_info")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="check_credits")]
    ])
    
    await callback_query.edit_message_text(earn_text, reply_markup=keyboard)