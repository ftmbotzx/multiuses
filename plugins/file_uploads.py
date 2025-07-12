import os
from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

# Store requests for file uploads - shared across modules
audio_replace_requests = {}
watermark_image_requests = {}
subtitle_requests = {}

@Client.on_message(filters.audio & filters.private)
async def handle_audio_upload(client: Client, message: Message):
    """Handle audio file uploads for replace audio operation"""
    try:
        user_id = message.from_user.id
        
        # Check if user has pending audio replace request
        if user_id in audio_replace_requests:
            request = audio_replace_requests[user_id]
            video_message = request["video_message"]
            
            # Download audio file
            audio_path = await message.download(
                file_name=f"{Config.TEMP_DIR}/{user_id}_audio_{message.audio.file_name or 'audio.mp3'}"
            )
            
            if audio_path:
                await message.reply_text(
                    f"✅ **ᴀᴜᴅɪᴏ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
                    f"**ꜰɪʟᴇ:** {message.audio.file_name or 'Unknown'}\n"
                    f"**sɪᴢᴇ:** {message.audio.file_size / (1024*1024):.2f} ᴍʙ\n\n"
                    f"🎵 sᴛᴀʀᴛɪɴɢ ᴀᴜᴅɪᴏ ʀᴇᴘʟᴀᴄᴇᴍᴇɴᴛ..."
                )
                
                # Clean up request
                del audio_replace_requests[user_id]
                
                # Start processing with audio file
                from plugins.video_processing import start_processing_with_params
                await start_processing_with_params(
                    client, 
                    message, 
                    video_message, 
                    f"replace_audio:{audio_path}", 
                    {"audio_file": audio_path}
                )
            else:
                await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴀᴜᴅɪᴏ")
        else:
            await message.reply_text("📎 **ᴀᴜᴅɪᴏ ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴀᴜᴅɪᴏ ɪɴ ᴀ ᴠɪᴅᴇᴏ, ꜰɪʀsᴛ sᴇɴᴅ ᴛʜᴇ ᴠɪᴅᴇᴏ.")
            
    except Exception as e:
        logger.error(f"Error handling audio upload: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ᴀᴜᴅɪᴏ ꜰɪʟᴇ")

@Client.on_message(filters.document & filters.private)
async def handle_document_upload(client: Client, message: Message):
    """Handle document uploads (SRT files for subtitles)"""
    try:
        user_id = message.from_user.id
        
        # Check if user has pending subtitle request
        if user_id in subtitle_requests:
            file_name = message.document.file_name or ""
            
            # Check if it's an SRT file
            if file_name.lower().endswith('.srt'):
                request = subtitle_requests[user_id]
                video_message = request["video_message"]
                
                # Download SRT file
                srt_path = await message.download(
                    file_name=f"{Config.TEMP_DIR}/{user_id}_subtitle.srt"
                )
                
                if srt_path:
                    await message.reply_text(
                        f"✅ **sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
                        f"**ꜰɪʟᴇ:** {file_name}\n"
                        f"**sɪᴢᴇ:** {message.document.file_size / 1024:.2f} ᴋʙ\n\n"
                        f"📝 sᴛᴀʀᴛɪɴɢ sᴜʙᴛɪᴛʟᴇ ᴘʀᴏᴄᴇssɪɴɢ..."
                    )
                    
                    # Clean up request
                    del subtitle_requests[user_id]
                    
                    # Start processing with SRT file
                    from plugins.video_processing import start_processing_with_params
                    await start_processing_with_params(
                        client, 
                        message, 
                        video_message, 
                        f"subtitles_custom:{srt_path}", 
                        {"srt_file": srt_path}
                    )
                else:
                    await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ")
            else:
                await message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ꜰɪʟᴇ ꜰᴏʀᴍᴀᴛ**\n\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ .sʀᴛ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ.")
        else:
            # Check file type and give appropriate response
            file_name = message.document.file_name or ""
            if file_name.lower().endswith('.srt'):
                await message.reply_text("📄 **sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\nᴛᴏ ᴀᴅᴅ sᴜʙᴛɪᴛʟᴇs ᴛᴏ ᴀ ᴠɪᴅᴇᴏ, ꜰɪʀsᴛ sᴇɴᴅ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴀɴᴅ sᴇʟᴇᴄᴛ sᴜʙᴛɪᴛʟᴇs ᴏᴘᴛɪᴏɴ.")
            else:
                await message.reply_text("📎 **ᴅᴏᴄᴜᴍᴇɴᴛ ʀᴇᴄᴇɪᴠᴇᴅ**\n\nsᴜᴘᴘᴏʀᴛᴇᴅ ꜰɪʟᴇs: .sʀᴛ ꜰᴏʀ sᴜʙᴛɪᴛʟᴇs")
            
    except Exception as e:
        logger.error(f"Error handling document upload: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ᴅᴏᴄᴜᴍᴇɴᴛ")

@Client.on_message(filters.photo & filters.private)
async def handle_image_upload(client: Client, message: Message):
    """Handle image uploads for watermark"""
    try:
        user_id = message.from_user.id
        
        # Check if user has pending watermark image request
        if user_id in watermark_image_requests:
            request = watermark_image_requests[user_id]
            video_message = request["video_message"]
            
            # Download image
            image_path = await message.download(
                file_name=f"{Config.TEMP_DIR}/{user_id}_watermark.jpg"
            )
            
            if image_path:
                await message.reply_text(
                    f"✅ **ᴡᴀᴛᴇʀᴍᴀʀᴋ ɪᴍᴀɢᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
                    f"🖼️ sᴛᴀʀᴛɪɴɢ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴘʀᴏᴄᴇssɪɴɢ..."
                )
                
                # Clean up request
                del watermark_image_requests[user_id]
                
                # Start processing with image watermark
                from plugins.watermark_processing import start_watermark_processing
                await start_watermark_processing(
                    client, 
                    message, 
                    video_message, 
                    "image", 
                    image_path
                )
            else:
                await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ɪᴍᴀɢᴇ")
        else:
            # Check if it's a thumbnail upload request  
            from plugins.thumbnail import thumbnail_requests
            if user_id in thumbnail_requests:
                # Handle thumbnail separately
                from plugins.thumbnail import handle_thumbnail_upload
                await handle_thumbnail_upload(client, message)
            else:
                await message.reply_text("🖼️ **ɪᴍᴀɢᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\nᴛᴏ ᴜsᴇ ᴀs ᴡᴀᴛᴇʀᴍᴀʀᴋ, ꜰɪʀsᴛ sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ ᴀɴᴅ sᴇʟᴇᴄᴛ ɪᴍᴀɢᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴏᴘᴛɪᴏɴ.")
            
    except Exception as e:
        logger.error(f"Error handling image upload: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ")