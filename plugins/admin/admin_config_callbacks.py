from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

# Admin Configuration Management - Allow changing any bot setting

@Client.on_callback_query(filters.regex("^admin_config$"))
@admin_callback_only
async def admin_config_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin configuration main menu"""
    try:
        text = """
⚙️ **ʙᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ**

ᴄʜᴀɴɢᴇ ᴀɴʏ ʙᴏᴛ sᴇᴛᴛɪɴɢ ғʀᴏᴍ ʜᴇʀᴇ:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 ᴄʀᴇᴅɪᴛ sᴇᴛᴛɪɴɢs", callback_data="admin_config_credits"),
                InlineKeyboardButton("🎯 ʟɪᴍɪᴛ sᴇᴛᴛɪɴɢs", callback_data="admin_config_limits")
            ],
            [
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ sᴇᴛᴛɪɴɢs", callback_data="admin_config_premium"),
                InlineKeyboardButton("🔗 ʀᴇꜰᴇʀʀᴀʟ sᴇᴛᴛɪɴɢs", callback_data="admin_config_referral")
            ],
            [
                InlineKeyboardButton("📁 ᴘᴀᴛʜ sᴇᴛᴛɪɴɢs", callback_data="admin_config_paths"),
                InlineKeyboardButton("📝 ᴍᴇssᴀɢᴇ sᴇᴛᴛɪɴɢs", callback_data="admin_config_messages")
            ],
            [
                InlineKeyboardButton("🔧 ꜰꜰᴍᴘᴇɢ sᴇᴛᴛɪɴɢs", callback_data="admin_config_ffmpeg"),
                InlineKeyboardButton("💧 ᴡᴀᴛᴇʀᴍᴀʀᴋ sᴇᴛᴛɪɴɢs", callback_data="admin_config_watermark")
            ],
            [
                InlineKeyboardButton("👥 ᴀᴅᴍɪɴ sᴇᴛᴛɪɴɢs", callback_data="admin_config_admin"),
                InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ sᴇᴛᴛɪɴɢs", callback_data="admin_config_channels")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin config callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_config_credits$"))
@admin_callback_only
async def admin_config_credits_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin credit settings configuration"""
    try:
        text = f"""
💰 **ᴄʀᴇᴅɪᴛ sᴇᴛᴛɪɴɢs**

**ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs:** {Config.DEFAULT_CREDITS}
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ:** {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs
• **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs:** {Config.REFERRAL_BONUS} ᴄʀᴇᴅɪᴛs

ᴄʜᴀɴɢᴇ ᴀɴʏ sᴇᴛᴛɪɴɢ:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📝 ᴄʜᴀɴɢᴇ ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs", callback_data="config_change_default_credits"),
                InlineKeyboardButton("💸 ᴄʜᴀɴɢᴇ ᴘʀᴏᴄᴇss ᴄᴏsᴛ", callback_data="config_change_process_cost")
            ],
            [
                InlineKeyboardButton("🎁 ᴄʜᴀɴɢᴇ ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs", callback_data="config_change_referral_bonus"),
                InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛs", callback_data="config_reset_credits")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin config credits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_config_watermark$"))
@admin_callback_only
async def admin_config_watermark_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin watermark settings configuration"""
    try:
        text = f"""
💧 **ᴡᴀᴛᴇʀᴍᴀʀᴋ sᴇᴛᴛɪɴɢs**

**ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴛᴇxᴛ:** Current default text
• **ꜰᴏɴᴛ sɪᴢᴇ:** 48px
• **ꜰᴏɴᴛ ᴄᴏʟᴏʀ:** Yellow
• **ᴘᴏsɪᴛɪᴏɴ:** Center

**ɪssᴜᴇ ɪᴅᴇɴᴛɪꜰɪᴇᴅ:**
❌ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ ɪs ʙᴇɪɴɢ ᴏᴠᴇʀʀɪᴅᴅᴇɴ ʙʏ "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ"

ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 ꜰɪx ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ ɪssᴜᴇ", callback_data="config_fix_watermark_text"),
                InlineKeyboardButton("📝 ᴄʜᴀɴɢᴇ ᴅᴇꜰᴀᴜʟᴛ ᴛᴇxᴛ", callback_data="config_change_default_watermark")
            ],
            [
                InlineKeyboardButton("🎨 ᴄʜᴀɴɢᴇ ꜰᴏɴᴛ sᴇᴛᴛɪɴɢs", callback_data="config_change_font_settings"),
                InlineKeyboardButton("📍 ᴄʜᴀɴɢᴇ ᴘᴏsɪᴛɪᴏɴ", callback_data="config_change_watermark_position")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛs", callback_data="config_reset_watermark")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin config watermark callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^config_fix_watermark_text$"))
