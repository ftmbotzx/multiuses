from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

def get_referral_rank(referral_count):
    """Get referral rank based on count"""
    if referral_count >= 100:
        return "🏆 ᴍᴀsᴛᴇʀ ʀᴇᴄʀᴜɪᴛᴇʀ"
    elif referral_count >= 50:
        return "🥇 ɢᴏʟᴅ ᴀᴍʙᴀssᴀᴅᴏʀ"
    elif referral_count >= 25:
        return "🥈 sɪʟᴠᴇʀ ᴀᴍʙᴀssᴀᴅᴏʀ"
    elif referral_count >= 10:
        return "🥉 ʙʀᴏɴᴢᴇ ᴀᴍʙᴀssᴀᴅᴏʀ"
    elif referral_count >= 5:
        return "⭐ ʀɪsɪɴɢ sᴛᴀʀ"
    else:
        return "🌱 ɴᴇᴡᴄᴏᴍᴇʀ"

def get_next_milestone(referral_count):
    """Get next milestone"""
    if referral_count < 5:
        return f"ɴᴇxᴛ: ⭐ ʀɪsɪɴɢ sᴛᴀʀ ({5 - referral_count} ᴍᴏʀᴇ)"
    elif referral_count < 10:
        return f"ɴᴇxᴛ: 🥉 ʙʀᴏɴᴢᴇ ({10 - referral_count} ᴍᴏʀᴇ)"
    elif referral_count < 25:
        return f"ɴᴇxᴛ: 🥈 sɪʟᴠᴇʀ ({25 - referral_count} ᴍᴏʀᴇ)"
    elif referral_count < 50:
        return f"ɴᴇxᴛ: 🥇 ɢᴏʟᴅ ({50 - referral_count} ᴍᴏʀᴇ)"
    elif referral_count < 100:
        return f"ɴᴇxᴛ: 🏆 ᴍᴀsᴛᴇʀ ({100 - referral_count} ᴍᴏʀᴇ)"
    else:
        return "🏆 ᴍᴀxɪᴍᴜᴍ ʀᴀɴᴋ ᴀᴄʜɪᴇᴠᴇᴅ!"

@Client.on_callback_query(filters.regex("^ref_stats$"))
async def ref_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle ref stats callback"""
    try:
        user_id = callback_query.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return
        
        # Get referral stats
        referral_count = await db.get_referral_stats(user_id)
        earned_credits = referral_count * Config.REFERRAL_BONUS
        
        stats_text = f"""
📊 **ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ sᴛᴀᴛs**

**ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟs:** {referral_count}
**ᴇᴀʀɴᴇᴅ ᴄʀᴇᴅɪᴛs:** {earned_credits}
**ʀᴇᴡᴀʀᴅ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ:** {Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs

**ʀᴇꜰᴇʀʀᴀʟ ʀᴀɴᴋɪɴɢ:**
{get_referral_rank(referral_count)}

**ɴᴇxᴛ ᴍɪʟᴇsᴛᴏɴᴇ:**
{get_next_milestone(referral_count)}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 ɢᴇᴛ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ", callback_data="referral_info")],
            [InlineKeyboardButton("💰 ᴄʜᴇᴄᴋ ᴄʀᴇᴅɪᴛs", callback_data="check_credits")]
        ])
        
        await callback_query.edit_message_text(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in ref stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ sᴛᴀᴛs", show_alert=True)