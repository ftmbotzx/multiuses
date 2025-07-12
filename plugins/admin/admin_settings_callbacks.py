from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
import os
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)
db = Database()

# Missing callback handlers for admin settings panel

@Client.on_callback_query(filters.regex("^admin_credit_settings$"))
@admin_callback_only
async def admin_credit_settings_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin credit settings callback"""
    try:
        text = f"""
💰 **ᴄʀᴇᴅɪᴛ sᴇᴛᴛɪɴɢs**

**ᴄᴜʀʀᴇɴᴛ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ:**
• **ᴅᴇꜰᴀᴜʟᴛ ᴄʀᴇᴅɪᴛs:** {Config.DEFAULT_CREDITS}
• **ᴘʀᴏᴄᴇss ᴄᴏsᴛ:** {Config.PROCESS_COST}
• **ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜs:** {Config.REFERRAL_BONUS}
• **ᴅᴀɪʟʏ ʟɪᴍɪᴛ:** {Config.DAILY_LIMIT}

**ɴᴏᴛᴇ:** ᴛʜᴇsᴇ sᴇᴛᴛɪɴɢs ᴀʀᴇ ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴠɪᴀ 
ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs ᴀɴᴅ ʀᴇQᴜɪʀᴇ ᴀ ʀᴇsᴛᴀʀᴛ ᴛᴏ ᴄʜᴀɴɢᴇ.

**ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs:**
• DEFAULT_CREDITS={Config.DEFAULT_CREDITS}
• PROCESS_COST={Config.PROCESS_COST}
• REFERRAL_BONUS={Config.REFERRAL_BONUS}
• DAILY_LIMIT={Config.DAILY_LIMIT}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin credit settings callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_system_info$"))
@admin_callback_only
async def admin_system_info_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin system info callback"""
    try:
        # Get Python and Pyrogram versions
        import pyrogram
        import sys
        
        if PSUTIL_AVAILABLE:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
                text = f"""
🔧 **sʏsᴛᴇᴍ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**

