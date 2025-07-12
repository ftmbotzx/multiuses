import os
import uuid
import asyncio
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from helpers.ffmpeg import FFmpegProcessor
from helpers.downloader import Aria2Downloader, FileCleanup
from helpers.watermark import WatermarkProcessor
from progress import ProgressTracker
import logging

logger = logging.getLogger(__name__)
db = Database()

# Store pending operations
pending_operations = {}

# Store temporary files for cleanup
temp_files = []

async def start_processing(client: Client, callback_query: CallbackQuery, video_message: Message, operation: str):
    """Start the actual processing"""
    try:
        user_id = callback_query.from_user.id

        # Get user for credit deduction
        user = await db.get_user(user_id)

        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin

        # Deduct credits only for non-privileged users
        if not bypass_limits:
            if not await db.deduct_credits(user_id, Config.PROCESS_COST):
                await callback_query.answer("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇᴅᴜᴄᴛ ᴄʀᴇᴅɪᴛs", show_alert=True)
                return

        # Increment daily usage only for non-privileged users
        if not bypass_limits:
            await db.increment_daily_usage(user_id)

        # Add operation record
        operation_record = await db.add_operation(user_id, operation, "processing")

        # Answer callback
        await callback_query.answer("✅ ᴘʀᴏᴄᴇssɪɴɢ sᴛᴀʀᴛᴇᴅ!")

        # Start processing using task manager for async handling
        from helpers.task_manager import task_manager
        
        task_id = await task_manager.start_task(
            user_id=user_id,
            task_name=f"video_processing_{operation}",
            coroutine=process_video(client, callback_query.message, video_message, operation, operation_record.inserted_id),
            task_data={
                "operation": operation,
                "video_file_name": video_message.video.file_name,
                "video_size": video_message.video.file_size
            }
        )
        
        logger.info(f"Started async video processing task {task_id} for user {user_id}")

    except Exception as e:
        logger.error(f"Error starting processing: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇss", show_alert=True)

