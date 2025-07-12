from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
from .admin_utils import admin_only
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.command("logs") & filters.private)
@admin_only
async def view_logs_command(client: Client, message: Message):
    """Handle /logs command"""
    try:
        # Get recent operations
        recent_ops = await db.operations.find({}).sort("date", -1).limit(10).to_list(None)
        
        if not recent_ops:
            await message.reply_text("📋 **ɴᴏ ʀᴇᴄᴇɴᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs**")
            return
        
        logs_text = "📋 **ʀᴇᴄᴇɴᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs**\n\n"
        
        for op in recent_ops:
            user_id = op.get("user_id")
            operation_type = op.get("operation_type")
            status = op.get("status")
            date = op.get("date")
            
            status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
            
            logs_text += f"{status_emoji} **{operation_type}**\n"
            logs_text += f"   ᴜsᴇʀ: `{user_id}`\n"
            logs_text += f"   ᴅᴀᴛᴇ: {date.strftime('%d/%m %H:%M')}\n\n"
        
        await message.reply_text(logs_text)
        
    except Exception as e:
        logger.error(f"Error in logs command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ʟᴏɢs.")