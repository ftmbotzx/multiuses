from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.video_handler import watermark_requests, merge_collections, screenshot_requests, trim_requests
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    """Handle /cancel command"""
    try:
        user_id = message.from_user.id
        
        # Check if user has pending watermark request
        if user_id in watermark_requests:
            request_type = watermark_requests[user_id]["type"]
            del watermark_requests[user_id]
            await message.reply_text(
                f"❌ **ᴄᴀɴᴄᴇʟʟᴇᴅ**\n\n"
                f"ʏᴏᴜʀ {request_type.replace('_', ' ')} ᴡᴀᴛᴇʀᴍᴀʀᴋ ʀᴇǫᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ."
            )
            return
        
        # Check if user has pending merge collection
        if user_id in merge_collections:
            del merge_collections[user_id]
            await message.reply_text(
                f"❌ **ᴄᴀɴᴄᴇʟʟᴇᴅ**\n\n"
                f"ʏᴏᴜʀ ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ."
            )
            return
        
        # Check if user has pending screenshot request
        if user_id in screenshot_requests:
            request_type = screenshot_requests[user_id]["type"]
            del screenshot_requests[user_id]
            await message.reply_text(
                f"❌ **ᴄᴀɴᴄᴇʟʟᴇᴅ**\n\n"
                f"ʏᴏᴜʀ {request_type.replace('_', ' ')} sᴄʀᴇᴇɴsʜᴏᴛ ʀᴇǫᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ."
            )
            return
        
        # Check if user has pending trim request
        if user_id in trim_requests:
            request_type = trim_requests[user_id]["type"]
            del trim_requests[user_id]
            await message.reply_text(
                f"❌ **ᴄᴀɴᴄᴇʟʟᴇᴅ**\n\n"
                f"ʏᴏᴜʀ {request_type.replace('_', ' ')} ᴛʀɪᴍ ʀᴇǫᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ."
            )
            return
        
        # No pending operations
        await message.reply_text(
            f"ℹ️ **ɴᴏ ᴀᴄᴛɪᴠᴇ ᴏᴘᴇʀᴀᴛɪᴏɴs**\n\n"
            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘᴇɴᴅɪɴɢ ᴏᴘᴇʀᴀᴛɪᴏɴs ᴛᴏ ᴄᴀɴᴄᴇʟ."
        )
        
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴄᴀɴᴄᴇʟʟɪɴɢ ᴏᴘᴇʀᴀᴛɪᴏɴ.")