from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

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

        # Get user for credit display
        user_id = callback_query.from_user.id
        user = await db.get_user(user_id)
        
        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS

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
            ],
            [
                InlineKeyboardButton("🎬 ɢᴇɴᴇʀᴀᴛᴇ sᴀᴍᴘʟᴇ", callback_data=f"option_generate_{message_id}")
            ]
        ])

        # Build video info text
        video_info = f"📹 **ᴠɪᴅᴇᴏ ʀᴇᴄᴇɪᴠᴇᴅ**\n\n"
        video_info += f"**ꜰɪʟᴇ ɴᴀᴍᴇ:** {video_message.video.file_name or 'Unknown'}\n"
        video_info += f"**sɪᴢᴇ:** {video_message.video.file_size / (1024*1024):.2f} ᴍʙ\n"
        video_info += f"**ᴅᴜʀᴀᴛɪᴏɴ:** {video_message.video.duration // 60}:{video_message.video.duration % 60:02d}\n"
        video_info += f"**ʀᴇsᴏʟᴜᴛɪᴏɴ:** {video_message.video.width}x{video_message.video.height}\n\n"
        
        if is_premium:
            video_info += f"**ᴄᴏsᴛ:** 💎 ꜰʀᴇᴇ (ᴘʀᴇᴍɪᴜᴍ)\n"
        elif is_admin:
            video_info += f"**ᴄᴏsᴛ:** 🔧 ꜰʀᴇᴇ (ᴀᴅᴍɪɴ)\n"
        else:
            video_info += f"**ᴄᴏsᴛ:** {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ᴘᴇʀ ᴏᴘᴇʀᴀᴛɪᴏɴ\n"
            video_info += f"**ʏᴏᴜʀ ᴄʀᴇᴅɪᴛs:** {user.get('credits', 0) if user else 0}\n\n"
        
        video_info += "ᴄʜᴏᴏsᴇ ᴀ ᴘʀᴏᴄᴇssɪɴɢ ᴏᴘᴛɪᴏɴ:"

        await callback_query.edit_message_text(video_info, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error in back to options: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)