async def process_video(client: Client, reply_message: Message, video_message: Message, operation: str, operation_id, audio_file: str = None, srt_file: str = None):
    """Process video with FFmpeg"""
    try:
        user_id = reply_message.from_user.id
        process_id = str(uuid.uuid4())[:8]
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker(client)
        
        # Create initial progress message
        progress_msg = await reply_message.reply_text(
            f"⏳ **ᴘʀᴇᴘᴀʀɪɴɢ ᴘʀᴏᴄᴇssɪɴɢ...**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"🔄 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ..."
        )
        
        # Setup downloader
        downloader = Aria2Downloader()
        
        # Download video
        await progress_tracker.start_progress(
            chat_id=progress_msg.chat.id,
            message_id=progress_msg.id,
            operation="Downloading Video",
            total_size=video_message.video.file_size,
            progress_id=f"{process_id}_download"
        )
        
        # Download the video file
        video_path = await client.download_media(
            video_message,
            progress=progress_tracker.download_progress,
            file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_{video_message.video.file_name or 'video.mp4'}"
        )
        
        if not video_path:
            await progress_tracker.complete_progress(f"{process_id}_download", False)
            await db.update_operation(operation_id, {"status": "failed"})
            await progress_msg.edit_text("❌ **ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ**")
            return
        
        # Complete download progress
        await progress_tracker.complete_progress(f"{process_id}_download", True)
        
        # Update message for processing
        await progress_msg.edit_text(
            f"✅ **ᴅᴏᴡɴʟᴏᴀᴅ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"🎬 ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ..."
        )
        
        # Store file for cleanup
        temp_files.append(video_path)
        
        # Start processing progress
        await progress_tracker.start_progress(
            chat_id=progress_msg.chat.id,
            message_id=progress_msg.id,
            operation=f"Processing {operation.replace('_', ' ').title()}",
            total_size=100,  # Percentage based
            progress_id=f"{process_id}_process"
        )
        
        # Process video based on operation
        ffmpeg = FFmpegProcessor()
        output_path = None
        
        if operation.startswith("watermark") and operation.count("_") >= 2:
            # Handle watermark operations with specific types
            watermark = WatermarkProcessor()
            parts = operation.split(":")
            if len(parts) > 1:
                watermark_type = parts[0].split("_")[-1]
                watermark_data = parts[1]
                
                if watermark_type == "text":
                    output_path = await watermark.add_text_watermark(
                        video_path, 
                        f"{Config.UPLOADS_DIR}/{process_id}_watermarked.mp4",
                        watermark_data,
                        progress_tracker
                    )
                elif watermark_type == "image" and os.path.exists(watermark_data):
                    output_path = await watermark.add_image_watermark(
                        video_path,
                        f"{Config.UPLOADS_DIR}/{process_id}_watermarked.mp4", 
                        watermark_data,
                        progress_tracker
                    )
        else:
            # Use FFmpeg processor for other operations
            output_path = await ffmpeg.process_video(
                video_path, 
                operation,
                process_id,
                progress_tracker
            )
        
        # Check if processing was successful
        if not output_path:
            await progress_tracker.complete_progress(f"{process_id}_process", False)
            await db.update_operation(operation_id, {"status": "failed"})
            return

        # For multiple screenshots, check if at least one exists
        if isinstance(output_path, list):
            if not any(os.path.exists(path) for path in output_path):
                await progress_tracker.complete_progress(f"{process_id}_process", False)
                await db.update_operation(operation_id, {"status": "failed"})
                return
        else:
            # For single files, check if it exists
            if not os.path.exists(output_path):
                await progress_tracker.complete_progress(f"{process_id}_process", False)
                await db.update_operation(operation_id, {"status": "failed"})
                return

        # Complete processing progress
        await progress_tracker.complete_progress(f"{process_id}_process", True)

        # Update final message
        await progress_msg.edit_text(
            f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"🚀 ᴜᴘʟᴏᴀᴅɪɴɢ ᴘʀᴏᴄᴇssᴇᴅ ᴠɪᴅᴇᴏ..."
        )

        # Send processed video based on operation type
        if operation.startswith("screenshot"):
            # Handle multiple screenshots
            if isinstance(output_path, list):
                for i, screenshot_path in enumerate(output_path):
                    if os.path.exists(screenshot_path):
                        await client.send_photo(
                            reply_message.chat.id,
                            screenshot_path,
                            caption=f"📸 **sᴄʀᴇᴇɴsʜᴏᴛ {i+1}**\n\nᴘʀᴏᴄᴇssᴇᴅ ʙʏ @{client.me.username}",
                            reply_to_message_id=video_message.id
                        )
                        # Store for cleanup
                        temp_files.append(screenshot_path)
                        
                        # Small delay between uploads
                        await asyncio.sleep(0.5)
            else:
                # Single screenshot
                if os.path.exists(output_path):
                    await client.send_photo(
                        reply_message.chat.id,
                        output_path,
                        caption=f"📸 **sᴄʀᴇᴇɴsʜᴏᴛ**\n\nᴘʀᴏᴄᴇssᴇᴅ ʙʏ @{client.me.username}",
                        reply_to_message_id=video_message.id
                    )
                    temp_files.append(output_path)
                    
        elif operation.startswith("extract_audio"):
            # Send as audio
            await client.send_audio(
                reply_message.chat.id,
                output_path,
                caption=f"🎶 **ᴇxᴛʀᴀᴄᴛᴇᴅ ᴀᴜᴅɪᴏ**\n\nᴘʀᴏᴄᴇssᴇᴅ ʙʏ @{client.me.username}",
                reply_to_message_id=video_message.id,
                progress=progress_tracker.upload_progress
            )
            temp_files.append(output_path)
        else:
            # Send as video
            await client.send_video(
                reply_message.chat.id,
                output_path,
                caption=f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\nᴘʀᴏᴄᴇssᴇᴅ ʙʏ @{client.me.username}",
                reply_to_message_id=video_message.id,
                progress=progress_tracker.upload_progress
            )
            temp_files.append(output_path)

        # Update operation status
        await db.update_operation(operation_id, {"status": "completed"})
        
        # Update final message
        await progress_msg.edit_text(
            f"🎉 **ᴄᴏᴍᴘʟᴇᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"✅ ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ ᴀɴᴅ sᴇɴᴛ!"
        )
        
        # Schedule cleanup
        FileCleanup.cleanup_files(temp_files, delay_seconds=10)
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        try:
            await progress_tracker.complete_progress(f"{process_id}_process", False)
            await db.update_operation(operation_id, {"status": "failed"})
            await progress_msg.edit_text(
                f"❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**\n\n"
                f"**ᴇʀʀᴏʀ:** {str(e)[:100]}...\n\n"
                f"ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ."
            )
        except:
            pass
        
        # Cleanup on error
        FileCleanup.cleanup_files(temp_files, delay_seconds=5)

