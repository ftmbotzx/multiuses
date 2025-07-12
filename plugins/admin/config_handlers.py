from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
import os

logger = logging.getLogger(__name__)
db = Database()

# Implement actual configuration change handlers

@Client.on_callback_query(filters.regex("^config_change_default_credits$"))
@admin_callback_only
async def config_change_default_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle changing default credits"""
    try:
        text = f"""
📝 **ᴄʜᴀɴɢᴇ ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs**

**ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ:** {Config.DEFAULT_CREDITS} ᴄʀᴇᴅɪᴛs

**ʜᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ:**
1. sᴇᴛ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇ: `DEFAULT_CREDITS=200`
2. ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ

**ɴᴏᴛᴇ:** ᴛʜɪs ʀᴇQᴜɪʀᴇs sᴇʀᴠᴇʀ ᴀᴄᴄᴇss ᴛᴏ ᴄʜᴀɴɢᴇ 
ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs. ᴄᴜʀʀᴇɴᴛʟʏ ᴄᴀɴɴᴏᴛ ʙᴇ 
ᴄʜᴀɴɢᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ.

**ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ ᴠᴀʟᴜᴇs:**
• 50 - ʟᴏᴡ sᴛᴀʀᴛɪɴɢ ᴄʀᴇᴅɪᴛs
• 100 - sᴛᴀɴᴅᴀʀᴅ (ᴄᴜʀʀᴇɴᴛ)
• 200 - ɢᴇɴᴇʀᴏᴜs sᴛᴀʀᴛɪɴɢ ᴄʀᴇᴅɪᴛs
• 500 - ꜰᴏʀ ᴛᴇsᴛɪɴɢ ᴘᴜʀᴘᴏsᴇs
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 50", callback_data="set_credits_50"),
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 200", callback_data="set_credits_200")
            ],
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 500", callback_data="set_credits_500"),
                InlineKeyboardButton("ℹ️ ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs", callback_data="credits_info")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config_credits")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config change default credits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^config_change_process_cost$"))
@admin_callback_only
async def config_change_process_cost_callback(client: Client, callback_query: CallbackQuery):
    """Handle changing process cost"""
    try:
        text = f"""
💸 **ᴄʜᴀɴɢᴇ ᴘʀᴏᴄᴇss ᴄᴏsᴛ**

**ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ:** {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ᴘᴇʀ ᴏᴘᴇʀᴀᴛɪᴏɴ

**ʜᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ:**
1. sᴇᴛ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇ: `PROCESS_COST=5`
2. ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ

**ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ ᴠᴀʟᴜᴇs:**
• 1 - ᴠᴇʀʏ ᴄʜᴇᴀᴘ (ᴀʟᴍᴏsᴛ ꜰʀᴇᴇ)
• 5 - ᴄʜᴇᴀᴘ ᴏᴘᴇʀᴀᴛɪᴏɴs
• 10 - sᴛᴀɴᴅᴀʀᴅ (ᴄᴜʀʀᴇɴᴛ)
• 20 - ᴇxᴘᴇɴsɪᴠᴇ ᴏᴘᴇʀᴀᴛɪᴏɴs
• 50 - ᴘʀᴇᴍɪᴜᴍ ᴘʀɪᴄɪɴɢ

**ɪᴍᴘᴀᴄᴛ:**
ʜɪɢʜᴇʀ ᴄᴏsᴛ = ꜰᴇᴡᴇʀ ᴏᴘᴇʀᴀᴛɪᴏɴs ᴘᴇʀ ᴜsᴇʀ
ʟᴏᴡᴇʀ ᴄᴏsᴛ = ᴍᴏʀᴇ ᴏᴘᴇʀᴀᴛɪᴏɴs ᴘᴇʀ ᴜsᴇʀ
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 1", callback_data="set_cost_1"),
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 5", callback_data="set_cost_5")
            ],
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 20", callback_data="set_cost_20"),
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 50", callback_data="set_cost_50")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config_credits")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config change process cost callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^config_change_referral_bonus$"))
@admin_callback_only
async def config_change_referral_bonus_callback(client: Client, callback_query: CallbackQuery):
    """Handle changing referral bonus"""
    try:
        text = f"""
