import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from helpers.ffmpeg import FFmpegProcessor
from helpers.downloader import Aria2Downloader, FileCleanup
from progress import ProgressTracker
import logging

logger = logging.getLogger(__name__)
db = Database()

# Store merge video collections - shared from video_upload
from plugins.video_upload import merge_collections

@Client.on_callback_query(filters.regex(r"^merge_"))
async def handle_merge_callback(client: Client, callback_query: CallbackQuery):
    """Handle merge operation callbacks"""
    try:
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        if data.startswith("merge_start_"):
            message_id = int(data.split("_")[-1])
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            # Initialize merge collection for this user
            merge_collections[user_id] = {
                "videos": [video_message],
                "started_at": time.time()
            }
            
            await callback_query.edit_message_text(
                f"🔗 **ᴍᴇʀɢᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ sᴛᴀʀᴛᴇᴅ**\n\n"
                f"**ᴠɪᴅᴇᴏs ᴄᴏʟʟᴇᴄᴛᴇᴅ:** 1\n\n"
                f"📤 sᴇɴᴅ ᴍᴇ ᴍᴏʀᴇ ᴠɪᴅᴇᴏs ᴛᴏ ᴀᴅᴅ ᴛᴏ ᴛʜᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ.\n\n"
                f"ᴡʜᴇɴ ᴅᴏɴᴇ, ᴄʟɪᴄᴋ '✅ ᴍᴇʀɢᴇ ᴀʟʟ' ᴛᴏ ᴄᴏᴍʙɪɴᴇ ᴛʜᴇᴍ.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ ᴍᴇʀɢᴇ ᴀʟʟ", callback_data=f"merge_process_{user_id}")],
                    [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"merge_cancel_{user_id}")]
                ])
            )
            
        elif data.startswith("merge_process_"):
            await process_merge_collection(client, callback_query, user_id)
            
        elif data.startswith("merge_cancel_"):
            if user_id in merge_collections:
                del merge_collections[user_id]
            await callback_query.edit_message_text("❌ **ᴍᴇʀɢᴇ ᴄᴀɴᴄᴇʟʟᴇᴅ**")
            
    except Exception as e:
        logger.error(f"Error in merge callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

async def handle_merge_collection(client: Client, message: Message, user_id: int):
    """Handle video collection for merge"""
    try:
        if user_id not in merge_collections:
            return
            
        collection = merge_collections[user_id]
        collection["videos"].append(message)
        
        video_count = len(collection["videos"])
        total_size = sum(v.video.file_size for v in collection["videos"]) / (1024*1024)
        
        await message.reply_text(
            f"🔗 **ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ ᴛᴏ ᴍᴇʀɢᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ**\n\n"
            f"**ᴠɪᴅᴇᴏs ᴄᴏʟʟᴇᴄᴛᴇᴅ:** {video_count}\n"
            f"**ᴛᴏᴛᴀʟ sɪᴢᴇ:** {total_size:.2f} ᴍʙ\n\n"
            f"📤 sᴇɴᴅ ᴍᴏʀᴇ ᴠɪᴅᴇᴏs ᴏʀ ᴄʟɪᴄᴋ ᴍᴇʀɢᴇ ᴛᴏ ᴄᴏᴍʙɪɴᴇ ᴛʜᴇᴍ.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ᴍᴇʀɢᴇ ᴀʟʟ", callback_data=f"merge_process_{user_id}")],
                [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"merge_cancel_{user_id}")]
            ])
        )
        
    except Exception as e:
        logger.error(f"Error handling merge collection: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴀᴅᴅɪɴɢ ᴠɪᴅᴇᴏ ᴛᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ")

