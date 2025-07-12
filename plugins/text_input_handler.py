from pyrogram import Client, filters
from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "cancel", "credits", "referral", "premium", "sample", "admin", "myplan", "redeem", "refer", "refstats", "earncredits", "setthumbnail", "deletethumbnail", "showthumbnail", "broadcast", "ban", "unban", "addpremium", "createcode", "status", "logs", "dbbackup", "restart", "searchuser"]))
async def handle_text_input(client: Client, message: Message):
    """Handle text input for various operations"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Import request storages
        from plugins.custom_callbacks import trim_requests, screenshot_requests
        from plugins.watermark_handler import watermark_requests
        
        # Check for trim requests
        if user_id in trim_requests:
            request = trim_requests[user_id]
            if request["type"] == "custom_trim":
                try:
                    # Parse time input (supports formats like "30", "1:30", "90")
                    if ":" in text:
                        # Format: MM:SS
                        parts = text.split(":")
                        if len(parts) == 2:
                            minutes = int(parts[0])
                            seconds = int(parts[1])
                            total_seconds = minutes * 60 + seconds
                        else:
                            raise ValueError("Invalid time format")
                    else:
                        # Format: seconds only
                        total_seconds = int(text)
                    
                    # Validate time range
                    video_message = request["video_message"]
                    video_duration = video_message.video.duration
                    
                    if total_seconds < 0 or total_seconds > video_duration:
                        await message.reply_text(
                            f"❌ **ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ**\n\n"
                            f"ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ {video_duration} sᴇᴄᴏɴᴅs."
                        )
                        return
                    
                    # Clean up request
                    del trim_requests[user_id]
                    
                    # Start trim processing
                    from plugins.trim_processing import start_trim_processing
                    await start_trim_processing(client, message, video_message, total_seconds)
                    
                except ValueError:
                    await message.reply_text(
                        f"❌ **ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ**\n\n"
                        f"ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ:\n"
                        f"• sᴇᴄᴏɴᴅs: `120`\n"
                        f"• ᴍɪɴᴜᴛᴇs:sᴇᴄᴏɴᴅs: `2:30`"
                    )
                    return
        
        # Check for screenshot requests
        elif user_id in screenshot_requests:
            request = screenshot_requests[user_id]
            if request["type"] == "custom_screenshot":
                try:
                    # Parse time input (supports formats like "30", "1:30", "90")
                    if ":" in text:
                        # Format: MM:SS
                        parts = text.split(":")
                        if len(parts) == 2:
                            minutes = int(parts[0])
                            seconds = int(parts[1])
                            total_seconds = minutes * 60 + seconds
                        else:
                            raise ValueError("Invalid time format")
                    else:
                        # Format: seconds only
                        total_seconds = int(text)
                    
                    # Validate time range
                    video_message = request["video_message"]
                    video_duration = video_message.video.duration
                    
                    if total_seconds < 0 or total_seconds > video_duration:
                        await message.reply_text(
                            f"❌ **ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ**\n\n"
                            f"ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ {video_duration} sᴇᴄᴏɴᴅs."
                        )
                        return
                    
                    # Clean up request
                    del screenshot_requests[user_id]
                    
                    # Start screenshot processing
                    from plugins.video_processing import start_processing_with_params
                    await start_processing_with_params(
                        client, 
                        message, 
                        video_message, 
                        f"screenshot_1_medium:{total_seconds}", 
                        {"screenshot_time": total_seconds}
                    )
                    
                except ValueError:
                    await message.reply_text(
                        f"❌ **ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ**\n\n"
                        f"ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ:\n"
                        f"• sᴇᴄᴏɴᴅs: `30`\n"
                        f"• ᴍɪɴᴜᴛᴇs:sᴇᴄᴏɴᴅs: `1:30`"
                    )
                    return
        
        # Check for watermark text requests
        elif user_id in watermark_requests:
            request = watermark_requests[user_id]
            if request["type"] == "text_watermark":
                video_message = request["video_message"]
                
                # Validate text length
                if len(text) > 100:
                    await message.reply_text(
                        f"❌ **ᴛᴇxᴛ ᴛᴏᴏ ʟᴏɴɢ**\n\n"
                        f"ᴘʟᴇᴀsᴇ ᴜsᴇ ᴛᴇxᴛ ᴡɪᴛʜ ᴍᴀx 100 ᴄʜᴀʀᴀᴄᴛᴇʀs."
                    )
                    return
                
                # Clean up request
                del watermark_requests[user_id]
                
                # Start watermark processing
                from plugins.watermark_processing import start_watermark_processing
                await start_watermark_processing(client, message, video_message, "text", text)
        
        else:
            # No pending requests - provide general help
            await message.reply_text(
                f"💬 **ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
                f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘᴇɴᴅɪɴɢ ʀᴇǫᴜᴇsᴛs ꜰᴏʀ ᴛᴇxᴛ ɪɴᴘᴜᴛ.\n\n"
                f"sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ ᴛᴏ sᴛᴀʀᴛ ᴘʀᴏᴄᴇssɪɴɢ!"
            )
            
    except Exception as e:
        logger.error(f"Error handling text input: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ᴛᴇxᴛ ɪɴᴘᴜᴛ")