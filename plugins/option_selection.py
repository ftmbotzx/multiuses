import time
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

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

        # Import show option functions from their respective modules
        from plugins.option_menus import (
            show_trim_options, show_compress_options, show_rotate_options,
            show_merge_options, show_watermark_options, show_screenshot_options,
            show_resolution_options, show_extract_audio_options, 
            show_subtitles_options, show_replace_audio_options
        )
        
        # Import start_processing from processing module
        from plugins.video_processing import start_processing

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