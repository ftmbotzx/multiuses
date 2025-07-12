from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import logging

logger = logging.getLogger(__name__)

async def handle_subtitle_selection(client: Client, callback_query: CallbackQuery):
    """Handle subtitle selection from custom callbacks"""
    try:
        # Handle subtitle type selection
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        if data.startswith("subtitles_custom_"):
            # Store request for subtitle file upload
            from plugins.file_uploads import subtitle_requests
            message_id = int(data.split("_")[-1])
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            subtitle_requests[user_id] = {
                "type": "custom_subtitle",
                "video_message": video_message
            }
            
            await callback_query.edit_message_text(
                f"📄 **ᴄᴜsᴛᴏᴍ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ**\n\n"
                f"📤 sᴇɴᴅ ʏᴏᴜʀ .sʀᴛ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ:\n\n"
                f"**ꜱᴜᴘᴘᴏʀᴛᴇᴅ:** .srt files only\n\n"
                f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
            )
        
    except Exception as e:
        logger.error(f"Error in subtitle selection: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)