import os
import uuid
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import Config
from database.db import Database
from helpers.ffmpeg import FFmpegProcessor
from helpers.downloader import FileCleanup
import logging

logger = logging.getLogger(__name__)
db = Database()

# Store sample generation requests
sample_requests = {}

@Client.on_message(filters.command("generate") & filters.private)
async def generate_command(client: Client, message: Message):
    """Handle /generate command for sample videos"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        user_id = message.from_user.id

        # Check if user exists
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰɪʀsᴛ ᴜsɪɴɢ /start")
            return

        # Check if user is banned
        if await db.is_user_banned(user_id):
            await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.")
            return

        # Show quantity selection
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1 ᴠɪᴅᴇᴏ", callback_data="sample_qty_1"),
                InlineKeyboardButton("3 ᴠɪᴅᴇᴏs", callback_data="sample_qty_3")
            ],
            [
                InlineKeyboardButton("5 ᴠɪᴅᴇᴏs", callback_data="sample_qty_5"),
                InlineKeyboardButton("10 ᴠɪᴅᴇᴏs", callback_data="sample_qty_10")
            ]
        ])

        await message.reply_text(
            f"🎬 **sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ ɢᴇɴᴇʀᴀᴛᴏʀ**\n\n"
            f"sᴇʟᴇᴄᴛ ʜᴏᴡ ᴍᴀɴʏ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ:",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in generate command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ɪɴ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴍᴍᴀɴᴅ")

@Client.on_callback_query(filters.regex(r"^sample_qty_"))
async def handle_sample_quantity(client: Client, callback_query: CallbackQuery):
    """Handle sample quantity selection"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        user_id = callback_query.from_user.id
        quantity = int(callback_query.data.split("_")[-1])
        
        # Store quantity and show duration options
        # Also preserve existing video_message if it exists
        if user_id in sample_requests:
            sample_requests[user_id]["quantity"] = quantity
        else:
            sample_requests[user_id] = {"quantity": quantity}
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("10 sᴇᴄᴏɴᴅs", callback_data="sample_dur_10"),
                InlineKeyboardButton("30 sᴇᴄᴏɴᴅs", callback_data="sample_dur_30")
            ],
            [
                InlineKeyboardButton("60 sᴇᴄᴏɴᴅs", callback_data="sample_dur_60"),
                InlineKeyboardButton("2 ᴍɪɴᴜᴛᴇs", callback_data="sample_dur_120")
            ],
            [
                InlineKeyboardButton("5 ᴍɪɴᴜᴛᴇs", callback_data="sample_dur_300")
            ]
        ])

        await callback_query.edit_message_text(
            f"🎬 **sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ ɢᴇɴᴇʀᴀᴛᴏʀ**\n\n"
            f"**Qᴜᴀɴᴛɪᴛʏ:** {quantity} ᴠɪᴅᴇᴏ{'s' if quantity > 1 else ''}\n\n"
            f"ɴᴏᴡ sᴇʟᴇᴄᴛ ᴛʜᴇ ᴅᴜʀᴀᴛɪᴏɴ ꜰᴏʀ ᴇᴀᴄʜ ᴠɪᴅᴇᴏ:",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error handling sample quantity: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex(r"^sample_dur_"))