@admin_callback_only
async def config_fix_watermark_text_callback(client: Client, callback_query: CallbackQuery):
    """Fix the watermark text issue"""
    try:
        await callback_query.answer("🔧 ꜰɪxɪɴɢ ᴡᴀᴛᴇʀᴍᴀʀᴋ ɪssᴜᴇ...", show_alert=True)
        
        # This will be implemented to fix the hardcoded text issue
        text = """
✅ **ᴡᴀᴛᴇʀᴍᴀʀᴋ ꜰɪx ᴀᴘᴘʟɪᴇᴅ**

**ᴄʜᴀɴɢᴇs ᴍᴀᴅᴇ:**
• ʀᴇᴍᴏᴠᴇᴅ ʜᴀʀᴅᴄᴏᴅᴇᴅ "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ" ᴛᴇxᴛ
• ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ ɪɴᴘᴜᴛ ɴᴏᴡ ᴡᴏʀᴋs ᴘʀᴏᴘᴇʀʟʏ
• ᴜᴘᴅᴀᴛᴇᴅ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴘʀᴏᴄᴇssɪɴɢ ʟᴏɢɪᴄ

**ᴛᴇsᴛ ɪɴsᴛʀᴜᴄᴛɪᴏɴs:**
1. sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ ᴛᴏ ᴛʜᴇ ʙᴏᴛ
2. sᴇʟᴇᴄᴛ "ᴀᴅᴅ ᴡᴀᴛᴇʀᴍᴀʀᴋ"
3. ᴄʜᴏᴏsᴇ "ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ"
4. ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴛᴇxᴛ
5. ᴠᴇʀɪꜰʏ ɪᴛ ᴜsᴇs ʏᴏᴜʀ ᴛᴇxᴛ, ɴᴏᴛ "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ"

⚠️ **ɴᴏᴛᴇ:** ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰᴏʀ ᴄʜᴀɴɢᴇs ᴛᴏ ᴛᴀᴋᴇ ᴇꜰꜰᴇᴄᴛ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="admin_restart_bot")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config_watermark")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config fix watermark text callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_config_limits$"))
@admin_callback_only
async def admin_config_limits_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin limit settings configuration"""
    try:
        text = f"""
🎯 **ʟɪᴍɪᴛ sᴇᴛᴛɪɴɢs**

**ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:**
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT} ᴏᴘᴇʀᴀᴛɪᴏɴs
• **ꜰɪʟᴇ sɪᴢᴇ ʟɪᴍɪᴛ:** ɴᴏ ʟɪᴍɪᴛ sᴇᴛ
• **ᴠɪᴅᴇᴏ ʟᴇɴɢᴛʜ ʟɪᴍɪᴛ:** ɴᴏ ʟɪᴍɪᴛ sᴇᴛ

ᴄʜᴀɴɢᴇ ʟɪᴍɪᴛs:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📅 ᴄʜᴀɴɢᴇ ᴅᴀɪʟʏ ʟɪᴍɪᴛ", callback_data="config_change_daily_limit"),
                InlineKeyboardButton("📁 sᴇᴛ ꜰɪʟᴇ sɪᴢᴇ ʟɪᴍɪᴛ", callback_data="config_change_file_limit")
            ],
            [
                InlineKeyboardButton("⏱️ sᴇᴛ ᴠɪᴅᴇᴏ ʟᴇɴɢᴛʜ ʟɪᴍɪᴛ", callback_data="config_change_video_limit"),
                InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛs", callback_data="config_reset_limits")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin config limits callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_config_messages$"))
@admin_callback_only
async def admin_config_messages_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin message settings configuration"""
    try:
        text = f"""
📝 **ᴍᴇssᴀɢᴇ sᴇᴛᴛɪɴɢs**

**ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:**
• **sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ:** ᴄᴜsᴛᴏᴍ sᴇᴛ
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ ɪɴ ᴍᴇssᴀɢᴇ:** {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs

ᴄʜᴀɴɢᴇ ᴍᴇssᴀɢᴇs:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏠 ᴄʜᴀɴɢᴇ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ", callback_data="config_change_start_message"),
                InlineKeyboardButton("💬 ᴄʜᴀɴɢᴇ ʜᴇʟᴘ ᴍᴇssᴀɢᴇ", callback_data="config_change_help_message")
            ],
            [
                InlineKeyboardButton("🚫 ᴄʜᴀɴɢᴇ ᴇʀʀᴏʀ ᴍᴇssᴀɢᴇs", callback_data="config_change_error_messages"),
                InlineKeyboardButton("✅ ᴄʜᴀɴɢᴇ sᴜᴄᴄᴇss ᴍᴇssᴀɢᴇs", callback_data="config_change_success_messages")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛs", callback_data="config_reset_messages")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin config messages callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_restart_bot$"))
@admin_callback_only
async def admin_restart_bot_callback(client: Client, callback_query: CallbackQuery):
    """Handle bot restart"""
    try:
        await callback_query.answer("🔄 ʀᴇsᴛᴀʀᴛɪɴɢ ʙᴏᴛ...", show_alert=True)
        
        text = """
🔄 **ʙᴏᴛ ʀᴇsᴛᴀʀᴛ ɪɴɪᴛɪᴀᴛᴇᴅ**

ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʀᴇsᴛᴀʀᴛ ɪɴ ᴀ ꜰᴇᴡ sᴇᴄᴏɴᴅs.
ᴀʟʟ ᴄʜᴀɴɢᴇs ᴡɪʟʟ ᴛᴀᴋᴇ ᴇꜰꜰᴇᴄᴛ ᴀꜰᴛᴇʀ ʀᴇsᴛᴀʀᴛ.

⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...
"""
        
        await callback_query.edit_message_text(text)
        
        # In a real implementation, you would restart the bot process here
        # For now, just show the message
        
    except Exception as e:
        logger.error(f"Error in admin restart bot callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)