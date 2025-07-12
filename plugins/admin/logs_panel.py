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