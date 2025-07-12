from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from database.db import Database
from info import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.command("myplan") & filters.private)
async def my_plan_command(client: Client, message: Message):
    """Handle /myplan command"""
    try:
        user_id = message.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            return
        
        # Check premium status
        is_premium = await db.is_user_premium(user_id)
        
        if is_premium:
            premium_until = user.get("premium_until")
            if premium_until:
                remaining_days = (premium_until - datetime.now()).days
                expiry_date = premium_until.strftime("%d/%m/%Y")
                
                plan_text = f"""
📊 **ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ**

**ᴘʟᴀɴ ᴛʏᴘᴇ:** 💎 ᴘʀᴇᴍɪᴜᴍ
**sᴛᴀᴛᴜs:** ✅ ᴀᴄᴛɪᴠᴇ
**ᴇxᴘɪʀᴇs ᴏɴ:** {expiry_date}
**ᴅᴀʏs ʀᴇᴍᴀɪɴɪɴɢ:** {remaining_days} ᴅᴀʏs

**ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏ:**
• **ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {user.get('total_operations', 0)}
"""
            else:
                plan_text = f"""
📊 **ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ**

**ᴘʟᴀɴ ᴛʏᴘᴇ:** 💎 ᴘʀᴇᴍɪᴜᴍ
**sᴛᴀᴛᴜs:** ✅ ᴀᴄᴛɪᴠᴇ

**ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏ:**
• **ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {user.get('total_operations', 0)}
"""
        else:
            plan_text = f"""
📊 **ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ**

**ᴘʟᴀɴ ᴛʏᴘᴇ:** 🆓 ꜰʀᴇᴇ
**sᴛᴀᴛᴜs:** ✅ ᴀᴄᴛɪᴠᴇ
**ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT} ᴏᴘᴇʀᴀᴛɪᴏɴs

**ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏ:**
• **ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}
• **ᴛᴏᴅᴀʏ's ᴜsᴀɢᴇ:** {user.get('daily_usage', 0)}/{Config.DAILY_LIMIT}
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {user.get('total_operations', 0)}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_info")]
        ])
        
        await message.reply_text(plan_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in myplan command: {e}")
        await message.reply_text("❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

@Client.on_callback_query(filters.regex("^my_plan$"))
async def my_plan_callback(client: Client, callback_query: CallbackQuery):
    """Handle my plan callback"""
    try:
        user_id = callback_query.from_user.id
        
        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return
        
        # Check premium status
        is_premium = await db.is_user_premium(user_id)
        premium_until = user.get("premium_until")
        
        if is_premium and premium_until:
            remaining_days = (premium_until - datetime.now()).days
            expiry_date = premium_until.strftime("%d/%m/%Y")
            
            plan_text = f"""
📊 **ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ**

**ᴘʟᴀɴ ᴛʏᴘᴇ:** 💎 ᴘʀᴇᴍɪᴜᴍ
**sᴛᴀᴛᴜs:** ✅ ᴀᴄᴛɪᴠᴇ
**ᴇxᴘɪʀᴇs ᴏɴ:** {expiry_date}
**ᴅᴀʏs ʀᴇᴍᴀɪɴɪɴɢ:** {remaining_days} ᴅᴀʏs

**ᴀᴄᴛɪᴠᴇ ʙᴇɴᴇꜰɪᴛs:**
✅ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴀɪʟʏ ᴘʀᴏᴄᴇssɪɴɢ
✅ ᴘʀɪᴏʀɪᴛʏ ᴘʀᴏᴄᴇssɪɴɢ
✅ ʟᴀʀɢᴇʀ ꜰɪʟᴇ sɪᴢᴇ sᴜᴘᴘᴏʀᴛ
✅ ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs
✅ ᴘʀᴇᴍɪᴜᴍ sᴜᴘᴘᴏʀᴛ

**ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏ:**
• **ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {user.get('total_operations', 0)}
"""
        else:
            plan_text = f"""
📊 **ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ**

**ᴘʟᴀɴ ᴛʏᴘᴇ:** 🆓 ꜰʀᴇᴇ
**sᴛᴀᴛᴜs:** ✅ ᴀᴄᴛɪᴠᴇ
**ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT} ᴏᴘᴇʀᴀᴛɪᴏɴs

**ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏ:**
• **ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}
• **ᴛᴏᴅᴀʏ's ᴜsᴀɢᴇ:** {user.get('daily_usage', 0)}/{Config.DAILY_LIMIT}
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {user.get('total_operations', 0)}

**ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ꜰᴏʀ:**
• ᴜɴʟɪᴍɪᴛᴇᴅ ᴅᴀɪʟʏ ᴘʀᴏᴄᴇssɪɴɢ
• ᴘʀɪᴏʀɪᴛʏ ᴘʀᴏᴄᴇssɪɴɢ
• ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ", callback_data="premium_info")],
            [InlineKeyboardButton("🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", callback_data="redeem_code")],
            [InlineKeyboardButton("💰 ᴄʀᴇᴅɪᴛs", callback_data="check_credits")]
        ])
        
        await callback_query.edit_message_text(plan_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in my plan callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘʟᴀɴ ɪɴꜰᴏ", show_alert=True)