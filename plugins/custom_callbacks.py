from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

# Store requests for custom inputs
trim_requests = {}
screenshot_requests = {}

@Client.on_callback_query(filters.regex(r"^process_trim_custom_"))
async def handle_trim_custom(client: Client, callback_query: CallbackQuery):
    """Handle custom trim time input"""
    try:
        message_id = int(callback_query.data.split("_")[-1])
        user_id = callback_query.from_user.id
        
        # Get video message
        video_message = await client.get_messages(callback_query.message.chat.id, message_id)
        
        # Store trim request
        trim_requests[user_id] = {
            "type": "custom_trim",
            "video_message": video_message
        }
        
        await callback_query.edit_message_text(
            f"✂️ **ᴄᴜsᴛᴏᴍ ᴛʀɪᴍ ᴅᴜʀᴀᴛɪᴏɴ**\n\n"
            f"**ᴏʀɪɢɪɴᴀʟ ᴅᴜʀᴀᴛɪᴏɴ:** {video_message.video.duration // 60}:{video_message.video.duration % 60:02d}\n\n"
            f"📝 sᴇɴᴅ ᴛʜᴇ ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs (ᴇ.ɢ., `120` ꜰᴏʀ 2 ᴍɪɴᴜᴛᴇs)\n\n"
            f"ᴏʀ ᴜsᴇ ᴍᴍ:ss ꜰᴏʀᴍᴀᴛ (ᴇ.ɢ., `2:30` ꜰᴏʀ 2 ᴍɪɴᴜᴛᴇs 30 sᴇᴄᴏɴᴅs)\n\n"
            f"**ᴍᴀx ᴅᴜʀᴀᴛɪᴏɴ:** {video_message.video.duration}s\n\n"
            f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"back_to_options_{video_message.id}")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in trim custom callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex(r"^screenshot_custom_"))
async def handle_screenshot_custom(client: Client, callback_query: CallbackQuery):
    """Handle custom screenshot time input"""
    try:
        message_id = int(callback_query.data.split("_")[-1])
        user_id = callback_query.from_user.id
        
        # Get video message
        video_message = await client.get_messages(callback_query.message.chat.id, message_id)
        
        # Store screenshot request
        screenshot_requests[user_id] = {
            "type": "custom_screenshot",
            "video_message": video_message
        }
        
        await callback_query.edit_message_text(
            f"📸 **ᴄᴜsᴛᴏᴍ sᴄʀᴇᴇɴsʜᴏᴛ ᴛɪᴍᴇ**\n\n"
            f"**ᴠɪᴅᴇᴏ ᴅᴜʀᴀᴛɪᴏɴ:** {video_message.video.duration // 60}:{video_message.video.duration % 60:02d}\n\n"
            f"📝 sᴇɴᴅ ᴛʜᴇ ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs (ᴇ.ɢ., `30` ꜰᴏʀ 30sᴇᴄᴏɴᴅs)\n\n"
            f"ᴏʀ ᴜsᴇ ᴍᴍ:ss ꜰᴏʀᴍᴀᴛ (ᴇ.ɢ., `1:30` ꜰᴏʀ 1 ᴍɪɴᴜᴛᴇ 30 sᴇᴄᴏɴᴅs)\n\n"
            f"**ᴍᴀx ᴛɪᴍᴇ:** {video_message.video.duration}s\n\n"
            f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"back_to_options_{video_message.id}")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error in screenshot custom callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex(r"^(watermark|subtitles|replace_audio)_"))
async def handle_custom_type_callbacks(client: Client, callback_query: CallbackQuery):
    """Handle watermark, subtitles, and replace audio callbacks"""
    try:
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        if data.startswith("watermark_"):
            from plugins.watermark_handler import handle_watermark_selection
            await handle_watermark_selection(client, callback_query)
        elif data.startswith("subtitles_"):
            from plugins.subtitle_handler import handle_subtitle_selection
            await handle_subtitle_selection(client, callback_query)
        elif data.startswith("replace_audio_"):
            from plugins.audio_replacement import handle_audio_replacement_selection
            await handle_audio_replacement_selection(client, callback_query)
        
    except Exception as e:
        logger.error(f"Error in custom type callbacks: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)