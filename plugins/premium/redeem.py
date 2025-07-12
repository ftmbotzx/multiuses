from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_command(client: Client, message: Message):
    """Handle /redeem command"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ**\n\n"
                "**ᴜsᴀɢᴇ:** `/redeem <code>`\n"
                "**ᴇxᴀᴍᴘʟᴇ:** `/redeem PREMIUM30`"
            )
            return
        
        code = message.command[1].upper()
        user_id = message.from_user.id
        
        # Try to redeem the code
        result = await db.redeem_premium_code(code, user_id)
        
        if result:
            await message.reply_text(
                f"🎉 **ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n"
                f"ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘɢʀᴀᴅᴇᴅ.\n"
                f"ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʟᴀɴ ᴡɪᴛʜ `/myplan`"
            )
        else:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ᴄᴏᴅᴇ**\n\n"
                "ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄᴏᴅᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
            )
            
    except Exception as e:
        logger.error(f"Error in redeem command: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

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