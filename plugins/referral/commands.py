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
        
        # Get referral link
        referral_link = f"https://t.me/{client.me.username}?start={user_id}"
        
        # Get referral stats
        referrals = await db.get_referral_stats(user_id)
        
        refer_text = f"""
🎁 **ʀᴇꜰᴇʀʀᴀʟ ᴘʀᴏɢʀᴀᴍ**

**ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ:**
`{referral_link}`

**ʏᴏᴜʀ sᴛᴀᴛs:**
• **ʀᴇꜰᴇʀʀᴀʟs:** {referrals.get('count', 0)}
• **ᴇᴀʀɴɪɴɢs:** {referrals.get('earnings', 0)} ᴄʀᴇᴅɪᴛs

**ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:**
1. sʜᴀʀᴇ ʏᴏᴜʀ ʟɪɴᴋ ᴡɪᴛʜ ꜰʀɪᴇɴᴅs
2. ᴛʜᴇʏ ɢᴇᴛ {Config.DEFAULT_CREDITS} ᴄʀᴇᴅɪᴛs
3. ʏᴏᴜ ɢᴇᴛ {Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs

sʜᴀʀᴇ ᴀɴᴅ ᴇᴀʀɴ!
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 ʀᴇꜰᴇʀʀᴀʟ sᴛᴀᴛs", callback_data="ref_stats")]
        ])
        
        await message.reply_text(refer_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in refer command: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

@Client.on_message(filters.command("refstats") & filters.private)
async def refstats_command(client: Client, message: Message):
    """Handle /refstats command"""
    try:
        user_id = message.from_user.id
        
        # Get referral stats
        referrals = await db.get_referral_stats(user_id)
        
        stats_text = f"""
📊 **ʀᴇꜰᴇʀʀᴀʟ sᴛᴀᴛɪsᴛɪᴄs**

**ʏᴏᴜʀ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ:**
• **ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟs:** {referrals.get('count', 0)}
• **ᴛᴏᴛᴀʟ ᴇᴀʀɴɪɴɢs:** {referrals.get('earnings', 0)} ᴄʀᴇᴅɪᴛs
• **ᴀᴠᴇʀᴀɢᴇ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ:** {Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs

**ɪɴᴠɪᴛᴇ ᴍᴏʀᴇ ꜰʀɪᴇɴᴅs ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ ᴄʀᴇᴅɪᴛs!**
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 ɢᴇᴛ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ", callback_data="referral_info")]
        ])
        
        await message.reply_text(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in refstats command: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

@Client.on_message(filters.command("credits") & filters.private)
async def credits_command(client: Client, message: Message):
    """Handle /credits command"""
    try:
        user_id = message.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            return
        
        credits = user.get('credits', 0)
        daily_usage = user.get('daily_usage', 0)
        
        credits_text = f"""
💰 **ʏᴏᴜʀ ᴄʀᴇᴅɪᴛs**

**ᴀᴠᴀɪʟᴀʙʟᴇ ᴄʀᴇᴅɪᴛs:** {credits}
**ᴛᴏᴅᴀʏ's ᴜsᴀɢᴇ:** {daily_usage}/{Config.DAILY_LIMIT}

**ɴᴇᴇᴅ ᴍᴏʀᴇ ᴄʀᴇᴅɪᴛs?**
• ʀᴇꜰᴇʀ ꜰʀɪᴇɴᴅs
• ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ
• ᴜsᴇ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 ʀᴇꜰᴇʀ ꜰʀɪᴇɴᴅs", callback_data="referral_info")],
            [InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_info")]
        ])
        
        await message.reply_text(credits_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in credits command: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")