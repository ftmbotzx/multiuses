from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_only, admin_callback_only
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.command("searchuser") & filters.private)
@admin_only
async def search_user_command(client: Client, message: Message):
    """Handle /searchuser command"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ**\n\n"
                "**ᴜsᴀɢᴇ:** `/searchuser <user_id>`\n"
                "**ᴇxᴀᴍᴘʟᴇ:** `/searchuser 123456789`"
            )
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ")
            return
        
        # Search for user
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            return
        
        # Get user's stats
        is_premium = await db.is_user_premium(user_id)
        is_banned = await db.is_user_banned(user_id)
        referrals = await db.get_referral_stats(user_id)
        
        # Format user info
        text = f"""
🔍 **ᴜsᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**

**ʙᴀsɪᴄ ɪɴꜰᴏ:**
• **ᴜsᴇʀ ɪᴅ:** `{user_id}`
• **ɴᴀᴍᴇ:** {user.get('first_name', 'Unknown')}
• **ᴜsᴇʀɴᴀᴍᴇ:** @{user.get('username', 'None')}
• **ᴊᴏɪɴᴇᴅ:** {user.get('joined_date', 'Unknown')}

**ᴀᴄᴄᴏᴜɴᴛ sᴛᴀᴛᴜs:**
• **ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}
• **ᴘʀᴇᴍɪᴜᴍ:** {'✅' if is_premium else '❌'}
• **ʙᴀɴɴᴇᴅ:** {'✅' if is_banned else '❌'}
• **ᴅᴀɪʟʏ ᴜsᴀɢᴇ:** {user.get('daily_usage', 0)}/{Config.DAILY_LIMIT}

**ʀᴇꜰᴇʀʀᴀʟs:**
• **ʀᴇꜰᴇʀʀᴇᴅ ʙʏ:** {user.get('referred_by', 'None')}
• **ʀᴇꜰᴇʀʀᴀʟs ᴄᴏᴜɴᴛ:** {referrals.get('count', 0)}
• **ʀᴇꜰᴇʀʀᴀʟ ᴇᴀʀɴɪɴɢs:** {referrals.get('earnings', 0)}

**ᴘʀᴇᴍɪᴜᴍ ɪɴꜰᴏ:**
• **ᴘʀᴇᴍɪᴜᴍ ᴜɴᴛɪʟ:** {user.get('premium_until', 'None')}
"""
        
        await message.reply_text(text)
        
    except Exception as e:
        logger.error(f"Error in search user command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ sᴇᴀʀᴄʜɪɴɢ ᴜsᴇʀ.")

@Client.on_callback_query(filters.regex("^admin_search_user$"))
@admin_callback_only
async def admin_search_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin search user callback"""
    try:
        text = """
🔍 **sᴇᴀʀᴄʜ ᴜsᴇʀ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴇᴀʀᴄʜ ꜰᴏʀ ᴀ ᴜsᴇʀ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/searchuser <user_id>`
**ᴇxᴀᴍᴘʟᴇ:** `/searchuser 123456789`

ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴄᴏᴍᴘʟᴇᴛᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴜsᴇʀ.
"""
        
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin search user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_recent_users$"))
@admin_callback_only
async def admin_recent_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin recent users callback"""
    try:
        # Get recent users (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(hours=24)
        
        recent_users = await db.users.find({
            "joined_date": {"$gte": yesterday}
        }).sort("joined_date", -1).limit(20).to_list(None)
        
        text = "👥 **ʀᴇᴄᴇɴᴛ ᴜsᴇʀs (ʟᴀsᴛ 24ʜ)**\n\n"
        
        if recent_users:
            for i, user in enumerate(recent_users, 1):
                user_id = user.get("user_id")
                first_name = user.get("first_name", "Unknown")
                joined_date = user.get("joined_date", datetime.now())
                
                text += f"`{i}.` **{first_name}**\n"
                text += f"   ɪᴅ: `{user_id}`\n"
                text += f"   ᴊᴏɪɴᴇᴅ: {joined_date.strftime('%d/%m %H:%M')}\n\n"
        else:
            text += "ɴᴏ ɴᴇᴡ ᴜsᴇʀs ɪɴ ᴛʜᴇ ʟᴀsᴛ 24 ʜᴏᴜʀs."
        
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin recent users callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_ban_user$"))
@admin_callback_only
async def admin_ban_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin ban user callback"""
    try:
        text = """
🚫 **ʙᴀɴ ᴜsᴇʀ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʙᴀɴ ᴀ ᴜsᴇʀ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/ban <user_id>`
**ᴇxᴀᴍᴘʟᴇ:** `/ban 123456789`

⚠️ **ᴡᴀʀɴɪɴɢ:** ʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ.
"""
        
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin ban user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_unban_user$"))
@admin_callback_only
async def admin_unban_user_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin unban user callback"""
    try:
        text = """
✅ **ᴜɴʙᴀɴ ᴜsᴇʀ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/unban <user_id>`
**ᴇxᴀᴍᴘʟᴇ:** `/unban 123456789`

ᴛʜɪs ᴡɪʟʟ ʀᴇsᴛᴏʀᴇ ᴛʜᴇ ᴜsᴇʀ's ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ʙᴏᴛ.
"""
        
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin unban user callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_add_credits$"))
@admin_callback_only
async def admin_add_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin add credits callback"""
    try:
        text = """
💰 **ᴀᴅᴅ ᴄʀᴇᴅɪᴛs**

ᴛᴏ ᴀᴅᴅ ᴄʀᴇᴅɪᴛs ᴛᴏ ᴀ ᴜsᴇʀ, ᴜsᴇ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ sᴇᴄᴛɪᴏɴ.

ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇʟʏ, ᴜsᴇ:
**ᴄᴏᴍᴍᴀɴᴅ:** `/addpremium <user_id> <days>`

ᴛʜɪs ᴡɪʟʟ ɢʀᴀɴᴛ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴡɪᴛʜ ᴜɴʟɪᴍɪᴛᴇᴅ ᴄʀᴇᴅɪᴛs.
"""
        
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="admin_premium")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin add credits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_user_stats$"))
@admin_callback_only
async def admin_user_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin user stats callback"""
    try:
        # Get comprehensive user stats
        stats = await db.get_user_stats()
        
        text = f"""
📊 **ᴅᴇᴛᴀɪʟᴇᴅ ᴜsᴇʀ sᴛᴀᴛɪsᴛɪᴄs**

**ᴏᴠᴇʀᴀʟʟ:**
• **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {stats.get('total_users', 0)}
• **ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs:** {stats.get('active_users', 0)}
• **ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:** {stats.get('premium_users', 0)}
• **ʙᴀɴɴᴇᴅ ᴜsᴇʀs:** {stats.get('banned_users', 0)}

**ᴇɴɢᴀɢᴇᴍᴇɴᴛ:**
• **ᴛᴏᴅᴀʏ's ɴᴇᴡ ᴜsᴇʀs:** {stats.get('new_today', 0)}
• **ᴛʜɪs ᴡᴇᴇᴋ's ɴᴇᴡ:** {stats.get('new_week', 0)}
• **ᴛʜɪs ᴍᴏɴᴛʜ's ɴᴇᴡ:** {stats.get('new_month', 0)}

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_user_stats")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_users")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin user stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)