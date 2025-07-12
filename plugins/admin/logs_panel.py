from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_logs$"))
@admin_callback_only
async def admin_logs_panel(client: Client, callback_query: CallbackQuery):
    """Logs panel"""
    try:
            
        # Get recent operations
        recent_ops = await db.operations.find({}).sort("date", -1).limit(10).to_list(None) if db.operations is not None else []
        
        text = "📋 **ʀᴇᴄᴇɴᴛ ᴀᴄᴛɪᴠɪᴛʏ**\n\n"
        
        if recent_ops:
            for i, op in enumerate(recent_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                status = op.get("status", "Unknown")
                date = op.get("date", datetime.now())
                
                status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                
                text += f"`{i}.` {status_emoji} **{operation_type}** - ᴜsᴇʀ: `{user_id}`\n"
                text += f"    📅 {date.strftime('%d/%m %H:%M')}\n\n"
        else:
            text += "ɴᴏ ʀᴇᴄᴇɴᴛ ᴀᴄᴛɪᴠɪᴛʏ ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 ꜰᴜʟʟ ʟᴏɢs", callback_data="admin_full_logs"),
                InlineKeyboardButton("🔍 ꜰɪʟᴛᴇʀ", callback_data="admin_filter_logs")
            ],
            [
                InlineKeyboardButton("❌ ᴇʀʀᴏʀs", callback_data="admin_error_logs"),
                InlineKeyboardButton("✅ sᴜᴄᴄᴇss", callback_data="admin_success_logs")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="admin_logs"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin logs panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Add missing logs panel callbacks
@Client.on_callback_query(filters.regex("^admin_full_logs$"))
@admin_callback_only
async def admin_full_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle full logs callback"""
    try:
        # Get more operations
        recent_ops = await db.operations.find({}).sort("date", -1).limit(50).to_list(None) if db.operations is not None else []
        
        text = "📊 **ꜰᴜʟʟ ᴀᴄᴛɪᴠɪᴛʏ ʟᴏɢs**\n\n"
        
        if recent_ops:
            for i, op in enumerate(recent_ops, 1):
                if i > 20:  # Limit to 20 for message length
                    break
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                status = op.get("status", "Unknown")
                date = op.get("date", datetime.now())
                
                status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                
                text += f"`{i}.` {status_emoji} **{operation_type}** - `{user_id}` - {date.strftime('%d/%m %H:%M')}\n"
        else:
            text += "ɴᴏ ᴀᴄᴛɪᴠɪᴛʏ ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_logs")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in full logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_filter_logs$"))
@admin_callback_only
async def admin_filter_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle filter logs callback"""
    try:
        text = """
🔍 **ꜰɪʟᴛᴇʀ ʟᴏɢs**

ᴄʜᴏᴏsᴇ ᴀ ꜰɪʟᴛᴇʀ ᴏᴘᴛɪᴏɴ:
"""
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ sᴜᴄᴄᴇss", callback_data="admin_success_logs"),
                InlineKeyboardButton("❌ ᴇʀʀᴏʀs", callback_data="admin_error_logs")
            ],
            [
                InlineKeyboardButton("⏳ ᴘᴇɴᴅɪɴɢ", callback_data="admin_pending_logs"),
                InlineKeyboardButton("📅 ᴛᴏᴅᴀʏ", callback_data="admin_today_logs")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_logs")
            ]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in filter logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_error_logs$"))
@admin_callback_only
async def admin_error_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle error logs callback"""
    try:
        # Get failed operations
        error_ops = await db.operations.find({"status": "failed"}).sort("date", -1).limit(20).to_list(None) if db.operations is not None else []
        
        text = "❌ **ᴇʀʀᴏʀ ʟᴏɢs**\n\n"
        
        if error_ops:
            for i, op in enumerate(error_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                date = op.get("date", datetime.now())
                error_message = op.get("error_message", "Unknown error")
                
                text += f"`{i}.` ❌ **{operation_type}** - `{user_id}`\n"
                text += f"    📅 {date.strftime('%d/%m %H:%M')}\n"
                text += f"    💬 {error_message[:50]}...\n\n"
        else:
            text += "ɴᴏ ᴇʀʀᴏʀ ʟᴏɢs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_logs")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in error logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_success_logs$"))
@admin_callback_only
async def admin_success_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle success logs callback"""
    try:
        # Get successful operations
        success_ops = await db.operations.find({"status": "completed"}).sort("date", -1).limit(20).to_list(None) if db.operations is not None else []
        
        text = "✅ **sᴜᴄᴄᴇssꜰᴜʟ ᴏᴘᴇʀᴀᴛɪᴏɴs**\n\n"
        
        if success_ops:
            for i, op in enumerate(success_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                date = op.get("date", datetime.now())
                
                text += f"`{i}.` ✅ **{operation_type}** - `{user_id}` - {date.strftime('%d/%m %H:%M')}\n"
        else:
            text += "ɴᴏ sᴜᴄᴄᴇssꜰᴜʟ ᴏᴘᴇʀᴀᴛɪᴏɴs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_logs")]
        ])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in success logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)