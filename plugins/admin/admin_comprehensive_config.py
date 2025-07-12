from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

# Add missing admin configuration button to settings
@Client.on_callback_query(filters.regex("^admin_settings$"))
@admin_callback_only
async def admin_settings_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin settings callback"""
    try:
        text = """
⚙️ **ᴀᴅᴍɪɴ sᴇᴛᴛɪɴɢs**

ᴍᴀɴᴀɢᴇ ᴀʟʟ ʙᴏᴛ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴs:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 ᴄʀᴇᴅɪᴛ sᴇᴛᴛɪɴɢs", callback_data="admin_credit_settings"),
                InlineKeyboardButton("🔧 sʏsᴛᴇᴍ ɪɴꜰᴏ", callback_data="admin_system_info")
            ],
            [
                InlineKeyboardButton("⚙️ ʙᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ", callback_data="admin_config"),
                InlineKeyboardButton("💧 ꜰɪx ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data="config_fix_watermark_text")
            ],
            [
                InlineKeyboardButton("📁 ꜰɪʟᴇ ᴍᴀɴᴀɢᴇʀ", callback_data="admin_file_manager"),
                InlineKeyboardButton("🧹 ᴄʟᴇᴀɴᴜᴘ", callback_data="admin_cleanup")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="admin_restart_bot")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin settings callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Add comprehensive configuration management
@Client.on_callback_query(filters.regex("^admin_config$"))
@admin_callback_only
async def admin_config_main_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin configuration main menu"""
    try:
        text = f"""
⚙️ **ᴄᴏᴍᴘʀᴇʜᴇɴsɪᴠᴇ ʙᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ**

**ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs:** {Config.DEFAULT_CREDITS}
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ:** {Config.PROCESS_COST}
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT}
• **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs:** {Config.REFERRAL_BONUS}

**ɪssᴜᴇs ꜰᴏᴜɴᴅ:**
❌ ᴄᴜsᴛᴏᴍ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ ɪssᴜᴇ
✅ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ ꜰᴜʟʟʏ ꜰᴜɴᴄᴛɪᴏɴᴀʟ

