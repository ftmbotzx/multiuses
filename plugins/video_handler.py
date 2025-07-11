import os
import uuid
import json
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
from helpers.ffmpeg import FFmpegProcessor
from helpers.downloader import Aria2Downloader, FileCleanup
from helpers.watermark import WatermarkProcessor
from progress import ProgressTracker
import logging
import asyncio

logger = logging.getLogger(__name__)
db = Database()

# Store pending operations
pending_operations = {}

# Store merge video collections
merge_collections = {}

# Store temporary files for cleanup
temp_files = []

# Store watermark requests
watermark_requests = {}

# Store trim requests  
trim_requests = {}

# Store screenshot requests
screenshot_requests = {}

async def check_user_privileges(user_id, user, db):
    """Check if user has unlimited privileges (premium or admin)"""
    is_premium = await db.is_user_premium(user_id)
    is_admin = user_id in Config.ADMINS
    return is_premium, is_admin

async def should_bypass_limits(user_id, db):
    """Check if user should bypass credit and daily limits"""
    is_premium = await db.is_user_premium(user_id)
    is_admin = user_id in Config.ADMINS
    return is_premium or is_admin

@Client.on_message(filters.video & filters.private)
async def handle_video(client: Client, message: Message):
    """Handle video uploads"""
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

        # Check if user is collecting videos for merge
        if user_id in merge_collections:
            await handle_merge_collection(client, message, user_id)
            return

        # Check if user is premium or admin - they have unlimited access
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS

        # Check daily limit only for non-premium, non-admin users
        if not is_premium and not is_admin and not await db.check_daily_limit(user_id):
            await message.reply_text(
                f"⏰ **ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ**\n\n"
                f"ꜰʀᴇᴇ ᴜsᴇʀs ᴄᴀɴ ᴏɴʟʏ ᴘʀᴏᴄᴇss {Config.DAILY_LIMIT} ᴠɪᴅᴇᴏs ᴘᴇʀ ᴅᴀʏ.\n\n"
                f"💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ꜰᴏʀ ᴜɴʟɪᴍɪᴛᴇᴅ ᴘʀᴏᴄᴇssɪɴɢ!"
            )
            return

        # Show processing options
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✂️ ᴛʀɪᴍ ᴠɪᴅᴇᴏ", callback_data=f"option_trim_{message.id}"),
                InlineKeyboardButton("🗜️ ᴄᴏᴍᴘʀᴇss", callback_data=f"option_compress_{message.id}")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴏᴛᴀᴛᴇ", callback_data=f"option_rotate_{message.id}"),
                InlineKeyboardButton("🔗 ᴍᴇʀɢᴇ", callback_data=f"option_merge_{message.id}")
            ],
            [
                InlineKeyboardButton("💧 ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data=f"option_watermark_{message.id}"),
                InlineKeyboardButton("🔇 ᴍᴜᴛᴇ", callback_data=f"option_mute_{message.id}")
            ],
            [
                InlineKeyboardButton("🎵 ʀᴇᴘʟᴀᴄᴇ ᴀᴜᴅɪᴏ", callback_data=f"option_replace_audio_{message.id}"),
                InlineKeyboardButton("⏮️ ʀᴇᴠᴇʀsᴇ", callback_data=f"option_reverse_{message.id}")
            ],
            [
                InlineKeyboardButton("📝 sᴜʙᴛɪᴛʟᴇs", callback_data=f"option_subtitles_{message.id}"),
                InlineKeyboardButton("📏 ʀᴇsᴏʟᴜᴛɪᴏɴ", callback_data=f"option_resolution_{message.id}")
            ],
            [
                InlineKeyboardButton("🎶 ᴇxᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ", callback_data=f"option_extract_audio_{message.id}"),
                InlineKeyboardButton("📸 sᴄʀᴇᴇɴsʜᴏᴛ", callback_data=f"option_screenshot_{message.id}")
            ],
            [
                InlineKeyboardButton("🎬 ɢᴇɴᴇʀᴀᴛᴇ sᴀᴍᴘʟᴇ", callback_data=f"option_generate_{message.id}")
            ]
        ])

        video_info = f"📹 **ᴠɪᴅᴇᴏ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
        video_info += f"**ꜰɪʟᴇ ɴᴀᴍᴇ:** {message.video.file_name or 'Unknown'}\n"
        video_info += f"**sɪᴢᴇ:** {message.video.file_size / (1024*1024):.2f} ᴍʙ\n"
        video_info += f"**ᴅᴜʀᴀᴛɪᴏɴ:** {message.video.duration // 60}:{message.video.duration % 60:02d}\n"
        video_info += f"**ʀᴇsᴏʟᴜᴛɪᴏɴ:** {message.video.width}x{message.video.height}\n\n"
        if is_premium:
            video_info += f"**ᴄᴏsᴛ:** 💎 ꜰʀᴇᴇ (ᴘʀᴇᴍɪᴜᴍ)\n"
        elif is_admin:
            video_info += f"**ᴄᴏsᴛ:** 🔧 ꜰʀᴇᴇ (ᴀᴅᴍɪɴ)\n"
        else:
            video_info += f"**ᴄᴏsᴛ:** {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ᴘᴇʀ ᴏᴘᴇʀᴀᴛɪᴏɴ\n"
            video_info += f"**ʏᴏᴜʀ ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0)}\n\n"
        video_info += "ᴄʜᴏᴏsᴇ ᴀ ᴘʀᴏᴄᴇssɪɴɢ ᴏᴘᴛɪᴏɴ:"

        await message.reply_text(video_info, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error handling video: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

# Handle option selection (with detailed configuration)
@Client.on_callback_query(filters.regex(r"^option_"))
async def handle_option_callback(client: Client, callback_query: CallbackQuery):
    """Handle video processing option callbacks"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        user_id = callback_query.from_user.id
        data = callback_query.data

        # Parse callback data
        parts = data.split("_")
        if len(parts) < 3:
            await callback_query.answer("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ", show_alert=True)
            return

        operation = "_".join(parts[1:-1])
        message_id = int(parts[-1])

        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Check if user is banned
        if await db.is_user_banned(user_id):
            await callback_query.answer("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ", show_alert=True)
            return

        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin

        # Check credits only for non-privileged users
        if not bypass_limits and user.get("credits", 0) < Config.PROCESS_COST:
            await callback_query.answer(
                f"❌ ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs!\nʏᴏᴜ ɴᴇᴇᴅ {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ʙᴜᴛ ʜᴀᴠᴇ {user.get('credits', 0)}",
                show_alert=True
            )
            return

        # Check daily limit only for non-privileged users
        if not bypass_limits and not await db.check_daily_limit(user_id):
            await callback_query.answer("⏰ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ", show_alert=True)
            return

        # Get original video message
        try:
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            if not video_message.video:
                await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
                return
        except Exception as e:
            await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Handle generate option separately - Show options first, then download
        if operation == "generate":
            # Import the sample_requests here to store the video message info
            from plugins.sample_generator import sample_requests
            
            # Store the video message info (but don't download yet)
            sample_requests[user_id] = {
                "video_message": video_message,
                "timestamp": time.time()
            }
            
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
            await callback_query.edit_message_text(
                f"🎬 **sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ ɢᴇɴᴇʀᴀᴛᴏʀ**\n\n"
                f"ɪ'ʟʟ ᴄʀᴇᴀᴛᴇ sᴀᴍᴘʟᴇs ꜰʀᴏᴍ ʏᴏᴜʀ ᴜᴘʟᴏᴀᴅᴇᴅ ᴠɪᴅᴇᴏ.\n\n"
                f"sᴇʟᴇᴄᴛ ʜᴏᴡ ᴍᴀɴʏ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏs ʏᴏᴜ ᴡᴀɴᴛ:",
                reply_markup=keyboard
            )
            return

        # Show detailed options based on operation type
        if operation == "trim":
            await show_trim_options(client, callback_query, video_message)
        elif operation == "compress":
            await show_compress_options(client, callback_query, video_message)
        elif operation == "rotate":
            await show_rotate_options(client, callback_query, video_message)
        elif operation == "merge":
            await show_merge_options(client, callback_query, video_message)
        elif operation == "watermark":
            await show_watermark_options(client, callback_query, video_message)
        elif operation == "screenshot":
            await show_screenshot_options(client, callback_query, video_message)
        elif operation == "resolution":
            await show_resolution_options(client, callback_query, video_message)
        elif operation == "extract_audio":
            await show_extract_audio_options(client, callback_query, video_message)
        elif operation == "subtitles":
            await show_subtitles_options(client, callback_query, video_message)
        elif operation == "replace_audio":
            await show_replace_audio_options(client, callback_query, video_message)
        else:
            # For simple operations, start processing directly
            await start_processing(client, callback_query, video_message, operation)

    except Exception as e:
        logger.error(f"Error in option callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ sʜᴏᴡɪɴɢ ᴏᴘᴛɪᴏɴs", show_alert=True)

# Handle processing confirmation
@Client.on_callback_query(filters.regex(r"^process_"))
async def handle_process_callback(client: Client, callback_query: CallbackQuery):
    """Handle video processing callbacks"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        user_id = callback_query.from_user.id
        data = callback_query.data

        # Parse callback data
        parts = data.split("_")
        if len(parts) < 3:
            await callback_query.answer("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ", show_alert=True)
            return

        operation = "_".join(parts[1:-1])
        message_id = int(parts[-1])

        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Check if user is banned
        if await db.is_user_banned(user_id):
            await callback_query.answer("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ", show_alert=True)
            return

        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin

        # Check credits only for non-privileged users
        if not bypass_limits and user.get("credits", 0) < Config.PROCESS_COST:
            await callback_query.answer(
                f"❌ ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs!\nʏᴏᴜ ɴᴇᴇᴅ {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ʙᴜᴛ ʜᴀᴠᴇ {user.get('credits', 0)}",
                show_alert=True
            )
            return

        # Check daily limit only for non-privileged users
        if not bypass_limits and not await db.check_daily_limit(user_id):
            await callback_query.answer("⏰ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ", show_alert=True)
            return

        # Get original video message
        try:
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            if not video_message.video:
                await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
                return
        except Exception as e:
            await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Start processing
        await start_processing(client, callback_query, video_message, operation)

    except Exception as e:
        logger.error(f"Error in process callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇss", show_alert=True)

async def show_trim_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show trim options"""
    duration = video_message.video.duration
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✂️ ꜰɪʀsᴛ 30s", callback_data=f"process_trim_30_{video_message.id}"),
            InlineKeyboardButton("✂️ ꜰɪʀsᴛ 60s", callback_data=f"process_trim_60_{video_message.id}")
        ],
        [
            InlineKeyboardButton("✂️ ꜰɪʀsᴛ 5ᴍɪɴ", callback_data=f"process_trim_300_{video_message.id}"),
            InlineKeyboardButton("✂️ ꜰɪʀsᴛ 10ᴍɪɴ", callback_data=f"process_trim_600_{video_message.id}")
        ],
        [
            InlineKeyboardButton("✂️ ᴄᴜsᴛᴏᴍ", callback_data=f"process_trim_custom_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"✂️ **ᴛʀɪᴍ ᴠɪᴅᴇᴏ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"**ᴏʀɪɢɪɴᴀʟ ᴅᴜʀᴀᴛɪᴏɴ:** {duration // 60}:{duration % 60:02d}\n\n"
    text += f"sᴇʟᴇᴄᴛ ʜᴏᴡ ᴍᴜᴄʜ ᴏꜰ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴛᴏ ᴋᴇᴇᴘ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_compress_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show compress options"""
    size_mb = video_message.video.file_size / (1024 * 1024)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗜️ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ", callback_data=f"process_compress_high_{video_message.id}"),
            InlineKeyboardButton("🗜️ ᴍᴇᴅɪᴜᴍ", callback_data=f"process_compress_medium_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🗜️ sᴍᴀʟʟ sɪᴢᴇ", callback_data=f"process_compress_small_{video_message.id}"),
            InlineKeyboardButton("🗜️ ᴛɪɴʏ sɪᴢᴇ", callback_data=f"process_compress_tiny_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"🗜️ **ᴄᴏᴍᴘʀᴇss ᴠɪᴅᴇᴏ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"**ᴏʀɪɢɪɴᴀʟ sɪᴢᴇ:** {size_mb:.2f} ᴍʙ\n\n"
    text += f"sᴇʟᴇᴄᴛ ᴄᴏᴍᴘʀᴇssɪᴏɴ ʟᴇᴠᴇʟ:\n"
    text += f"• ʜɪɢʜ ǫᴜᴀʟɪᴛʏ: ~{size_mb * 0.7:.1f} ᴍʙ\n"
    text += f"• ᴍᴇᴅɪᴜᴍ: ~{size_mb * 0.5:.1f} ᴍʙ\n"
    text += f"• sᴍᴀʟʟ sɪᴢᴇ: ~{size_mb * 0.3:.1f} ᴍʙ\n"
    text += f"• ᴛɪɴʏ sɪᴢᴇ: ~{size_mb * 0.1:.1f} ᴍʙ"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_rotate_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show rotate options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 90° ᴄʟᴏᴄᴋᴡɪsᴇ", callback_data=f"process_rotate_90_{video_message.id}"),
            InlineKeyboardButton("🔄 180°", callback_data=f"process_rotate_180_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🔄 270° ᴄʟᴏᴄᴋᴡɪsᴇ", callback_data=f"process_rotate_270_{video_message.id}"),
            InlineKeyboardButton("🔄 ꜰʟɪᴘ ʜᴏʀɪᴢᴏɴᴛᴀʟ", callback_data=f"process_rotate_flip_h_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🔄 ꜰʟɪᴘ ᴠᴇʀᴛɪᴄᴀʟ", callback_data=f"process_rotate_flip_v_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"🔄 **ʀᴏᴛᴀᴛᴇ ᴠɪᴅᴇᴏ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"sᴇʟᴇᴄᴛ ʀᴏᴛᴀᴛɪᴏɴ ᴏᴘᴛɪᴏɴ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_merge_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show merge options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📤 sᴇɴᴅ ᴀɴᴏᴛʜᴇʀ ᴠɪᴅᴇᴏ", callback_data=f"merge_wait_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"🔗 **ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏs**\n\n"
    text += f"ᴛᴏ ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏs, ɪ ɴᴇᴇᴅ ᴀɴᴏᴛʜᴇʀ ᴠɪᴅᴇᴏ ꜰʀᴏᴍ ʏᴏᴜ.\n\n"
    text += f"**ᴄᴜʀʀᴇɴᴛ ᴠɪᴅᴇᴏ:**\n"
    text += f"• ᴅᴜʀᴀᴛɪᴏɴ: {video_message.video.duration // 60}:{video_message.video.duration % 60:02d}\n"
    text += f"• sɪᴢᴇ: {video_message.video.file_size / (1024*1024):.2f} ᴍʙ\n\n"
    text += f"ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_watermark_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show watermark options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💧 ᴅᴇꜰᴀᴜʟᴛ ᴛᴇxᴛ", callback_data=f"process_watermark_text_{video_message.id}"),
            InlineKeyboardButton("🎨 ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ", callback_data=f"watermark_custom_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🖼️ ɪᴍᴀɢᴇ", callback_data=f"watermark_image_{video_message.id}"),
            InlineKeyboardButton("🏷️ ᴛɪᴍᴇsᴛᴀᴍᴘ", callback_data=f"process_watermark_timestamp_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"💧 **ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"sᴇʟᴇᴄᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛʏᴘᴇ:\n\n"
    text += f"• **ᴅᴇꜰᴀᴜʟᴛ ᴛᴇxᴛ**: ᴀᴅᴅs 'ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ' ᴛᴇxᴛ\n"
    text += f"• **ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ**: ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴏᴡɴ ᴛᴇxᴛ\n"
    text += f"• **ɪᴍᴀɢᴇ**: ᴜsᴇ ʏᴏᴜʀ ᴏᴡɴ ɪᴍᴀɢᴇ/ʟᴏɢᴏ\n"
    text += f"• **ᴛɪᴍᴇsᴛᴀᴍᴘ**: ᴀᴅᴅs ᴄᴜʀʀᴇɴᴛ ᴅᴀᴛᴇ/ᴛɪᴍᴇ (ɪsᴛ)"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_screenshot_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show screenshot options"""
    duration = video_message.video.duration
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📸 sɪɴɢʟᴇ (ᴍɪᴅᴅʟᴇ)", callback_data=f"process_screenshot_single_{video_message.id}"),
            InlineKeyboardButton("📸 3 sᴄʀᴇᴇɴsʜᴏᴛs", callback_data=f"process_screenshot_multi_3_{video_message.id}")
        ],
        [
            InlineKeyboardButton("📸 5 sᴄʀᴇᴇɴsʜᴏᴛs", callback_data=f"process_screenshot_multi_5_{video_message.id}"),
            InlineKeyboardButton("📸 10 sᴄʀᴇᴇɴsʜᴏᴛs", callback_data=f"process_screenshot_multi_10_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🎨 ʜᴅ ǫᴜᴀʟɪᴛʏ", callback_data=f"process_screenshot_hd_{video_message.id}"),
            InlineKeyboardButton("📝 ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇ", callback_data=f"screenshot_custom_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"📸 **sᴄʀᴇᴇɴsʜᴏᴛ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"**ᴠɪᴅᴇᴏ ᴅᴜʀᴀᴛɪᴏɴ:** {duration // 60}:{duration % 60:02d}\n\n"
    text += f"sᴇʟᴇᴄᴛ sᴄʀᴇᴇɴsʜᴏᴛ ᴏᴘᴛɪᴏɴ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_resolution_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show resolution options"""
    current_res = f"{video_message.video.width}x{video_message.video.height}"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📏 480ᴘ", callback_data=f"process_resolution_480_{video_message.id}"),
            InlineKeyboardButton("📏 720ᴘ", callback_data=f"process_resolution_720_{video_message.id}")
        ],
        [
            InlineKeyboardButton("📏 1080ᴘ", callback_data=f"process_resolution_1080_{video_message.id}"),
            InlineKeyboardButton("📏 1440ᴘ", callback_data=f"process_resolution_1440_{video_message.id}")
        ],
        [
            InlineKeyboardButton("📏 4ᴋ", callback_data=f"process_resolution_4k_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"📏 **ᴄʜᴀɴɢᴇ ʀᴇsᴏʟᴜᴛɪᴏɴ**\n\n"
    text += f"**ᴄᴜʀʀᴇɴᴛ ʀᴇsᴏʟᴜᴛɪᴏɴ:** {current_res}\n\n"
    text += f"sᴇʟᴇᴄᴛ ɴᴇᴡ ʀᴇsᴏʟᴜᴛɪᴏɴ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_extract_audio_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show extract audio options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎶 ᴍᴘ3 (ʜɪɢʜ)", callback_data=f"process_extract_audio_mp3_high_{video_message.id}"),
            InlineKeyboardButton("🎶 ᴍᴘ3 (ᴍᴇᴅɪᴜᴍ)", callback_data=f"process_extract_audio_mp3_medium_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🎶 ᴍᴘ3 (ʟᴏᴡ)", callback_data=f"process_extract_audio_mp3_low_{video_message.id}"),
            InlineKeyboardButton("🎵 ᴡᴀᴠ", callback_data=f"process_extract_audio_wav_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"🎶 **ᴇxᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"sᴇʟᴇᴄᴛ ᴀᴜᴅɪᴏ ғᴏʀᴍᴀᴛ ᴀɴᴅ ǫᴜᴀʟɪᴛʏ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_subtitles_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show subtitles options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 sᴀᴍᴘʟᴇ sᴜʙᴛɪᴛʟᴇ", callback_data=f"process_subtitles_sample_{video_message.id}"),
            InlineKeyboardButton("📄 ᴄᴜsᴛᴏᴍ .sʀᴛ ꜰɪʟᴇ", callback_data=f"subtitles_custom_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"📝 **ᴀᴅᴅ sᴜʙᴛɪᴛʟᴇs**\n\n"
    text += f"sᴇʟᴇᴄᴛ sᴜʙᴛɪᴛʟᴇ ᴏᴘᴛɪᴏɴ:\n\n"
    text += f"• **sᴀᴍᴘʟᴇ sᴜʙᴛɪᴛʟᴇ**: ᴀᴅᴅ ᴀ sᴀᴍᴘʟᴇ ᴛᴇxᴛ\n"
    text += f"• **ᴄᴜsᴛᴏᴍ .sʀᴛ ꜰɪʟᴇ**: ᴜᴘʟᴏᴀᴅ ʏᴏᴜʀ ᴏᴡɴ .sʀᴛ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_replace_audio_options(client: Client, callback_query: CallbackQuery, video_message: Message):
    """Show replace audio options - direct to upload"""
    # Store request for audio upload directly
    user_id = callback_query.from_user.id
    audio_replace_requests[user_id] = {
        "video_message": video_message,
        "user_id": user_id,
        "message_id": video_message.id
    }
    
    # Show upload instruction directly without options menu
    await callback_query.edit_message_text(
        "🎵 **Upload New Audio**\n\n"
        "Please send the audio file you want to replace the video audio with:\n\n"
        "**Supported formats:** MP3, M4A, WAV, FLAC\n\n"
        "Use /cancel to cancel."
    )

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

# Handle trim custom callback
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

# Handle screenshot custom callback
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
            "type": "custom_time",
            "video_message": video_message
        }
        
        await callback_query.edit_message_text(
            f"📸 **ᴄᴜsᴛᴏᴍ sᴄʀᴇᴇɴsʜᴏᴛ ᴛɪᴍᴇ**\n\n"
            f"**ᴠɪᴅᴇᴏ ᴅᴜʀᴀᴛɪᴏɴ:** {video_message.video.duration // 60}:{video_message.video.duration % 60:02d}\n\n"
            f"📝 sᴇɴᴅ ᴛʜᴇ ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs (ᴇ.ɢ., `120` ꜰᴏʀ 2 ᴍɪɴᴜᴛᴇs)\n\n"
            f"ᴏʀ ᴜsᴇ ᴍᴍ:ss ꜰᴏʀᴍᴀᴛ (ᴇ.ɢ., `2:30` ꜰᴏʀ 2 ᴍɪɴᴜᴛᴇs 30 sᴇᴄᴏɴᴅs)\n\n"
            f"**ᴍᴀx ᴛɪᴍᴇ:** {video_message.video.duration}s\n\n"
            f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
        )
        
    except Exception as e:
        logger.error(f"Error in screenshot custom callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Handle custom callbacks (watermark, subtitles, audio upload)
@Client.on_callback_query(filters.regex(r"^(watermark|subtitles|replace_audio)_"))
async def handle_custom_callbacks(client: Client, callback_query: CallbackQuery):
    """Handle custom callbacks for watermark, subtitles, and replace audio"""
    try:
        # Store the video info for later processing
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        if data.startswith("watermark_custom_"):
            message_id = int(data.split("_")[-1])
            await callback_query.edit_message_text(
                "💧 **ᴄᴜsᴛᴏᴍ ᴡᴀᴛᴇʀᴍᴀʀᴋ**\n\n"
                "ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴛᴇxᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴀs ᴡᴀᴛᴇʀᴍᴀʀᴋ:"
            )
        elif data.startswith("subtitles_custom_"):
            message_id = int(data.split("_")[-1])
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            # Store request for SRT upload
            subtitle_requests[user_id] = {
                "video_message": video_message,
                "user_id": user_id,
                "message_id": message_id
            }
            
            await callback_query.edit_message_text(
                "📄 **ᴄᴜsᴛᴏᴍ sᴜʙᴛɪᴛʟᴇs**\n\n"
                "ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ .sʀᴛ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ:\n\n"
                "**ꜰᴏʀᴍᴀᴛ:** .sʀᴛ ꜰɪʟᴇ ᴏɴʟʏ\n"
                "**ᴇɴᴄᴏᴅɪɴɢ:** ᴜᴛꜰ-8 ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ\n\n"
                "ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
            )
        elif data.startswith("replace_audio_upload_"):
            message_id = int(data.split("_")[-1])
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            # Store request for audio upload
            audio_replace_requests[user_id] = {
                "video_message": video_message,
                "user_id": user_id,
                "message_id": message_id
            }
            
            await callback_query.edit_message_text(
                "🎵 **ᴜᴘʟᴏᴀᴅ ɴᴇᴡ ᴀᴜᴅɪᴏ**\n\n"
                "ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴀᴜᴅɪᴏ ꜰɪʟᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴀᴜᴅɪᴏ ᴡɪᴛʜ:\n\n"
                "**sᴜᴘᴘᴏʀᴛᴇᴅ ꜰᴏʀᴍᴀᴛs:** ᴍᴘ3, ᴍ4ᴀ, ᴡᴀᴠ, ꜰʟᴀᴄ\n\n"
                "ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
            )
        
    except Exception as e:
        logger.error(f"Error in custom callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Store requests for file uploads
audio_replace_requests = {}
subtitle_requests = {}

# Handle audio file uploads for replace audio
@Client.on_message(filters.audio & filters.private)
async def handle_audio_upload(client: Client, message: Message):
    """Handle audio file uploads for replace audio"""
    try:
        user_id = message.from_user.id
        
        # Check if user has a pending audio replace request
        if user_id in audio_replace_requests:
            request_info = audio_replace_requests[user_id]
            del audio_replace_requests[user_id]  # Clean up request
            
            # Download the audio file
            import uuid
            audio_id = uuid.uuid4().hex
            audio_path = f"{Config.DOWNLOADS_DIR}/{audio_id}_audio.{message.audio.file_name.split('.')[-1] if message.audio.file_name else 'mp3'}"
            
            status_msg = await message.reply_text("🎵 **ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ ꜰɪʟᴇ...**")
            
            await client.download_media(message.audio, file_name=audio_path)
            
            # Store the audio file path for processing
            request_info["audio_file"] = audio_path
            
            # Start processing with the audio file
            await status_msg.edit_text("🎵 **ᴀᴜᴅɪᴏ ʀᴇᴄᴇɪᴠᴇᴅ! sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇssɪɴɢ...**")
            
            # Process replace audio with custom audio file
            video_message = request_info["video_message"]
            user_id = request_info["user_id"]
            
            # Ensure database is connected
            if not db._connected:
                await db.connect()
            
            # Create operation record
            operation_record = await db.add_operation(user_id, "replace_audio", "processing")
            
            # Start the processing
            await process_video(client, status_msg, video_message, "replace_audio", operation_record.inserted_id, audio_file=audio_path)
            
    except Exception as e:
        logger.error(f"Error handling audio upload: {e}")
        await message.reply_text("❌ **ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ᴀᴜᴅɪᴏ ꜰɪʟᴇ**")

# Handle document uploads for SRT files
@Client.on_message(filters.document & filters.private)
async def handle_document_upload(client: Client, message: Message):
    """Handle document uploads for SRT subtitle files"""
    try:
        user_id = message.from_user.id
        
        # Check if it's an SRT file and user has a pending subtitle request
        if (user_id in subtitle_requests and 
            message.document.file_name and 
            message.document.file_name.lower().endswith('.srt')):
            
            request_info = subtitle_requests[user_id]
            del subtitle_requests[user_id]  # Clean up request
            
            # Download the SRT file
            import uuid
            srt_id = uuid.uuid4().hex
            srt_path = f"{Config.DOWNLOADS_DIR}/{srt_id}_subtitles.srt"
            
            status_msg = await message.reply_text("📄 **ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ...**")
            
            await client.download_media(message.document, file_name=srt_path)
            
            # Start processing with the SRT file
            await status_msg.edit_text("📄 **sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ! sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇssɪɴɢ...**")
            
            # Process subtitles with custom SRT file
            video_message = request_info["video_message"]
            user_id = request_info["user_id"]
            
            # Ensure database is connected
            if not db._connected:
                await db.connect()
            
            # Create operation record
            operation_record = await db.add_operation(user_id, "subtitles", "processing")
            
            # Start the processing
            await process_video(client, status_msg, video_message, "subtitles", operation_record.inserted_id, srt_file=srt_path)
            
    except Exception as e:
        logger.error(f"Error handling document upload: {e}")
        await message.reply_text("❌ **ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ sᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ**")

# Handle image uploads for watermark
@Client.on_message(filters.photo & filters.private)
async def handle_image_upload(client: Client, message: Message):
    """Handle image uploads for watermark"""
    try:
        user_id = message.from_user.id
        
        # Check if user has a pending image watermark request
        if user_id in watermark_requests and watermark_requests[user_id]["type"] == "image":
            request_info = watermark_requests[user_id]
            del watermark_requests[user_id]  # Clean up request
            
            # Download the image
            import uuid
            image_id = uuid.uuid4().hex
            image_path = f"{Config.DOWNLOADS_DIR}/{image_id}_watermark.jpg"
            
            status_msg = await message.reply_text("🖼️ **ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ...**")
            
            await client.download_media(message.photo, file_name=image_path)
            
            # Start processing with the image watermark
            await status_msg.edit_text("🖼️ **ɪᴍᴀɢᴇ ʀᴇᴄᴇɪᴠᴇᴅ! sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇssɪɴɢ...**")
            
            # Process watermark with custom image
            video_message = request_info["video_message"]
            user_id = request_info["user_id"] if "user_id" in request_info else user_id
            
            # Ensure database is connected
            if not db._connected:
                await db.connect()
            
            # Create operation record
            operation_record = await db.add_operation(user_id, "watermark", "processing")
            
            # Process video with image watermark - use specific watermark function
            process_id = str(uuid.uuid4())
            
            # Download video first
            video_path = await client.download_media(
                video_message.video,
                file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_{video_message.video.file_name or 'video.mp4'}"
            )
            
            # Apply image watermark
            from helpers.watermark import WatermarkProcessor
            watermark_processor = WatermarkProcessor()
            output_path = await watermark_processor.add_image_watermark(
                video_path, 
                f"{Config.UPLOADS_DIR}/{process_id}_image_watermark.mp4", 
                image_path
            )
            
            if output_path and os.path.exists(output_path):
                # Send the processed video
                await client.send_video(
                    user_id,
                    output_path,
                    caption="✅ **ɪᴍᴀɢᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴀᴅᴅᴇᴅ**"
                )
                
                # Update operation status
                await db.update_operation(operation_record.inserted_id, {"status": "completed"})
                
                # Clean up files
                from helpers.downloader import FileCleanup
                FileCleanup.cleanup_files([video_path, image_path, output_path], delay_seconds=30)
            else:
                await status_msg.edit_text("❌ **ᴡᴀᴛᴇʀᴍᴀʀᴋ ꜰᴀɪʟᴇᴅ**")
                await db.update_operation(operation_record.inserted_id, {"status": "failed"})
            
    except Exception as e:
        logger.error(f"Error handling image upload: {e}")
        await message.reply_text("❌ **ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ ꜰɪʟᴇ**")

async def process_video(client: Client, reply_message: Message, video_message: Message, operation: str, operation_id, audio_file: str = None, srt_file: str = None):
    """Process video with selected operation"""
    try:
        user_id = reply_message.chat.id

        # Create unique process ID
        process_id = str(uuid.uuid4())

        # Initialize progress tracker
        progress_tracker = ProgressTracker(client)

        # Create progress message
        progress_msg = await reply_message.edit_text(
            f"🎬 **ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
            f"📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ..."
        )

        # Start progress tracking for download
        await progress_tracker.start_progress(
            user_id,
            progress_msg.id,
            f"Downloading {operation.replace('_', ' ').title()}",
            video_message.video.file_size,
            f"{process_id}_download"
        )

        # Download video with progress tracking
        async def download_progress(current: int, total: int):
            await progress_tracker.update_progress(f"{process_id}_download", current)

        video_path = await client.download_media(
            video_message.video,
            file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_{video_message.video.file_name or 'video.mp4'}",
            progress=download_progress
        )

        # Complete download progress
        await progress_tracker.complete_progress(f"{process_id}_download", True)

        # Start processing progress
        await progress_tracker.start_progress(
            user_id,
            progress_msg.id,
            f"Processing {operation.replace('_', ' ').title()}",
            video_message.video.file_size,
            f"{process_id}_process"
        )

        # Process video with proper error handling
        ffmpeg_processor = FFmpegProcessor()
        try:
            # Prepare parameters for processing
            params = {}
            if audio_file:
                params["audio_file"] = audio_file
            if srt_file:
                params["srt_file"] = srt_file
                params["type"] = "custom"
            
            if params:
                # Use specific processing method for operations with parameters
                if operation == "replace_audio":
                    output_path = await ffmpeg_processor.replace_audio(video_path, f"{Config.UPLOADS_DIR}/{process_id}_replace_audio.mp4", progress_tracker, params)
                elif operation == "subtitles":
                    output_path = await ffmpeg_processor.add_subtitles(video_path, f"{Config.UPLOADS_DIR}/{process_id}_subtitles.mp4", progress_tracker, params)
                else:
                    output_path = await ffmpeg_processor.process_video(video_path, operation, process_id, progress_tracker)
            else:
                output_path = await ffmpeg_processor.process_video(video_path, operation, process_id, progress_tracker)
                
        except Exception as e:
            logger.error(f"FFmpeg processing error: {e}")
            await progress_msg.edit_text("❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**\n\nᴇʀʀᴏʀ ɪɴ ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssɪɴɢ")
            await db.update_operation(operation_id, {"status": "failed"})
            return

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
            # Check if multiple screenshots were generated
            if isinstance(output_path, list):
                # Multiple screenshots
                await progress_msg.edit_text(
                    f"📸 **sᴄʀᴇᴇɴsʜᴏᴛs ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                    f"📤 sᴇɴᴅɪɴɢ {len(output_path)} sᴄʀᴇᴇɴsʜᴏᴛs..."
                )

                for i, screenshot_path in enumerate(output_path):
                    try:
                        await client.send_photo(
                            user_id,
                            screenshot_path,
                            caption=f"📸 sᴄʀᴇᴇɴsʜᴏᴛ {i+1}/{len(output_path)}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send screenshot {i+1}: {e}")
            else:
                # Single screenshot
                await client.send_photo(
                    user_id,
                    output_path,
                    caption=f"📸 **sᴄʀᴇᴇɴsʜᴏᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}"
                )
        elif operation.startswith("extract_audio"):
            # Send as audio
            await client.send_audio(
                user_id,
                output_path,
                caption=f"🎵 **ᴀᴜᴅɪᴏ ᴇxᴛʀᴀᴄᴛᴇᴅ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}"
            )
        else:
            # Send as video
            # Upload to media channel first
            if Config.MEDIA_CHANNEL_ID:
                try:
                    media_msg = await client.send_video(
                        Config.MEDIA_CHANNEL_ID,
                        output_path,
                        caption=f"ᴘʀᴏᴄᴇssᴇᴅ ᴠɪᴅᴇᴏ - {operation.replace('_', ' ').title()}"
                    )

                    # Forward to user
                    await media_msg.forward(user_id)

                except Exception as e:
                    logger.error(f"Failed to upload to media channel: {e}")
                    # Send directly to user
                    await client.send_video(
                        user_id,
                        output_path,
                        caption=f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}"
                    )
            else:
                # Send directly to user with thumbnail if available
                from plugins.thumbnail import get_user_thumbnail
                thumbnail_path = get_user_thumbnail(user_id)

                await client.send_video(
                    user_id,
                    output_path,
                    caption=f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}",
                    thumb=thumbnail_path
                )

        # Update operation status
        await db.update_operation(operation_id, {"status": "completed"})

        # Log to log channel
        if Config.LOG_CHANNEL_ID:
            try:
                log_text = f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                log_text += f"**ᴜsᴇʀ:** `{user_id}`\n"
                log_text += f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n"
                log_text += f"**ᴄʀᴇᴅɪᴛs ᴜsᴇᴅ:** {Config.PROCESS_COST}"

                await client.send_message(Config.LOG_CHANNEL_ID, log_text)
            except Exception as e:
                logger.error(f"Failed to log operation: {e}")

        # Enhanced file cleanup with delay to ensure upload completion
        cleanup_files = [video_path]
        
        # Handle cleanup for multiple screenshots
        if isinstance(output_path, list):
            cleanup_files.extend(output_path)
        else:
            cleanup_files.append(output_path)
        
        # Schedule cleanup after 30 seconds to ensure upload completion
        FileCleanup.cleanup_files(cleanup_files, delay_seconds=30)

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await db.update_operation(operation_id, {"status": "failed"})
        try:
            await client.send_message(
                user_id,
                f"❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**\n\n"
                f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.replace('_', ' ').title()}\n\n"
                f"ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ."
            )
        except:
            pass

async def handle_merge_collection(client: Client, message: Message, user_id: int):
    """Handle video collection for merge operation"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        collection = merge_collections[user_id]

        # Check user privileges for limits
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS

        # Set limits based on user type
        max_videos = 20 if (is_premium or is_admin) else 10

        # Check if user has reached limit
        if len(collection["videos"]) >= max_videos:
            await message.reply_text(
                f"⚠️ **ᴠɪᴅᴇᴏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ**\n\n"
                f"{'ᴘʀᴇᴍɪᴜᴍ' if is_premium else 'ꜰʀᴇᴇ'} ᴜsᴇʀs ᴄᴀɴ ᴍᴇʀɢᴇ ᴜᴘ ᴛᴏ {max_videos} ᴠɪᴅᴇᴏs.\n\n"
                f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴏʀ ᴄᴏɴᴛɪɴᴜᴇ ᴡɪᴛʜ ᴄᴜʀʀᴇɴᴛ ᴠɪᴅᴇᴏs."
            )
            return

        # Add video to collection
        collection["videos"].append({
            "message_id": message.id,
            "file_name": message.video.file_name or f"video_{len(collection['videos']) + 1}.mp4",
            "file_size": message.video.file_size,
            "duration": message.video.duration
        })

        # Create keyboard for next actions
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴘʀᴏᴄᴇss ᴍᴇʀɢᴇ", callback_data=f"merge_process_{user_id}"),
                InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴏʀᴇ", callback_data=f"merge_continue_{user_id}")
            ],
            [
                InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"merge_cancel_{user_id}")
            ]
        ])

        # Update status message
        video_count = len(collection["videos"])
        total_size = sum(v["file_size"] for v in collection["videos"]) / (1024*1024)

        status_text = f"🔗 **ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏs ᴄᴏʟʟᴇᴄᴛɪᴏɴ**\n\n"
        status_text += f"📹 **ᴠɪᴅᴇᴏs ᴄᴏʟʟᴇᴄᴛᴇᴅ:** {video_count}/{max_videos}\n"
        status_text += f"📦 **ᴛᴏᴛᴀʟ sɪᴢᴇ:** {total_size:.1f} ᴍʙ\n\n"

        for i, video in enumerate(collection["videos"], 1):
            status_text += f"{i}. {video['file_name']} ({video['file_size']/(1024*1024):.1f}ᴍʙ)\n"

        status_text += f"\n✅ ᴀᴅᴅᴇᴅ: {message.video.file_name or 'ᴠɪᴅᴇᴏ'}\n\n"
        status_text += "ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ɴᴇxᴛ ᴀᴄᴛɪᴏɴ:"

        await message.reply_text(status_text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error in merge collection: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴀᴅᴅɪɴɢ ᴠɪᴅᴇᴏ ᴛᴏ ᴍᴇʀɢᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ.")

async def process_merge_collection(client: Client, callback_query: CallbackQuery, user_id: int):
    """Process the collected videos for merge"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        collection = merge_collections[user_id]

        # Check if we have at least 2 videos
        if len(collection["videos"]) < 2:
            await callback_query.answer("❌ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2 ᴠɪᴅᴇᴏs ᴛᴏ ᴍᴇʀɢᴇ", show_alert=True)
            return

        # Check user privileges for credit/limit bypass
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS

        # Check credits and daily limits for non-privileged users
        if not is_premium and not is_admin:
            user = await db.get_user(user_id)
            if user["credits"] < Config.PROCESS_COST:
                await callback_query.answer("❌ ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs", show_alert=True)
                return

            if not await db.check_daily_limit(user_id):
                await callback_query.answer("❌ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ", show_alert=True)
                return

        # Create operation record
        operation_record = await db.add_operation(user_id, "merge", "processing")

        # Deduct credits and update daily usage for non-privileged users
        if not is_premium and not is_admin:
            await db.deduct_credits(user_id, Config.PROCESS_COST)
            await db.increment_daily_usage(user_id)

        # Start merge processing
        await callback_query.edit_message_text(
            f"🔗 **ᴘʀᴏᴄᴇssɪɴɢ ᴍᴇʀɢᴇ**\n\n"
            f"📹 **ᴠɪᴅᴇᴏs:** {len(collection['videos'])}\n\n"
            f"📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀɴᴅ ᴘʀᴏᴄᴇssɪɴɢ..."
        )

        # Get all video messages
        video_paths = []
        for video_info in collection["videos"]:
            video_msg = await client.get_messages(callback_query.message.chat.id, video_info["message_id"])
            if video_msg.video:
                # Download video
                process_id = str(uuid.uuid4())
                video_path = await client.download_media(
                    video_msg.video,
                    file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_{video_info['file_name']}"
                )
                video_paths.append(video_path)

        if len(video_paths) < 2:
            await callback_query.edit_message_text("❌ **ᴍᴇʀɢᴇ ꜰᴀɪʟᴇᴅ**\n\nᴄᴏᴜʟᴅɴ'ᴛ ᴅᴏᴡɴʟᴏᴀᴅ ᴀʟʟ ᴠɪᴅᴇᴏs.")
            await db.update_operation(operation_record.inserted_id, {"status": "failed"})
            return

        # Process merge using FFmpeg
        ffmpeg_processor = FFmpegProcessor()
        process_id = str(uuid.uuid4())
        output_path = await ffmpeg_processor.merge_multiple_videos(video_paths, process_id)

        if not output_path or not os.path.exists(output_path):
            await callback_query.edit_message_text("❌ **ᴍᴇʀɢᴇ ꜰᴀɪʟᴇᴅ**\n\nᴇʀʀᴏʀ ᴅᴜʀɪɴɢ ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssɪɴɢ.")
            await db.update_operation(operation_record.inserted_id, {"status": "failed"})
            return

        # Get merged video info
        import subprocess
        try:
            result = subprocess.run([
                Config.FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', output_path
            ], capture_output=True, text=True)

            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                duration = float(video_info['format']['duration'])
                file_size = os.path.getsize(output_path)
                duration_formatted = f"{int(duration // 60)}:{int(duration % 60):02d}"
                size_mb = file_size / (1024 * 1024)
            else:
                duration_formatted = "Unknown"
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
        except:
            duration_formatted = "Unknown"
            size_mb = os.path.getsize(output_path) / (1024 * 1024)

        # Ask for file format and name
        format_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📱 sᴇɴᴅ ᴀs ᴠɪᴅᴇᴏ", callback_data=f"merge_send_video_{process_id}"),
                InlineKeyboardButton("📎 sᴇɴᴅ ᴀs ꜰɪʟᴇ", callback_data=f"merge_send_file_{process_id}")
            ]
        ])

        await callback_query.edit_message_text(
            f"✅ **ᴍᴇʀɢᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"📹 **ᴠɪᴅᴇᴏs ᴍᴇʀɢᴇᴅ:** {len(collection['videos'])}\n"
            f"⏱️ **ᴅᴜʀᴀᴛɪᴏɴ:** {duration_formatted}\n"
            f"📦 **sɪᴢᴇ:** {size_mb:.1f} ᴍʙ\n\n"
            f"ᴄʜᴏᴏsᴇ ʜᴏᴡ ᴛᴏ sᴇɴᴅ:",
            reply_markup=format_keyboard
        )

        # Store merge info for callback
        merge_collections[f"result_{process_id}"] = {
            "output_path": output_path,
            "user_id": user_id,
            "operation_id": operation_record.inserted_id,
            "video_count": len(collection['videos']),
            "duration": duration_formatted,
            "size_mb": size_mb
        }

        # Clear user's merge collection but keep result
        del merge_collections[user_id]

        # Clean up source videos
        try:
            for path in video_paths:
                os.remove(path)
        except:
            pass

    except Exception as e:
        logger.error(f"Error processing merge collection: {e}")
        await callback_query.edit_message_text("❌ **ᴍᴇʀɢᴇ ꜰᴀɪʟᴇᴅ**\n\nᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.")
        if user_id in merge_collections:
            del merge_collections[user_id]

