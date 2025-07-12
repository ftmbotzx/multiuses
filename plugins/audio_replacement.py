from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import logging

logger = logging.getLogger(__name__)

async def handle_audio_replacement_selection(client: Client, callback_query: CallbackQuery):
    """Handle audio replacement selection from custom callbacks"""
    try:
        # Handle audio replacement selection
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        if data.startswith("replace_audio_custom_"):
            # Store request for audio file upload
            from plugins.file_uploads import audio_replace_requests
            message_id = int(data.split("_")[-1])
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            audio_replace_requests[user_id] = {
                "type": "audio_replacement",
                "video_message": video_message
            }
            
            await callback_query.edit_message_text(
                f"🎵 **ʀᴇᴘʟᴀᴄᴇ ᴀᴜᴅɪᴏ**\n\n"
                f"📤 sᴇɴᴅ ᴛʜᴇ ᴀᴜᴅɪᴏ ꜰɪʟᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴀᴜᴅɪᴏ ᴡɪᴛʜ:\n\n"
                f"**ꜱᴜᴘᴘᴏʀᴛᴇᴅ ꜰᴏʀᴍᴀᴛꜱ:** MP3, M4A, WAV, FLAC\n\n"
                f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
            )
        
    except Exception as e:
        logger.error(f"Error in audio replacement selection: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)