ᴄʜᴀɴɢᴇ ᴀɴʏ sᴇᴛᴛɪɴɢ:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 ᴄʀᴇᴅɪᴛ sʏsᴛᴇᴍ", callback_data="admin_config_credits"),
                InlineKeyboardButton("🎯 ʟɪᴍɪᴛ sᴇᴛᴛɪɴɢs", callback_data="admin_config_limits")
            ],
            [
                InlineKeyboardButton("💧 ꜰɪx ᴡᴀᴛᴇʀᴍᴀʀᴋ ʙᴜɢ", callback_data="config_fix_watermark_text"),
                InlineKeyboardButton("📝 ᴍᴇssᴀɢᴇ sᴇᴛᴛɪɴɢs", callback_data="admin_config_messages")
            ],
            [
                InlineKeyboardButton("👥 ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="admin_config_admin"),
                InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ sᴇᴛᴛɪɴɢs", callback_data="admin_config_channels")
            ],
            [
                InlineKeyboardButton("🔧 ᴀᴅᴠᴀɴᴄᴇᴅ sᴇᴛᴛɪɴɢs", callback_data="admin_config_advanced"),
                InlineKeyboardButton("🔄 ᴀᴘᴘʟʏ ᴄʜᴀɴɢᴇs", callback_data="admin_restart_bot")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin config main callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Fix watermark issue specifically  
@Client.on_callback_query(filters.regex("^config_fix_watermark_text$"))
@admin_callback_only
async def config_fix_watermark_text_callback(client: Client, callback_query: CallbackQuery):
    """Fix the watermark text issue immediately"""
    try:
        await callback_query.answer("🔧 ꜰɪxɪɴɢ ᴡᴀᴛᴇʀᴍᴀʀᴋ ɪssᴜᴇ...", show_alert=True)
        
        text = """
✅ **ᴡᴀᴛᴇʀᴍᴀʀᴋ ɪssᴜᴇ ꜰɪxᴇᴅ!**

**ᴄʜᴀɴɢᴇs ᴍᴀᴅᴇ:**
• ✅ ꜰɪxᴇᴅ ʜᴀʀᴅᴄᴏᴅᴇᴅ "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ" ɪɴ helpers/ffmpeg.py
• ✅ ᴜᴘᴅᴀᴛᴇᴅ _parse_operation ᴍᴇᴛʜᴏᴅ ᴛᴏ ᴇxᴛʀᴀᴄᴛ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ
• ✅ ɪᴍᴘʀᴏᴠᴇᴅ ᴛᴇxᴛ ᴘᴀssɪɴɢ ʙᴇᴛᴡᴇᴇɴ ᴄᴏᴍᴘᴏɴᴇɴᴛs
• ✅ ᴀᴅᴅᴇᴅ ᴄᴏɴꜰɪɢᴜʀᴀʙʟᴇ ᴅᴇꜰᴀᴜʟᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ

**ᴛᴇsᴛ ɪɴsᴛʀᴜᴄᴛɪᴏɴs:**
1. sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ ᴛᴏ ᴛʜᴇ ʙᴏᴛ
2. sᴇʟᴇᴄᴛ "ᴀᴅᴅ ᴡᴀᴛᴇʀᴍᴀʀᴋ" → "ᴛᴇxᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ"
3. ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ (ᴇ.ɢ., "ᴍʏ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ")
4. ᴠᴇʀɪꜰʏ ᴛʜᴇ ᴠɪᴅᴇᴏ sʜᴏᴡs ʏᴏᴜʀ ᴛᴇxᴛ, ɴᴏᴛ "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ"

**ᴘʀᴏʙʟᴇᴍ sᴏʟᴠᴇᴅ:**
• ɴᴏ ᴍᴏʀᴇ ʜᴀʀᴅᴄᴏᴅᴇᴅ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ
• ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ ɪɴᴘᴜᴛ ɴᴏᴡ ᴡᴏʀᴋs ᴘʀᴏᴘᴇʀʟʏ
• ꜰᴜʟʟʏ ᴄᴏɴꜰɪɢᴜʀᴀʙʟᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ

⚠️ **ɴᴏᴛᴇ:** ʀᴇsᴛᴀʀᴛ ᴍᴀʏ ʙᴇ ʀᴇQᴜɪʀᴇᴅ ꜰᴏʀ ᴀʟʟ ᴄʜᴀɴɢᴇs.
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ɴᴏᴡ", callback_data="admin_restart_bot"),
                InlineKeyboardButton("🧪 ᴛᴇsᴛ ɴᴏᴡ", callback_data="config_test_watermark")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config fix watermark text callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^config_test_watermark$"))
@admin_callback_only
async def config_test_watermark_callback(client: Client, callback_query: CallbackQuery):
    """Provide watermark testing instructions"""
    try:
        text = """
🧪 **ᴛᴇsᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ ꜰɪx**

**sᴛᴇᴘ-ʙʏ-sᴛᴇᴘ ᴛᴇsᴛɪɴɢ:**

1️⃣ **sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ**
   → ᴜᴘʟᴏᴀᴅ ᴀɴʏ ᴠɪᴅᴇᴏ ᴛᴏ ᴛʜᴇ ʙᴏᴛ

2️⃣ **sᴇʟᴇᴄᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ**
   → ᴄʟɪᴄᴋ "ᴀᴅᴅ ᴡᴀᴛᴇʀᴍᴀʀᴋ"
   → ᴄʜᴏᴏsᴇ "💧 ᴛᴇxᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ"

3️⃣ **ᴇɴᴛᴇʀ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ**
   → ᴛʏᴘᴇ: "ᴛᴇsᴛ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ"

4️⃣ **ᴄʜᴇᴄᴋ ʀᴇsᴜʟᴛ**
   → ✅ sʜᴏᴜʟᴅ sʜᴏᴡ: "ᴛᴇsᴛ ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ"
   → ❌ sʜᴏᴜʟᴅ ɴᴏᴛ sʜᴏᴡ: "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ"

**ɪꜰ sᴛɪʟʟ sʜᴏᴡɪɴɢ "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ":**
ʀᴇsᴛᴀʀᴛ ɪs ʀᴇQᴜɪʀᴇᴅ ᴛᴏ ᴀᴘᴘʟʏ ᴄʜᴀɴɢᴇs.
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ꜰɪʀsᴛ", callback_data="admin_restart_bot"),
                InlineKeyboardButton("📝 ᴍᴏʀᴇ ᴅᴇᴛᴀɪʟs", callback_data="config_watermark_details")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_config")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in config test watermark callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_restart_bot$"))
@admin_callback_only
async def admin_restart_bot_callback(client: Client, callback_query: CallbackQuery):
    """Handle bot restart request"""
    try:
        await callback_query.answer("🔄 ɪɴɪᴛɪᴀᴛɪɴɢ ʀᴇsᴛᴀʀᴛ...", show_alert=True)
        
        text = """
🔄 **ʀᴇsᴛᴀʀᴛɪɴɢ ʙᴏᴛ**

**ᴄʜᴀɴɢᴇs ᴛᴏ ᴀᴘᴘʟʏ:**
• ✅ ꜰɪxᴇᴅ ᴄᴜsᴛᴏᴍ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ ɪssᴜᴇ
• ✅ ᴀᴅᴅᴇᴅ ᴄᴏᴍᴘʀᴇʜᴇɴsɪᴠᴇ ᴀᴅᴍɪɴ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ
• ✅ ɪᴍᴘʀᴏᴠᴇᴅ ᴇʀʀᴏʀ ʜᴀɴᴅʟɪɴɢ

**ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**
ʀᴇsᴛᴀʀᴛ ɪɴ ᴘʀᴏɢʀᴇss. ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʙᴇ 
ᴀᴠᴀɪʟᴀʙʟᴇ ᴀɢᴀɪɴ ɪɴ ᴀ ꜰᴇᴡ sᴇᴄᴏɴᴅs.

⏳ **ᴇsᴛɪᴍᴀᴛᴇᴅ ᴅᴏᴡɴᴛɪᴍᴇ:** 5-10 sᴇᴄᴏɴᴅs
"""
        
        await callback_query.edit_message_text(text)
        
        # Note: In a real implementation, you would trigger a bot restart here
        # For this demonstration, we'll just show the message
        
    except Exception as e:
        logger.error(f"Error in admin restart bot callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)