async def handle_sample_duration(client: Client, callback_query: CallbackQuery):
    """Handle sample duration selection and start generation"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()
            
        user_id = callback_query.from_user.id
        duration = int(callback_query.data.split("_")[-1])
        
        if user_id not in sample_requests:
            await callback_query.answer("❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ", show_alert=True)
            return
        
        request_data = sample_requests[user_id]
        quantity = request_data.get("quantity", 1)
        
        # Check if we have video_message
        if "video_message" not in request_data:
            await callback_query.edit_message_text(
                "❌ **ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ**\n\n"
                "ᴘʟᴇᴀsᴇ ᴜᴘʟᴏᴀᴅ ᴀ ᴠɪᴅᴇᴏ ꜰɪʀsᴛ ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ɢᴇɴᴇʀᴀᴛᴇ sᴀᴍᴘʟᴇs"
            )
            del sample_requests[user_id]
            return
        
        video_message = request_data["video_message"]
        del sample_requests[user_id]  # Clean up request
        
        # Check if user is premium or admin
        user = await db.get_user(user_id)
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin
        
        # Calculate total cost
        total_cost = quantity * Config.PROCESS_COST
        
        # Check credits only for non-privileged users
        if not bypass_limits and user.get("credits", 0) < total_cost:
            await callback_query.edit_message_text(
                f"❌ **ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs**\n\n"
                f"ʏᴏᴜ ɴᴇᴇᴅ {total_cost} ᴄʀᴇᴅɪᴛs ʙᴜᴛ ʜᴀᴠᴇ {user.get('credits', 0)}"
            )
            return

        # Deduct credits only for non-privileged users
        if not bypass_limits:
            await db.deduct_credits(user_id, total_cost)

        await callback_query.edit_message_text(
            f"🎬 **ɢᴇɴᴇʀᴀᴛɪɴɢ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs**\n\n"
            f"**Qᴜᴀɴᴛɪᴛʏ:** {quantity}\n"
            f"**ᴅᴜʀᴀᴛɪᴏɴ:** {duration}s ᴇᴀᴄʜ\n\n"
            f"📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ..."
        )

        # Download video first, then generate samples
        import uuid
        unique_id = uuid.uuid4().hex
        video_path = f"{Config.DOWNLOADS_DIR}/{unique_id}_video.mp4"
        
        try:
            video_path = await client.download_media(
                video_message.video,
                file_name=video_path
            )
            
            if not video_path:
                await callback_query.edit_message_text("❌ **ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ**")
                return
            
            # Update status to processing
            await callback_query.edit_message_text(
                f"🎬 **ɢᴇɴᴇʀᴀᴛɪɴɢ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs**\n\n"
                f"**Qᴜᴀɴᴛɪᴛʏ:** {quantity}\n"
                f"**ᴅᴜʀᴀᴛɪᴏɴ:** {duration}s ᴇᴀᴄʜ\n\n"
                f"⏳ ɢᴇɴᴇʀᴀᴛɪɴɢ..."
            )

            # Generate sample videos from the downloaded video
            await generate_sample_videos(client, callback_query.message, user_id, quantity, duration, video_path)
            
        except Exception as e:
            logger.error(f"Error downloading video for sample generation: {e}")
            await callback_query.edit_message_text("❌ **ᴇʀʀᴏʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ**")

    except Exception as e:
        logger.error(f"Error handling sample duration: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

async def generate_sample_videos(client: Client, message: Message, user_id: int, quantity: int, duration: int, video_path: str):
    """Generate sample videos from the original uploaded video"""
    try:
        # Check if video file exists
        if not video_path or not os.path.exists(video_path):
            await message.edit_text("❌ **ᴏʀɪɢɪɴᴀʟ ᴠɪᴅᴇᴏ ꜰɪʟᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ**")
            return
        
        ffmpeg_processor = FFmpegProcessor()
        generated_videos = []
        
        # Get video duration to calculate sample start times
        video_duration = await ffmpeg_processor.get_video_duration(video_path)
        if not video_duration or video_duration < duration:
            await message.edit_text("❌ **ᴠɪᴅᴇᴏ ᴛᴏᴏ sʜᴏʀᴛ ꜰᴏʀ sᴀᴍᴘʟᴇs**")
            return
        
        for i in range(quantity):
            process_id = str(uuid.uuid4())
            output_path = f"{Config.UPLOADS_DIR}/{process_id}_sample_{i+1}_{duration}s.mp4"
            
            # Calculate start time for this sample (distribute samples across video)
            if quantity == 1:
                start_time = video_duration / 2  # Middle of video
            else:
                # Distribute samples evenly across the video
                segment_size = (video_duration - duration) / max(1, quantity - 1)
                start_time = i * segment_size
            
            # Update progress
            await message.edit_text(
                f"🎬 **ɢᴇɴᴇʀᴀᴛɪɴɢ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs**\n\n"
                f"**ᴘʀᴏɢʀᴇss:** {i+1}/{quantity}\n"
                f"**ᴅᴜʀᴀᴛɪᴏɴ:** {duration}s ᴇᴀᴄʜ\n"
                f"**sᴀᴍᴘʟᴇ {i+1}:** {int(start_time)}s - {int(start_time + duration)}s\n\n"
                f"⏳ ᴄʀᴇᴀᴛɪɴɢ sᴀᴍᴘʟᴇ {i+1}..."
            )
            
            # Create sample from original video with improved performance
            success = await create_sample_from_video_optimized(video_path, output_path, int(start_time), duration, i+1)
            
            if success and os.path.exists(output_path):
                generated_videos.append(output_path)
            else:
                logger.error(f"Failed to generate sample video {i+1}")

        # Send all generated videos
        if generated_videos:
            await message.edit_text(
                f"✅ **sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs ɢᴇɴᴇʀᴀᴛᴇᴅ**\n\n"
                f"📤 sᴇɴᴅɪɴɢ {len(generated_videos)} ᴠɪᴅᴇᴏs..."
            )
            
            for i, video_path in enumerate(generated_videos):
                try:
                    await client.send_video(
                        user_id,
                        video_path,
                        caption=f"🎬 **sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ {i+1}**\n\n**ᴅᴜʀᴀᴛɪᴏɴ:** {duration}s\n**ꜰʀᴏᴍ:** ʏᴏᴜʀ ᴜᴘʟᴏᴀᴅᴇᴅ ᴠɪᴅᴇᴏ"
                    )
                except Exception as e:
                    logger.error(f"Failed to send sample video {i+1}: {e}")
            
            # Clean up files (including original video)
            cleanup_files = generated_videos + [video_path]
            FileCleanup.cleanup_files(cleanup_files, delay_seconds=30)
            
            # Remove from sample_requests
            if user_id in sample_requests:
                del sample_requests[user_id]
            
            await message.edit_text(
                f"✅ **ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                f"sᴇɴᴛ {len(generated_videos)} sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs ꜰʀᴏᴍ ʏᴏᴜʀ ᴜᴘʟᴏᴀᴅᴇᴅ ᴠɪᴅᴇᴏ!"
            )
        else:
            await message.edit_text("❌ **ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs**")

    except Exception as e:
        logger.error(f"Error generating sample videos: {e}")
        await message.edit_text("❌ **ᴇʀʀᴏʀ ɪɴ ᴠɪᴅᴇᴏ ɢᴇɴᴇʀᴀᴛɪᴏɴ**")

async def create_sample_from_video(input_path: str, output_path: str, start_time: int, duration: int, video_number: int) -> bool:
    """Create a sample video clip from the original video"""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Trim the video to create a sample
        cmd = [
            Config.FFMPEG_PATH,
            "-i", input_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            "-y", output_path
        ]
        
        logger.info(f"Creating sample video {video_number}: {start_time}s-{start_time+duration}s from {input_path}")
        
        # Run the command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Sample video {video_number} created successfully: {output_path}")
            return True
        else:
            logger.error(f"Failed to create sample video {video_number}: {stderr.decode()}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample video {video_number}: {e}")
        return False

async def create_sample_from_video_optimized(input_path: str, output_path: str, start_time: int, duration: int, video_number: int) -> bool:
    """Create a sample video clip from the original video with optimized performance"""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Optimized FFmpeg command for faster processing
        cmd = [
            Config.FFMPEG_PATH,
            "-ss", str(start_time),  # Seek before input for faster performance
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",  # Stream copy for fastest processing
            "-avoid_negative_ts", "make_zero",
            "-fflags", "+genpts",  # Generate PTS for better compatibility
            "-y", output_path
        ]
        
        logger.info(f"Creating sample video {video_number}: {start_time}s-{start_time+duration}s from {input_path}")
        
        # Run the command with timeout for better performance
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Sample video {video_number} created successfully: {output_path}")
                return True
            else:
                logger.error(f"Failed to create sample video {video_number}: {stderr.decode()}")
                return False
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout creating sample video {video_number}")
            process.kill()
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample video {video_number}: {e}")
        return False

async def create_sample_video(output_path: str, duration: int, video_number: int) -> bool:
    """Create a sample video with colored bars and timer using FFmpeg"""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate colorful test pattern with timer (simplified for better compatibility)
        cmd = [
            Config.FFMPEG_PATH,
            "-f", "lavfi",
            "-i", f"testsrc2=duration={duration}:size=1280x720:rate=30",
            "-f", "lavfi", 
            "-i", f"sine=frequency=1000:duration={duration}",
            "-vf", f"drawtext=text='Sample Video {video_number}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.5,drawtext=text='%{{pts\\:hms}}':fontcolor=yellow:fontsize=36:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.5",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-shortest",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Sample video created successfully: {output_path}")
            return True
        else:
            logger.error(f"Failed to create sample video. FFmpeg error: {stderr.decode()}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample video: {e}")
        return False