async def process_video_with_params(client: Client, reply_message: Message, video_message: Message, operation: str, operation_id, params: dict):
    """Process video with custom parameters"""
    try:
        user_id = reply_message.from_user.id
        process_id = str(uuid.uuid4())[:8]
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker(client)
        
        # Create initial progress message
        progress_msg = await reply_message.reply_text(
            f"⏳ **ᴘʀᴇᴘᴀʀɪɴɢ ᴘʀᴏᴄᴇssɪɴɢ...**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"🔄 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ..."
        )
        
        # Download video
        await progress_tracker.start_progress(
            chat_id=progress_msg.chat.id,
            message_id=progress_msg.id,
            operation="Downloading Video",
            total_size=video_message.video.file_size,
            progress_id=f"{process_id}_download"
        )
        
        # Download the video file
        video_path = await client.download_media(
            video_message,
            progress=progress_tracker.download_progress,
            file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_{video_message.video.file_name or 'video.mp4'}"
        )
        
        if not video_path:
            await progress_tracker.complete_progress(f"{process_id}_download", False)
            await db.update_operation(operation_id, {"status": "failed"})
            await progress_msg.edit_text("❌ **ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ**")
            return
        
        # Complete download progress
        await progress_tracker.complete_progress(f"{process_id}_download", True)
        
        # Update message for processing
        await progress_msg.edit_text(
            f"✅ **ᴅᴏᴡɴʟᴏᴀᴅ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"🎬 ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ..."
        )
        
        # Store file for cleanup
        temp_files.append(video_path)
        
        # Start processing progress
        await progress_tracker.start_progress(
            chat_id=progress_msg.chat.id,
            message_id=progress_msg.id,
            operation=f"Processing {operation.replace('_', ' ').title()}",
            total_size=100,  # Percentage based
            progress_id=f"{process_id}_process"
        )
        
        # Process video with custom parameters
        if operation.startswith("watermark") and params.get("watermark_text"):
            # Handle custom text watermark
            from helpers.watermark import WatermarkProcessor
            watermark = WatermarkProcessor()
            output_path = await watermark.add_text_watermark(
                video_path, 
                f"{Config.UPLOADS_DIR}/{process_id}_watermarked.mp4",
                params["watermark_text"],
                progress_tracker
            )
        else:
            # Use standard FFmpeg processor
            ffmpeg = FFmpegProcessor()
            output_path = await ffmpeg.process_video(video_path, operation, process_id, progress_tracker)
        
        if not output_path or not os.path.exists(output_path):
            await progress_tracker.complete_progress(f"{process_id}_process", False)
            await db.update_operation(operation_id, {"status": "failed"})
            await progress_msg.edit_text("❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**")
            return

        # Complete processing progress
        await progress_tracker.complete_progress(f"{process_id}_process", True)

        # Update final message and send video
        await progress_msg.edit_text(
            f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"🚀 ᴜᴘʟᴏᴀᴅɪɴɢ ᴘʀᴏᴄᴇssᴇᴅ ᴠɪᴅᴇᴏ..."
        )

        # Send processed video
        await client.send_video(
            reply_message.chat.id,
            output_path,
            caption=f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\nᴘʀᴏᴄᴇssᴇᴅ ʙʏ @{client.me.username}",
            reply_to_message_id=video_message.id,
            progress=progress_tracker.upload_progress
        )
        temp_files.append(output_path)

        # Update operation status
        await db.update_operation(operation_id, {"status": "completed"})
        
        # Update final message
        await progress_msg.edit_text(
            f"🎉 **ᴄᴏᴍᴘʟᴇᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"✅ ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ ᴀɴᴅ sᴇɴᴛ!"
        )
        
        # Schedule cleanup
        FileCleanup.cleanup_files(temp_files, delay_seconds=10)
        
    except Exception as e:
        logger.error(f"Error processing video with params: {e}")
        try:
            await progress_tracker.complete_progress(f"{process_id}_process", False)
            await db.update_operation(operation_id, {"status": "failed"})
            await progress_msg.edit_text(
                f"❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**\n\n"
                f"**ᴇʀʀᴏʀ:** {str(e)[:100]}...\n\n"
                f"ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ."
            )
        except:
            pass
        
        # Cleanup on error
        FileCleanup.cleanup_files(temp_files, delay_seconds=5)

async def start_processing_with_params(client: Client, message: Message, video_message: Message, operation: str, params: dict):
    """Start processing with additional parameters"""
    try:
        user_id = message.from_user.id
        process_id = str(uuid.uuid4())[:8]
        
        # Get user for credit deduction
        user = await db.get_user(user_id)

        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin

        # Deduct credits only for non-privileged users
        if not bypass_limits:
            if not await db.deduct_credits(user_id, Config.PROCESS_COST):
                await message.reply_text("❌ ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs!")
                return

        # Increment daily usage only for non-privileged users
        if not bypass_limits:
            await db.increment_daily_usage(user_id)

        # Add operation record
        operation_record = await db.add_operation(user_id, operation, "processing")

        # Start processing using task manager for async handling
        from helpers.task_manager import task_manager
        
        task_id = await task_manager.start_task(
            user_id=user_id,
            task_name=f"video_processing_{operation}",
            coroutine=process_video_with_params(client, message, video_message, operation, operation_record.inserted_id, params),
            task_data={
                "operation": operation,
                "video_file_name": video_message.video.file_name,
                "video_size": video_message.video.file_size
            }
        )
        
        logger.info(f"Started async video processing task {task_id} for user {user_id}")

    except Exception as e:
        logger.error(f"Error starting processing with params: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇss")