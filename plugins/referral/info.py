from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^referral_info$"))
async def referral_info_callback(client: Client, callback_query: CallbackQuery):
    """Handle referral info callback"""
    try:
        user_id = callback_query.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return
        
        # Get bot info
        bot_info = await client.get_me()
        referral_link = f"https://t.me/{bot_info.username}?start={user_id}"
        
        # Get referral stats
        referral_count = await db.get_referral_stats(user_id)
        
        referral_text = f"""
🎁 **ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ**

**ʏᴏᴜʀ ʟɪɴᴋ:**
`{referral_link}`

**ʀᴇꜰᴇʀʀᴀʟ sᴛᴀᴛs:**
• **ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟs:** {referral_count}
• **ᴇᴀʀɴᴇᴅ ᴄʀᴇᴅɪᴛs:** {referral_count * Config.REFERRAL_BONUS}

**ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:**
1. sʜᴀʀᴇ ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ
2. ᴡʜᴇɴ sᴏᴍᴇᴏɴᴇ ᴊᴏɪɴs ᴜsɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ
3. ʏᴏᴜ ɢᴇᴛ **{Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs** ɪɴsᴛᴀɴᴛʟʏ!

**ɴᴏ ʟɪᴍɪᴛ ᴏɴ ʀᴇꜰᴇʀʀᴀʟs!**
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 ᴅᴇᴛᴀɪʟᴇᴅ sᴛᴀᴛs", callback_data="ref_stats")],
            [InlineKeyboardButton("💰 ᴄʜᴇᴄᴋ ᴄʀᴇᴅɪᴛs", callback_data="check_credits")]
        ])
        
        await callback_query.edit_message_text(referral_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in referral info callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ʀᴇꜰᴇʀʀᴀʟ ɪɴꜰᴏ", show_alert=True)