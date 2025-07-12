from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^redeem_code$"))
async def redeem_code_callback(client: Client, callback_query: CallbackQuery):
    """Handle redeem code callback"""
    redeem_text = """
🎫 **ʀᴇᴅᴇᴇᴍ ɢɪꜰᴛ ᴄᴏᴅᴇ**

**ʜᴏᴡ ᴛᴏ ʀᴇᴅᴇᴇᴍ:**
1. ᴜsᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ: `/redeem <code>`
2. ʀᴇᴘʟᴀᴄᴇ `<code>` ᴡɪᴛʜ ʏᴏᴜʀ ᴀᴄᴛᴜᴀʟ ᴄᴏᴅᴇ

**ᴇxᴀᴍᴘʟᴇ:**
`/redeem PREMIUM30`

**ᴡʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴄᴏᴅᴇs:**
• ᴄᴏɴᴛᴇsᴛs ᴀɴᴅ ɢɪᴠᴇᴀᴡᴀʏs
• ᴄᴏᴍᴍᴜɴɪᴛʏ ᴇᴠᴇɴᴛs
• ᴘʀᴏᴍᴏᴛɪᴏɴᴀʟ ᴄᴀᴍᴘᴀɪɢɴs
• ᴘᴜʀᴄʜᴀsᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ

**ɴᴏᴛᴇ:** ᴇᴀᴄʜ ᴄᴏᴅᴇ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ᴏɴᴄᴇ.
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url=f"tg://user?id={Config.OWNER_ID}")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_info")]
    ])
    
    await callback_query.edit_message_text(redeem_text, reply_markup=keyboard)