**sʏsᴛᴇᴍ ʀᴇsᴏᴜʀᴄᴇs:**
• **ᴄᴘᴜ ᴜsᴀɢᴇ:** {cpu_percent}%
• **ᴍᴇᴍᴏʀʏ:** {memory.percent}% ({memory.used // 1024**2}MB / {memory.total // 1024**2}MB)
• **ᴅɪsᴋ:** {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)

**sᴏꜰᴛᴡᴀʀᴇ:**
• **ᴘʏᴛʜᴏɴ:** {sys.version.split()[0]}
• **ᴘʏʀᴏɢʀᴀᴍ:** {pyrogram.__version__}
• **ᴏs:** {os.name}

**ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ:**
• **ᴅᴏᴡɴʟᴏᴀᴅs ᴅɪʀ:** {Config.DOWNLOADS_DIR}
• **ᴜᴘʟᴏᴀᴅs ᴅɪʀ:** {Config.UPLOADS_DIR}
• **ᴛᴇᴍᴘ ᴅɪʀ:** {Config.TEMP_DIR}

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
• **ᴛᴇᴍᴘ ᴅɪʀ:** {Config.TEMP_DIR}

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        else:
            text = f"""
🔧 **sʏsᴛᴇᴍ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**

**sʏsᴛᴇᴍ ʀᴇsᴏᴜʀᴄᴇs:**
• **sᴛᴀᴛᴜs:** ᴘsᴜᴛɪʟ ɴᴏᴡ ᴀᴠᴀɪʟᴀʙʟᴇ ✅

**sᴏꜰᴛᴡᴀʀᴇ:**
• **ᴘʏᴛʜᴏɴ:** {sys.version.split()[0]}
• **ᴘʏʀᴏɢʀᴀᴍ:** {pyrogram.__version__}
• **ᴏs:** {os.name}

**ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ:**
• **ᴅᴏᴡɴʟᴏᴀᴅs ᴅɪʀ:** {Config.DOWNLOADS_DIR}
• **ᴜᴘʟᴏᴀᴅs ᴅɪʀ:** {Config.UPLOADS_DIR}
• **ᴛᴇᴍᴘ ᴅɪʀ:** {Config.TEMP_DIR}

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
• **ᴛᴇᴍᴘ ᴅɪʀ:** {Config.TEMP_DIR}

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_system_info")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin system info callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_cleanup$"))
@admin_callback_only
async def admin_cleanup_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin cleanup callback"""
    try:
        import glob
        import shutil
        
        # Count files in directories
        downloads_count = len(glob.glob(f"{Config.DOWNLOADS_DIR}/*"))
        uploads_count = len(glob.glob(f"{Config.UPLOADS_DIR}/*"))
        temp_count = len(glob.glob(f"{Config.TEMP_DIR}/*"))
        
        # Calculate sizes
        def get_dir_size(path):
            try:
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                return total_size // 1024**2  # MB
            except:
                return 0
        
        downloads_size = get_dir_size(Config.DOWNLOADS_DIR)
        uploads_size = get_dir_size(Config.UPLOADS_DIR)
        temp_size = get_dir_size(Config.TEMP_DIR)
        
        text = f"""
🧹 **ꜰɪʟᴇ ᴄʟᴇᴀɴᴜᴘ**

**ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs:**
• **ᴅᴏᴡɴʟᴏᴀᴅs:** {downloads_count} ꜰɪʟᴇs ({downloads_size}MB)
• **ᴜᴘʟᴏᴀᴅs:** {uploads_count} ꜰɪʟᴇs ({uploads_size}MB)
• **ᴛᴇᴍᴘ:** {temp_count} ꜰɪʟᴇs ({temp_size}MB)

**ᴛᴏᴛᴀʟ:** {downloads_count + uploads_count + temp_count} ꜰɪʟᴇs ({downloads_size + uploads_size + temp_size}MB)

**ɴᴏᴛᴇ:** ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴄʟᴇᴀɴᴜᴘ ʀᴜɴs ᴇᴠᴇʀʏ 24 ʜᴏᴜʀs.
ꜰɪʟᴇs ᴏʟᴅᴇʀ ᴛʜᴀɴ 24 ʜᴏᴜʀs ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇᴍᴏᴠᴇᴅ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑️ ᴄʟᴇᴀɴ ɴᴏᴡ", callback_data="admin_cleanup_now")],
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_cleanup")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin cleanup callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_cleanup_now$"))
@admin_callback_only
async def admin_cleanup_now_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin cleanup now callback"""
    try:
        await callback_query.answer("🧹 sᴛᴀʀᴛɪɴɢ ᴄʟᴇᴀɴᴜᴘ...", show_alert=True)
        
        from helpers.downloader import FileCleanup
        
        # Cleanup files
        downloads_cleaned = FileCleanup.cleanup_directory(Config.DOWNLOADS_DIR, max_age_hours=24)
        uploads_cleaned = FileCleanup.cleanup_directory(Config.UPLOADS_DIR, max_age_hours=24)
        temp_cleaned = FileCleanup.cleanup_directory(Config.TEMP_DIR, max_age_hours=1)
        
        total_cleaned = downloads_cleaned + uploads_cleaned + temp_cleaned
        
        text = f"""
🧹 **ᴄʟᴇᴀɴᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**

**ʀᴇsᴜʟᴛs:**
• **ᴅᴏᴡɴʟᴏᴀᴅs:** {downloads_cleaned} ꜰɪʟᴇs ʀᴇᴍᴏᴠᴇᴅ
• **ᴜᴘʟᴏᴀᴅs:** {uploads_cleaned} ꜰɪʟᴇs ʀᴇᴍᴏᴠᴇᴅ
• **ᴛᴇᴍᴘ:** {temp_cleaned} ꜰɪʟᴇs ʀᴇᴍᴏᴠᴇᴅ

**ᴛᴏᴛᴀʟ ʀᴇᴍᴏᴠᴇᴅ:** {total_cleaned} ꜰɪʟᴇs

✅ **ᴄʟᴇᴀɴᴜᴘ sᴜᴄᴄᴇssꜰᴜʟ**
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_cleanup")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin cleanup now callback: {e}")
        await callback_query.answer("❌ ᴄʟᴇᴀɴᴜᴘ ꜰᴀɪʟᴇᴅ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_file_manager$"))
@admin_callback_only
async def admin_file_manager_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin file manager callback"""
    try:
        text = """
📁 **ꜰɪʟᴇ ᴍᴀɴᴀɢᴇʀ**

**ᴅɪʀᴇᴄᴛᴏʀɪᴇs:**
• **ᴅᴏᴡɴʟᴏᴀᴅs:** ᴛᴇᴍᴘᴏʀᴀʀʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜰɪʟᴇs
• **ᴜᴘʟᴏᴀᴅs:** ᴘʀᴏᴄᴇssᴇᴅ ꜰɪʟᴇs ʀᴇᴀᴅʏ ꜰᴏʀ ᴜᴘʟᴏᴀᴅ
• **ᴛᴇᴍᴘ:** ᴛᴇᴍᴘᴏʀᴀʀʏ ᴘʀᴏᴄᴇssɪɴɢ ꜰɪʟᴇs

**ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴄʟᴇᴀɴᴜᴘ:**
• ᴅᴏᴡɴʟᴏᴀᴅs/ᴜᴘʟᴏᴀᴅs: 24 ʜᴏᴜʀs
• ᴛᴇᴍᴘ: ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ᴀꜰᴛᴇʀ ᴘʀᴏᴄᴇssɪɴɢ

**ɴᴏᴛᴇ:** ꜰɪʟᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ɪs ᴀᴜᴛᴏᴍᴀᴛɪᴄ.
ᴍᴀɴᴜᴀʟ ɪɴᴛᴇʀᴠᴇɴᴛɪᴏɴ ɪs ʀᴀʀᴇʟʏ ɴᴇᴇᴅᴇᴅ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧹 ᴄʟᴇᴀɴᴜᴘ", callback_data="admin_cleanup")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin file manager callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_restart$"))
@admin_callback_only
async def admin_restart_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin restart callback"""
    try:
        text = """
🔄 **ʙᴏᴛ ʀᴇsᴛᴀʀᴛ**

ᴜsᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ:

**ᴄᴏᴍᴍᴀɴᴅ:** `/restart`

⚠️ **ᴡᴀʀɴɪɴɢ:** ᴛʜɪs ᴡɪʟʟ:
• sᴛᴏᴘ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴘʀᴏᴄᴇssɪɴɢ
• ᴄʟᴇᴀʀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴅᴀᴛᴀ
• ʀᴇʟᴏᴀᴅ ᴀʟʟ ᴘʟᴜɢɪɴs
• ʀᴇsᴇᴛ ᴀʟʟ ᴄᴏɴɴᴇᴄᴛɪᴏɴs

ᴜsᴇ ᴏɴʟʏ ᴡʜᴇɴ ɴᴇᴄᴇssᴀʀʏ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_settings")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin restart callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)