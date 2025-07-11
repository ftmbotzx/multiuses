from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

# Store watermark requests
watermark_requests = {}

@Client.on_callback_query(filters.regex(r"^watermark_"))
async def handle_watermark_callback(client: Client, callback_query: CallbackQuery):
    """Handle watermark type selection callbacks"""
    try:
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        # Parse callback data: watermark_type_messageid
        parts = data.split("_")
        if len(parts) >= 3:
            watermark_type = parts[1]
            message_id = int(parts[2])
            
            # Get video message
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            if watermark_type == "text":
                # Store request for text input
                watermark_requests[user_id] = {
                    "type": "text_watermark",
                    "video_message": video_message
                }
                
                await callback_query.edit_message_text(
                    f"💧 **ᴛᴇxᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ**\n\n"
                    f"📝 sᴇɴᴅ ᴛʜᴇ ᴛᴇxᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴀs ᴡᴀᴛᴇʀᴍᴀʀᴋ:\n\n"
                    f"**ᴇxᴀᴍᴘʟᴇ:** `@YourChannel` ᴏʀ `Your Name`\n\n"
                    f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"back_to_options_{video_message.id}")
                    ]])
                )
                
            elif watermark_type == "image":
                # Store request for image upload
                from plugins.file_uploads import watermark_image_requests
                watermark_image_requests[user_id] = {
                    "type": "image_watermark",
                    "video_message": video_message
                }
                
                await callback_query.edit_message_text(
                    f"🖼️ **ɪᴍᴀɢᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ**\n\n"
                    f"📤 sᴇɴᴅ ᴛʜᴇ ɪᴍᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴀs ᴡᴀᴛᴇʀᴍᴀʀᴋ:\n\n"
                    f"**sᴜᴘᴘᴏʀᴛᴇᴅ:** JPG, PNG, WebP\n\n"
                    f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"back_to_options_{video_message.id}")
                    ]])
                )
        
    except Exception as e:
        logger.error(f"Error in watermark callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

async def handle_watermark_selection(client: Client, callback_query: CallbackQuery):
    """Handle watermark selection from custom callbacks"""
    await handle_watermark_callback(client, callback_query)