🎁 **ᴄʜᴀɴɢᴇ ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs**

**ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ:** {Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs

**ʜᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ:**
1. sᴇᴛ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇ: `REFERRAL_BONUS=50`
2. ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ

**ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ ᴠᴀʟᴜᴇs:**
• 25 - sᴍᴀʟʟ ɪɴᴄᴇɴᴛɪᴠᴇ
• 50 - ᴍᴏᴅᴇʀᴀᴛᴇ ɪɴᴄᴇɴᴛɪᴠᴇ
• 100 - sᴛʀᴏɴɢ ɪɴᴄᴇɴᴛɪᴠᴇ (ᴄᴜʀʀᴇɴᴛ)
• 200 - ᴠᴇʀʏ sᴛʀᴏɴɢ ɪɴᴄᴇɴᴛɪᴠᴇ
• 500 - ᴍᴀxɪᴍᴜᴍ ɪɴᴄᴇɴᴛɪᴠᴇ

**ɪᴍᴘᴀᴄᴛ:**
ʜɪɢʜᴇʀ ʙᴏɴᴜs = ᴍᴏʀᴇ ʀᴇꜰᴇʀʀᴀʟs
ʟᴏᴡᴇʀ ʙᴏɴᴜs = ꜰᴇᴡᴇʀ ʀᴇꜰᴇʀʀᴀʟs
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 25", callback_data="set_referral_25"),
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 50", callback_data="set_referral_50")
            ],
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 200", callback_data="set_referral_200"),
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 500", callback_data="set_referral_500")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config_credits")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config change referral bonus callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^config_change_daily_limit$"))
@admin_callback_only
async def config_change_daily_limit_callback(client: Client, callback_query: CallbackQuery):
    """Handle changing daily limit"""
    try:
        text = f"""
📅 **ᴄʜᴀɴɢᴇ ᴅᴀɪʟʏ ʟɪᴍɪᴛ**

**ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ:** {Config.DAILY_LIMIT} ᴏᴘᴇʀᴀᴛɪᴏɴs ᴘᴇʀ ᴅᴀʏ

**ʜᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ:**
1. sᴇᴛ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇ: `DAILY_LIMIT=10`
2. ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ

**ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ ᴠᴀʟᴜᴇs:**
• 5 - ᴠᴇʀʏ ʀᴇsᴛʀɪᴄᴛɪᴠᴇ
• 10 - ʀᴇsᴛʀɪᴄᴛɪᴠᴇ
• 20 - ᴍᴏᴅᴇʀᴀᴛᴇ (ᴄᴜʀʀᴇɴᴛ)
• 50 - ɢᴇɴᴇʀᴏᴜs
• 100 - ᴠᴇʀʏ ɢᴇɴᴇʀᴏᴜs
• 0 - ɴᴏ ʟɪᴍɪᴛ

**ɪᴍᴘᴀᴄᴛ:**
ᴏɴʟʏ ᴀᴘᴘʟɪᴇs ᴛᴏ ꜰʀᴇᴇ ᴜsᴇʀs.
ᴘʀᴇᴍɪᴜᴍ ᴀɴᴅ ᴀᴅᴍɪɴs ʜᴀᴠᴇ ɴᴏ ʟɪᴍɪᴛs.
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 5", callback_data="set_limit_5"),
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 10", callback_data="set_limit_10")
            ],
            [
                InlineKeyboardButton("🔧 sᴇᴛ ᴛᴏ 50", callback_data="set_limit_50"),
                InlineKeyboardButton("🔧 ɴᴏ ʟɪᴍɪᴛ", callback_data="set_limit_0")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config_limits")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config change daily limit callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Note handlers that inform users these settings require environment variable changes
@Client.on_callback_query(filters.regex("^set_(credits|cost|referral|limit)_\d+$"))
@admin_callback_only
async def config_set_value_callback(client: Client, callback_query: CallbackQuery):
    """Handle setting configuration values"""
    try:
        await callback_query.answer("⚠️ ᴛʜɪs ʀᴇQᴜɪʀᴇs ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇ ᴄʜᴀɴɢᴇ", show_alert=True)
        
        text = """