async def process_merge_collection(client: Client, callback_query: CallbackQuery, user_id: int):
    """Process the collected videos for merging"""
    try:
        if user_id not in merge_collections:
            await callback_query.answer("❌ ɴᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ꜰᴏᴜɴᴅ", show_alert=True)
            return
            
        collection = merge_collections[user_id]
        videos = collection["videos"]
        
        if len(videos) < 2:
            await callback_query.answer("❌ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2 ᴠɪᴅᴇᴏs", show_alert=True)
            return
        
        # Check user privileges and credits
        user = await db.get_user(user_id)
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin
        
        # Deduct credits (merge costs per video being merged)
        cost = Config.PROCESS_COST * len(videos)
        if not bypass_limits:
            if not user or user.get("credits", 0) < cost:
                await callback_query.answer(
                    f"❌ ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs!\nɴᴇᴇᴅ {cost} ᴄʀᴇᴅɪᴛs ꜰᴏʀ {len(videos)} ᴠɪᴅᴇᴏs",
                    show_alert=True
                )
                return
                
            if not await db.deduct_credits(user_id, cost):
                await callback_query.answer("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇᴅᴜᴄᴛ ᴄʀᴇᴅɪᴛs", show_alert=True)
                return
        
        await callback_query.answer("✅ sᴛᴀʀᴛɪɴɢ ᴍᴇʀɢᴇ ᴘʀᴏᴄᴇss!")
        
        # Update message
        progress_msg = await callback_query.edit_message_text(
            f"🔗 **ᴍᴇʀɢɪɴɢ ᴠɪᴅᴇᴏs**\n\n"
            f"**ᴠɪᴅᴇᴏs:** {len(videos)}\n\n"
            f"⏳ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏs..."
        )
        
        # Download all videos
        video_paths = []
        progress_tracker = ProgressTracker(client)
        
        for i, video_msg in enumerate(videos):
            await progress_msg.edit_text(
                f"🔗 **ᴍᴇʀɢɪɴɢ ᴠɪᴅᴇᴏs**\n\n"
                f"**ᴠɪᴅᴇᴏs:** {len(videos)}\n\n"
                f"⏬ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ {i+1}/{len(videos)}..."
            )
            
            video_path = await client.download_media(
                video_msg,
                file_name=f"{Config.DOWNLOADS_DIR}/merge_{user_id}_{i}_{video_msg.video.file_name or f'video{i}.mp4'}"
            )
            
            if video_path:
                video_paths.append(video_path)
            else:
                await progress_msg.edit_text("❌ **ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ**")
                # Cleanup
                for path in video_paths:
                    try:
                        os.remove(path)
                    except:
                        pass
                del merge_collections[user_id]
                return
        
        # Merge videos
        await progress_msg.edit_text(
            f"🔗 **ᴍᴇʀɢɪɴɢ ᴠɪᴅᴇᴏs**\n\n"
            f"**ᴠɪᴅᴇᴏs:** {len(videos)}\n\n"
            f"🎬 ᴍᴇʀɢɪɴɢ ᴠɪᴅᴇᴏs..."
        )
        
        # Use FFmpeg to merge videos
        ffmpeg = FFmpegProcessor()
        process_id = f"merge_{user_id}"
        
        output_path = await ffmpeg.merge_multiple_videos(video_paths, process_id)
        
        if output_path and os.path.exists(output_path):
            # Send merged video
            await progress_msg.edit_text(
                f"🔗 **ᴍᴇʀɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                f"🚀 ᴜᴘʟᴏᴀᴅɪɴɢ ᴍᴇʀɢᴇᴅ ᴠɪᴅᴇᴏ..."
            )
            
            await client.send_video(
                callback_query.message.chat.id,
                output_path,
                caption=f"🔗 **ᴍᴇʀɢᴇᴅ ᴠɪᴅᴇᴏ**\n\n**ᴏʀɪɢɪɴᴀʟ ᴠɪᴅᴇᴏs:** {len(videos)}\n\nᴘʀᴏᴄᴇssᴇᴅ ʙʏ @{client.me.username}",
                progress=progress_tracker.upload_progress
            )
            
            await progress_msg.edit_text("🎉 **ᴍᴇʀɢᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**")
            
            # Cleanup
            for path in video_paths + [output_path]:
                try:
                    os.remove(path)
                except:
                    pass
        else:
            await progress_msg.edit_text("❌ **ᴍᴇʀɢᴇ ꜰᴀɪʟᴇᴅ**")
            
            # Cleanup on failure
            for path in video_paths:
                try:
                    os.remove(path)
                except:
                    pass
        
        # Clean up collection
        del merge_collections[user_id]
        
    except Exception as e:
        logger.error(f"Error processing merge: {e}")
        await callback_query.edit_message_text("❌ **ᴍᴇʀɢᴇ ꜰᴀɪʟᴇᴅ**\n\nᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.")
        if user_id in merge_collections:
            del merge_collections[user_id]