# Handle back button callbacks
@Client.on_callback_query(filters.regex(r"^back_to_options_"))
async def handle_back_to_options(client: Client, callback_query: CallbackQuery):
    """Handle back to options callbacks"""
    try:
        # Extract message ID from callback data
        message_id = int(callback_query.data.split("_")[-1])

        # Get original video message
        video_message = await client.get_messages(callback_query.message.chat.id, message_id)
        if not video_message.video:
            await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Recreate the main options keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✂️ ᴛʀɪᴍ ᴠɪᴅᴇᴏ", callback_data=f"option_trim_{message_id}"),
                InlineKeyboardButton("🗜️ ᴄᴏᴍᴘʀᴇss", callback_data=f"option_compress_{message_id}")
            ],
            [
                InlineKeyboardButton("🔄 ʀᴏᴛᴀᴛᴇ", callback_data=f"option_rotate_{message_id}"),
                InlineKeyboardButton("🔗 ᴍᴇʀɢᴇ", callback_data=f"option_merge_{message_id}")
            ],
            [
                InlineKeyboardButton("💧 ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data=f"option_watermark_{message_id}"),
                InlineKeyboardButton("🔇 ᴍᴜᴛᴇ", callback_data=f"option_mute_{message_id}")
            ],
            [
                InlineKeyboardButton("🎵 ʀᴇᴘʟᴀᴄᴇ ᴀᴜᴅɪᴏ", callback_data=f"option_replace_audio_{message_id}"),
                InlineKeyboardButton("⏮️ ʀᴇᴠᴇʀsᴇ", callback_data=f"option_reverse_{message_id}")
            ],
            [
                InlineKeyboardButton("📝 sᴜʙᴛɪᴛʟᴇs", callback_data=f"option_subtitles_{message_id}"),
                InlineKeyboardButton("📏 ʀᴇsᴏʟᴜᴛɪᴏɴ", callback_data=f"option_resolution_{message_id}")
            ],
            [
                InlineKeyboardButton("🎶 ᴇxᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ", callback_data=f"option_extract_audio_{message_id}"),
                InlineKeyboardButton("📸 sᴄʀᴇᴇɴsʜᴏᴛ", callback_data=f"option_screenshot_{message_id}")
            ]
        ])

        video_info = f"📹 **ᴠɪᴅᴇᴏ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
        video_info += f"**ꜰɪʟᴇ ɴᴀᴍᴇ:** {video_message.video.file_name or 'Unknown'}\n"
        video_info += f"**sɪᴢᴇ:** {video_message.video.file_size / (1024*1024):.2f} ᴍʙ\n"
        video_info += f"**ᴅᴜʀᴀᴛɪᴏɴ:** {video_message.video.duration // 60}:{video_message.video.duration % 60:02d}\n"
        video_info += f"**ʀᴇsᴏʟᴜᴛɪᴏɴ:** {video_message.video.width}x{video_message.video.height}\n\n"
        video_info += "ᴄʜᴏᴏsᴇ ᴀ ᴘʀᴏᴄᴇssɪɴɢ ᴏᴘᴛɪᴏɴ:"

        await callback_query.edit_message_text(video_info, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error in back to options: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Store watermark requests temporarily
watermark_requests = {}

# Store screenshot requests temporarily
screenshot_requests = {}

# Store trim requests temporarily
trim_requests = {}

# Handle watermark specific callbacks
@Client.on_callback_query(filters.regex(r"^watermark_"))
async def handle_watermark_callback(client: Client, callback_query: CallbackQuery):
    """Handle watermark specific callbacks"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data.startswith("watermark_custom_"):
            message_id = int(data.split("_")[-1])
            # Ask for custom text input
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            watermark_requests[user_id] = {
                "type": "custom_text", 
                "message_id": message_id,
                "video_message": video_message
            }
            
            await callback_query.edit_message_text(
                f"💧 **ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ**\n\n"
                f"📝 **What text or logo do you want to add as watermark?**\n\n"
                f"Please send me the text you want to use. It will be displayed as a watermark on your video.\n\n"
                f"**Example:** Your Channel Name, @username, or any custom text\n\n"
                f"Use /cancel to cancel this operation.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"back_to_options_{video_message.id}")
                ]])
            )
            
        elif data.startswith("watermark_image_"):
            message_id = int(data.split("_")[-1])
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            
            # Ask for image input
            watermark_requests[user_id] = {
                "type": "image",
                "message_id": message_id,
                "video_message": video_message
            }
            
            await callback_query.edit_message_text(
                f"🖼️ **ɪᴍᴀɢᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ**\n\n"
                f"📷 **What image or logo do you want to attach as watermark?**\n\n"
                f"Please send me the image you want to use as a watermark. This image will be overlaid on your video.\n\n"
                f"**Supported formats:** JPG, PNG, WEBP\n"
                f"**Recommended:** PNG with transparent background for best results\n\n"
                f"Use /cancel to cancel this operation.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"back_to_options_{video_message.id}")
                ]])
            )
            
        else:
            await callback_query.answer("❌ ᴜɴᴋɴᴏᴡɴ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴏᴘᴛɪᴏɴ", show_alert=True)

    except Exception as e:
        logger.error(f"Error in watermark callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Handle text input for watermarks and custom trim
@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "cancel", "credits", "referral", "premium", "sample", "admin"]))
async def handle_text_input(client: Client, message: Message):
    """Handle text input for watermark and trim time requests"""
    try:
        user_id = message.from_user.id
        
        # Handle watermark text input
        if user_id in watermark_requests:
            request = watermark_requests[user_id]
            
            if request["type"] in ["text", "custom_text"]:
                # Process text watermark
                watermark_text = message.text.strip()
                
                if len(watermark_text) > 50:
                    await message.reply_text(
                        "❌ **Text too long**\n\n"
                        "Please keep your watermark text under 50 characters."
                    )
                    return
                
                # Get video message
                video_message = request["video_message"]
                
                # Clean up request
                del watermark_requests[user_id]
                
                await message.reply_text(
                    f"💧 **Text watermark received**\n\n"
                    f"**Text:** {watermark_text}\n\n"
                    f"⏳ Processing your video with text watermark..."
                )
                
                # Start processing with custom text watermark
                await start_watermark_processing(client, message, video_message, "text", watermark_text)
        
        # Handle screenshot custom time input
        elif user_id in screenshot_requests:
            request = screenshot_requests[user_id]
            
            if request["type"] == "custom_time":
                # Process custom time for screenshot
                time_text = message.text.strip()
                
                try:
                    # Parse time input (supports formats like "30", "1:30", "90")
                    if ":" in time_text:
                        # Format: MM:SS
                        parts = time_text.split(":")
                        if len(parts) == 2:
                            minutes = int(parts[0])
                            seconds = int(parts[1])
                            total_seconds = minutes * 60 + seconds
                        else:
                            raise ValueError("Invalid time format")
                    else:
                        # Format: seconds only
                        total_seconds = int(time_text)
                    
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
                    
                    await message.reply_text(
                        f"📸 **ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
                        f"**ᴛɪᴍᴇ:** {total_seconds}s ({total_seconds // 60}:{total_seconds % 60:02d})\n\n"
                        f"⏳ ᴛᴀᴋɪɴɢ sᴄʀᴇᴇɴsʜᴏᴛ..."
                    )
                    
                    await start_processing_with_params(client, message, video_message, "screenshot", {"custom_time": total_seconds})
                    
                except ValueError:
                    await message.reply_text(
                        "❌ **ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ**\n\n"
                        "ᴘʟᴇᴀsᴇ ᴜsᴇ ᴏɴᴇ ᴏꜰ ᴛʜᴇsᴇ ꜰᴏʀᴍᴀᴛs:\n"
                        "• `30` (30 sᴇᴄᴏɴᴅs)\n"
                        "• `1:30` (1 ᴍɪɴᴜᴛᴇ 30 sᴇᴄᴏɴᴅs)\n"
                        "• `90` (90 sᴇᴄᴏɴᴅs)"
                    )
        
        # Handle trim custom time input
        elif user_id in trim_requests:
            request = trim_requests[user_id]
            
            if request["type"] == "custom_trim":
                # Process custom duration for trim
                duration_text = message.text.strip()
                
                try:
                    # Parse duration input (supports formats like "30", "1:30", "90")
                    if ":" in duration_text:
                        # Format: MM:SS
                        parts = duration_text.split(":")
                        if len(parts) == 2:
                            minutes = int(parts[0])
                            seconds = int(parts[1])
                            total_seconds = minutes * 60 + seconds
                        else:
                            raise ValueError("Invalid duration format")
                    else:
                        # Format: seconds only
                        total_seconds = int(duration_text)
                    
                    # Validate duration range
                    video_message = request["video_message"]
                    video_duration = video_message.video.duration
                    
                    if total_seconds <= 0 or total_seconds > video_duration:
                        await message.reply_text(
                            f"❌ **Invalid duration**\n\n"
                            f"Please enter a duration between 1 and {video_duration} seconds."
                        )
                        return
                    
                    # Clean up request
                    del trim_requests[user_id]
                    
                    await message.reply_text(
                        f"✂️ **Custom duration received**\n\n"
                        f"**Duration:** {total_seconds}s ({total_seconds // 60}:{total_seconds % 60:02d})\n\n"
                        f"⏳ Trimming your video..."
                    )
                    
                    # Start processing with custom trim duration
                    await start_trim_processing(client, message, video_message, total_seconds)
                    
                except ValueError:
                    await message.reply_text(
                        "❌ **Invalid duration format**\n\n"
                        "Please use one of these formats:\n"
                        "• `30` (30 seconds)\n"
                        "• `2:30` (2 minutes 30 seconds)\n"
                        "• `120` (120 seconds)"
                    )
    
    except Exception as e:
        logger.error(f"Error handling text input: {e}")

# Handle image input for watermarks  
@Client.on_message(filters.photo & filters.private & ~filters.command("setthumbnail"))
async def handle_watermark_image_input(client: Client, message: Message):
    """Handle image input for watermark requests"""
    try:
        user_id = message.from_user.id
        
        if user_id not in watermark_requests:
            return
        
        request = watermark_requests[user_id]
        
        if request["type"] == "image":
            # Download the image for watermark
            await message.reply_text("📥 **Downloading image...**")
            
            # Download image
            process_id = str(uuid.uuid4())
            image_path = await client.download_media(
                message.photo,
                file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_watermark.jpg"
            )
            
            if not image_path:
                await message.reply_text("❌ **Failed to download image**")
                return
            
            # Get video message
            video_message = request["video_message"]
            
            # Clean up request
            del watermark_requests[user_id]
            
            await message.reply_text(
                f"🖼️ **Image watermark received**\n\n"
                f"⏳ Processing your video with image watermark..."
            )
            
            # Start processing with image watermark
            await start_watermark_processing(client, message, video_message, "image", image_path)
    
    except Exception as e:
        logger.error(f"Error handling watermark image input: {e}")

async def start_processing_with_params(client: Client, message: Message, video_message: Message, operation: str, params: dict):
    """Start video processing with additional parameters"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        user_id = message.from_user.id

        # Get user
        user = await db.get_user(user_id)
        if not user:
            await message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            return

        # Check if user is banned
        if await db.is_user_banned(user_id):
            await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ")
            return

        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin

        # Check credits only for non-privileged users
        if not bypass_limits and user.get("credits", 0) < Config.PROCESS_COST:
            await message.reply_text(
                f"❌ **ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs**\n\n"
                f"ʏᴏᴜ ɴᴇᴇᴅ {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ʙᴜᴛ ʜᴀᴠᴇ {user.get('credits', 0)}"
            )
            return

        # Check daily limit only for non-privileged users
        if not bypass_limits and not await db.check_daily_limit(user_id):
            await message.reply_text("⏰ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ")
            return

        # Create operation record
        operation_record = await db.add_operation(user_id, operation.split(":")[0], "processing")
        operation_id = operation_record.inserted_id

        # Deduct credits and update daily usage only for non-privileged users
        if not bypass_limits:
            await db.deduct_credits(user_id, Config.PROCESS_COST)
            await db.increment_daily_usage(user_id)

        # Start processing
        process_id = str(uuid.uuid4())
        
        # Download video with aria2c if available
        downloader = Aria2Downloader()
        if downloader.check_aria2_installed():
            logger.info("Using aria2c for faster download")
        
        status_message = await message.reply_text(
            f"⚡ **ᴘʀᴏᴄᴇssɪɴɢ sᴛᴀʀᴛᴇᴅ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.split(':')[0].replace('_', ' ').title()}\n"
            f"**ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴇᴛʜᴏᴅ:** {'aria2c (ꜰᴀsᴛ)' if downloader.check_aria2_installed() else 'sᴛᴀɴᴅᴀʀᴅ'}\n\n"
            f"📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ..."
        )

        # Download video with enhanced progress tracking
        video_path = await client.download_media(
            video_message.video,
            file_name=f"{Config.DOWNLOADS_DIR}/{process_id}_{video_message.video.file_name or 'video.mp4'}"
        )

        if not video_path:
            await status_message.edit_text("❌ **ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ**")
            await db.update_operation(operation_id, {"status": "failed"})
            return

        # Update status
        await status_message.edit_text(
            f"⚡ **ᴘʀᴏᴄᴇssɪɴɢ**\n\n"
            f"**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.split(':')[0].replace('_', ' ').title()}\n\n"
            f"🎬 ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ..."
        )

        # Process video
        ffmpeg_processor = FFmpegProcessor()
        
        if operation.startswith("watermark_text:"):
            # Text watermark
            watermark_processor = WatermarkProcessor()
            output_path = await watermark_processor.add_text_watermark(
                video_path,
                f"{Config.UPLOADS_DIR}/{process_id}_watermark_text.mp4",
                params["text"],
                large_colorful=True
            )
        elif operation.startswith("watermark_image:"):
            # Image watermark  
            watermark_processor = WatermarkProcessor()
            output_path = await watermark_processor.add_image_watermark(
                video_path,
                f"{Config.UPLOADS_DIR}/{process_id}_watermark_image.mp4",
                params["image_path"]
            )
        elif operation == "watermark":
            # Handle generic watermark operation with params
            watermark_processor = WatermarkProcessor()
            if params.get("type") == "image":
                output_path = await watermark_processor.add_image_watermark(
                    video_path,
                    f"{Config.UPLOADS_DIR}/{process_id}_watermark_image.mp4",
                    params["image_path"]
                )
            elif params.get("type") in ["text", "custom_text"]:
                output_path = await watermark_processor.add_text_watermark(
                    video_path,
                    f"{Config.UPLOADS_DIR}/{process_id}_watermark_text.mp4",
                    params["text"],
                    large_colorful=True
                )
            else:
                output_path = None
        else:
            # Use FFmpeg processor for other operations
            output_path = await ffmpeg_processor.process_video(video_path, operation, process_id)

        if not output_path or not os.path.exists(output_path):
            await status_message.edit_text("❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**")
            await db.update_operation(operation_id, {"status": "failed"})
            return

        # Upload result
        await status_message.edit_text(
            f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"📤 ᴜᴘʟᴏᴀᴅɪɴɢ ʀᴇsᴜʟᴛ..."
        )

        # Send result with thumbnail if available
        from plugins.thumbnail import get_user_thumbnail
        thumbnail_path = get_user_thumbnail(user_id)

        await client.send_video(
            user_id,
            output_path,
            caption=f"✅ **ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n**ᴏᴘᴇʀᴀᴛɪᴏɴ:** {operation.split(':')[0].replace('_', ' ').title()}",
            thumb=thumbnail_path
        )

        # Update operation status
        await db.update_operation(operation_id, {"status": "completed"})

        # Enhanced file cleanup including watermark images
        cleanup_files = [video_path, output_path]
        if "image_path" in params:
            cleanup_files.append(params["image_path"])
        
        FileCleanup.cleanup_files(cleanup_files, delay_seconds=30)

    except Exception as e:
        logger.error(f"Error in processing with params: {e}")
        await message.reply_text("❌ **ᴘʀᴏᴄᴇssɪɴɢ ꜰᴀɪʟᴇᴅ**")

# Store screenshot requests temporarily
screenshot_requests = {}

# Handle screenshot specific callbacks
@Client.on_callback_query(filters.regex(r"^screenshot_"))
async def handle_screenshot_callback(client: Client, callback_query: CallbackQuery):
    """Handle screenshot specific callbacks"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data.startswith("screenshot_custom_"):
            message_id = int(data.split("_")[-1])
            # Ask for custom time input
            screenshot_requests[user_id] = {
                "type": "custom_time",
                "message_id": message_id,
                "video_message": await client.get_messages(callback_query.message.chat.id, message_id)
            }
            
            # Get video duration for reference
            video_message = screenshot_requests[user_id]["video_message"]
            duration = video_message.video.duration
            
            await callback_query.edit_message_text(
                f"📸 **ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇ sᴄʀᴇᴇɴsʜᴏᴛ**\n\n"
                f"📹 **ᴠɪᴅᴇᴏ ᴅᴜʀᴀᴛɪᴏɴ:** {duration // 60}:{duration % 60:02d}\n\n"
                f"⏰ ɴᴏᴡ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ᴛɪᴍᴇ (ɪɴ sᴇᴄᴏɴᴅs) ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛᴀᴋᴇ ᴛʜᴇ sᴄʀᴇᴇɴsʜᴏᴛ.\n\n"
                f"**ᴇxᴀᴍᴘʟᴇs:**\n"
                f"• `30` - ᴀᴛ 30 sᴇᴄᴏɴᴅs\n"
                f"• `1:30` - ᴀᴛ 1 ᴍɪɴᴜᴛᴇ 30 sᴇᴄᴏɴᴅs\n"
                f"• `90` - ᴀᴛ 90 sᴇᴄᴏɴᴅs\n\n"
                f"**ᴠᴀʟɪᴅ ʀᴀɴɢᴇ:** 0 - {duration} sᴇᴄᴏɴᴅs\n\n"
                f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ."
            )
        else:
            await callback_query.answer("❌ ᴜɴᴋɴᴏᴡɴ sᴄʀᴇᴇɴsʜᴏᴛ ᴏᴘᴛɪᴏɴ", show_alert=True)

    except Exception as e:
        logger.error(f"Error in screenshot callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# Handle merge specific callbacks
@Client.on_callback_query(filters.regex(r"^merge_"))
async def handle_merge_callback(client: Client, callback_query: CallbackQuery):
    """Handle merge specific callbacks"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id

        if data.startswith("merge_wait_"):
            message_id = int(data.split("_")[-1])

            # Get user info for limits
            is_premium = await db.is_user_premium(user_id)
            is_admin = user_id in Config.ADMINS
            max_videos = 20 if (is_premium or is_admin) else 10

            # Initialize merge collection
            merge_collections[user_id] = {
                "videos": [{
                    "message_id": message_id,
                    "file_name": "First Video",
                    "file_size": 0,  # Will be updated when processing
                    "duration": 0
                }],
                "started_at": callback_query.message.date
            }

            await callback_query.edit_message_text(
                f"🔗 **ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏs ᴄᴏʟʟᴇᴄᴛɪᴏɴ**\n\n"
                f"✅ ꜰɪʀsᴛ ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ ᴛᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ\n\n"
                f"📤 ɴᴏᴡ sᴇɴᴅ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴠɪᴅᴇᴏs ᴛᴏ ᴍᴇʀɢᴇ.\n"
                f"{'ᴘʀᴇᴍɪᴜᴍ' if is_premium else 'ꜰʀᴇᴇ'} ᴜsᴇʀs ᴄᴀɴ ᴍᴇʀɢᴇ ᴜᴘ ᴛᴏ {max_videos} ᴠɪᴅᴇᴏs.\n\n"
                f"ᴜsᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴀᴛ ᴀɴʏ ᴛɪᴍᴇ."
            )

        elif data.startswith("merge_process_"):
            # Process the collected videos
            if user_id in merge_collections:
                await process_merge_collection(client, callback_query, user_id)
            else:
                await callback_query.answer("❌ ɴᴏ ᴠɪᴅᴇᴏs ɪɴ ᴄᴏʟʟᴇᴄᴛɪᴏɴ", show_alert=True)

        elif data.startswith("merge_continue_"):
            # Just acknowledge, user can send more videos
            await callback_query.answer("📤 sᴇɴᴅ ᴍᴏʀᴇ ᴠɪᴅᴇᴏs ᴛᴏ ᴀᴅᴅ ᴛᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ")

        elif data.startswith("merge_cancel_"):
            # Cancel merge collection
            if user_id in merge_collections:
                del merge_collections[user_id]
            await callback_query.edit_message_text(
                "❌ **ᴍᴇʀɢᴇ ᴄᴀɴᴄᴇʟʟᴇᴅ**\n\n"
                "ᴠɪᴅᴇᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ."
            )

        elif data.startswith("merge_send_video_") or data.startswith("merge_send_file_"):
            # Handle sending merged video
            process_id = data.split("_")[-1]
            result_key = f"result_{process_id}"

            if result_key not in merge_collections:
                await callback_query.answer("❌ ʀᴇsᴜʟᴛ ᴇxᴘɪʀᴇᴅ", show_alert=True)
                return

            result_info = merge_collections[result_key]
            send_as_file = data.startswith("merge_send_file_")

            await callback_query.edit_message_text(
                f"🚀 **ᴜᴘʟᴏᴀᴅɪɴɢ ᴍᴇʀɢᴇᴅ ᴠɪᴅᴇᴏ**\n\n"
                f"📤 sᴇɴᴅɪɴɢ ᴀs {'ꜰɪʟᴇ' if send_as_file else 'ᴠɪᴅᴇᴏ'}..."
            )

            try:
                caption = (f"✅ **ᴍᴇʀɢᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                          f"📹 **ᴠɪᴅᴇᴏs ᴍᴇʀɢᴇᴅ:** {result_info['video_count']}\n"
                          f"⏱️ **ᴅᴜʀᴀᴛɪᴏɴ:** {result_info['duration']}\n"
                          f"📦 **sɪᴢᴇ:** {result_info['size_mb']:.1f} ᴍʙ")

                if send_as_file:
                    await client.send_document(
                        result_info['user_id'],
                        result_info['output_path'],
                        caption=caption,
                        file_name=f"merged_video_{process_id}.mp4"
                    )
                else:
                    from plugins.thumbnail import get_user_thumbnail
                    thumbnail_path = get_user_thumbnail(result_info['user_id'])

                    await client.send_video(
                        result_info['user_id'],
                        result_info['output_path'],
                        caption=caption,
                        thumb=thumbnail_path
                    )

                await db.update_operation(result_info['operation_id'], {"status": "completed"})

                # Clean up
                try:
                    os.remove(result_info['output_path'])
                except:
                    pass

                del merge_collections[result_key]

            except Exception as e:
                logger.error(f"Failed to send merged video: {e}")
                await callback_query.edit_message_text("❌ **ᴜᴘʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ**\n\nᴄᴏᴜʟᴅɴ'ᴛ sᴇɴᴅ ᴍᴇʀɢᴇᴅ ᴠɪᴅᴇᴏ.")

        else:
            await callback_query.answer("❌ ᴜɴᴋɴᴏᴡɴ ᴍᴇʀɢᴇ ᴏᴘᴛɪᴏɴ", show_alert=True)

    except Exception as e:
        logger.error(f"Error in merge callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

# New processing functions for watermark and trim
async def start_watermark_processing(client: Client, reply_message: Message, video_message: Message, watermark_type: str, watermark_data: str):
    """Start watermark processing with specific type and data"""
    try:
        user_id = reply_message.from_user.id
        db = Database()
        await db.connect()
        
        # Check user privileges
        user = await db.get_user(user_id)
        if not await should_bypass_limits(user_id, db):
            if not user:
                await reply_message.reply_text("❌ User not found. Please use /start first.")
                return
                
            if user.get("credits", 0) < Config.PROCESS_COST:
                await reply_message.reply_text(
                    f"❌ **Insufficient Credits**\n\n"
                    f"You need {Config.PROCESS_COST} credits for this operation.\n"
                    f"Your balance: {user.get('credits', 0)} credits\n\n"
                    f"Use /referral to earn more credits or /premium to get unlimited access."
                )
                return
        
        # Create processing operation based on watermark type
        if watermark_type == "text":
            operation = f"watermark_text:{watermark_data}"
        elif watermark_type == "image":
            operation = f"watermark_image:{watermark_data}"
        else:
            operation = "watermark_default"
        
        # Create operation record
        operation_id = await db.add_operation(user_id, f"watermark_{watermark_type}")
        
        # Start processing using task manager
        task_manager = TaskManager()
        await task_manager.start_task(
            user_id=user_id,
            task_name=f"watermark_{watermark_type}",
            coroutine=process_video(client, reply_message, video_message, operation, operation_id),
            task_data={"operation": operation, "operation_id": str(operation_id)}
        )
        
    except Exception as e:
        logger.error(f"Error starting watermark processing: {e}")
        await reply_message.reply_text("❌ **Error starting watermark processing**")

async def start_trim_processing(client: Client, reply_message: Message, video_message: Message, duration: int):
    """Start trim processing with custom duration"""
    try:
        user_id = reply_message.from_user.id
        db = Database()
        await db.connect()
        
        # Check user privileges
        user = await db.get_user(user_id)
        if not await should_bypass_limits(user_id, db):
            if not user:
                await reply_message.reply_text("❌ User not found. Please use /start first.")
                return
                
            if user.get("credits", 0) < Config.PROCESS_COST:
                await reply_message.reply_text(
                    f"❌ **Insufficient Credits**\n\n"
                    f"You need {Config.PROCESS_COST} credits for this operation.\n"
                    f"Your balance: {user.get('credits', 0)} credits\n\n"
                    f"Use /referral to earn more credits or /premium to get unlimited access."
                )
                return
        
        # Create operation record
        operation_id = await db.add_operation(user_id, "trim_custom")
        
        # Start processing using task manager
        task_manager = TaskManager()
        await task_manager.start_task(
            user_id=user_id,
            task_name="trim_custom",
            coroutine=process_video(client, reply_message, video_message, f"trim_{duration}", operation_id),
            task_data={"operation": f"trim_{duration}", "operation_id": str(operation_id)}
        )
        
    except Exception as e:
        logger.error(f"Error starting trim processing: {e}")
        await reply_message.reply_text("❌ **Error starting trim processing**")