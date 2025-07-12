from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.command("refer") & filters.private)
async def refer_command(client: Client, message: Message):
    """Handle /refer command"""
    try:
        user_id = message.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰɪʀsᴛ ᴜsɪɴɢ /start")
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
ᴋᴇᴇᴘ sʜᴀʀɪɴɢ ᴀɴᴅ ᴋᴇᴇᴘ ᴇᴀʀɴɪɴɢ!
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 ʀᴇꜰᴇʀʀᴀʟ sᴛᴀᴛs", callback_data="ref_stats")],
            [InlineKeyboardButton("💰 ᴄʜᴇᴄᴋ ᴄʀᴇᴅɪᴛs", callback_data="check_credits")]
        ])
        
        await message.reply_text(referral_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in refer command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ɢᴇɴᴇʀᴀᴛɪɴɢ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

@Client.on_message(filters.command("refstats") & filters.private)
async def refstats_command(client: Client, message: Message):
    """Handle /refstats command"""
    try:
        user_id = message.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰɪʀsᴛ ᴜsɪɴɢ /start")
            return
        
        # Get referral stats
        referral_count = await db.get_referral_stats(user_id)
        earned_credits = referral_count * Config.REFERRAL_BONUS
        
        def get_referral_rank(count):
            if count >= 100:
                return "🏆 ᴍᴀsᴛᴇʀ ʀᴇᴄʀᴜɪᴛᴇʀ"
            elif count >= 50:
                return "🥇 ɢᴏʟᴅ ᴀᴍʙᴀssᴀᴅᴏʀ"
            elif count >= 25:
                return "🥈 sɪʟᴠᴇʀ ᴀᴍʙᴀssᴀᴅᴏʀ"
            elif count >= 10:
                return "🥉 ʙʀᴏɴᴢᴇ ᴀᴍʙᴀssᴀᴅᴏʀ"
            elif count >= 5:
                return "⭐ ʀɪsɪɴɢ sᴛᴀʀ"
            else:
                return "🌱 ɴᴇᴡᴄᴏᴍᴇʀ"
        
        def get_next_milestone(count):
            if count < 5:
                return f"ɴᴇxᴛ: ⭐ ʀɪsɪɴɢ sᴛᴀʀ ({5 - count} ᴍᴏʀᴇ)"
            elif count < 10:
                return f"ɴᴇxᴛ: 🥉 ʙʀᴏɴᴢᴇ ({10 - count} ᴍᴏʀᴇ)"
            elif count < 25:
                return f"ɴᴇxᴛ: 🥈 sɪʟᴠᴇʀ ({25 - count} ᴍᴏʀᴇ)"
            elif count < 50:
                return f"ɴᴇxᴛ: 🥇 ɢᴏʟᴅ ({50 - count} ᴍᴏʀᴇ)"
            elif count < 100:
                return f"ɴᴇxᴛ: 🏆 ᴍᴀsᴛᴇʀ ({100 - count} ᴍᴏʀᴇ)"
            else:
                return "🏆 ᴍᴀxɪᴍᴜᴍ ʀᴀɴᴋ ᴀᴄʜɪᴇᴠᴇᴅ!"
        
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
        
        await message.reply_text(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in refstats command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ʀᴇꜰᴇʀʀᴀʟ sᴛᴀᴛs. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

# Callback handlers moved to separate files in plugins/referral/