⚠️ **ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ ɴᴏᴛɪᴄᴇ**

**ɪᴍᴘᴏʀᴛᴀɴᴛ:**
ᴛʜɪs ʙᴏᴛ ᴜsᴇs ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs ꜰᴏʀ 
ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ. ᴄʜᴀɴɢᴇs ʀᴇQᴜɪʀᴇ:

1. **sᴇʀᴠᴇʀ ᴀᴄᴄᴇss** ᴛᴏ ᴍᴏᴅɪꜰʏ .ᴇɴᴠ ꜰɪʟᴇ
2. **ʙᴏᴛ ʀᴇsᴛᴀʀᴛ** ᴛᴏ ᴀᴘᴘʟʏ ᴄʜᴀɴɢᴇs

**ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇs:**
• ᴜsᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ꜰᴏʀ ᴜsᴇʀs
• ᴍᴀɴᴜᴀʟ ᴄʀᴇᴅɪᴛ ᴀᴅᴊᴜsᴛᴍᴇɴᴛs ᴠɪᴀ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ
• ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛɪᴏɴ

**ɴᴇxᴛ sᴛᴇᴘs:**
1. ᴀᴄᴄᴇss sᴇʀᴠᴇʀ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ
2. ᴍᴏᴅɪꜰʏ ʀᴇQᴜɪʀᴇᴅ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇ
3. ʀᴇsᴛᴀʀᴛ ʙᴏᴛ ᴛᴏ ᴀᴘᴘʟʏ ᴄʜᴀɴɢᴇs
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📖 ᴠɪᴇᴡ ᴀʟʟ ᴇɴᴠ ᴠᴀʀs", callback_data="view_env_vars"),
                InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="admin_restart_bot")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config set value callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^view_env_vars$"))
@admin_callback_only
async def view_env_vars_callback(client: Client, callback_query: CallbackQuery):
    """Show all environment variables"""
    try:
        text = f"""
📖 **ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs**

**ᴄʀᴇᴅɪᴛ sʏsᴛᴇᴍ:**
• `DEFAULT_CREDITS={Config.DEFAULT_CREDITS}`
• `PROCESS_COST={Config.PROCESS_COST}`
• `REFERRAL_BONUS={Config.REFERRAL_BONUS}`
• `DAILY_LIMIT={Config.DAILY_LIMIT}`

**ᴀᴅᴍɪɴ sᴇᴛᴛɪɴɢs:**
• `OWNER_ID={Config.OWNER_ID}`
• `ADMINS={','.join(map(str, Config.ADMINS))}`

**ᴅɪʀᴇᴄᴛᴏʀɪᴇs:**
• `DOWNLOADS_DIR={Config.DOWNLOADS_DIR}`
• `UPLOADS_DIR={Config.UPLOADS_DIR}`
• `TEMP_DIR={Config.TEMP_DIR}`

**ᴘʀᴇᴍɪᴜᴍ sᴇᴛᴛɪɴɢs:**
• ᴍᴏɴᴛʜʟʏ: {Config.PREMIUM_PRICES['monthly']['credits']} ᴄʀᴇᴅɪᴛs, {Config.PREMIUM_PRICES['monthly']['days']} ᴅᴀʏs
• ʏᴇᴀʀʟʏ: {Config.PREMIUM_PRICES['yearly']['credits']} ᴄʀᴇᴅɪᴛs, {Config.PREMIUM_PRICES['yearly']['days']} ᴅᴀʏs

**ɴᴏᴛᴇ:** ᴀʟʟ ᴄʜᴀɴɢᴇs ʀᴇQᴜɪʀᴇ ʙᴏᴛ ʀᴇsᴛᴀʀᴛ
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="admin_restart_bot"),
                InlineKeyboardButton("📋 ᴄᴏᴘʏ ᴛᴇᴍᴘʟᴀᴛᴇ", callback_data="copy_env_template")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in view env vars callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)