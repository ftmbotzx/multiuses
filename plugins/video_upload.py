from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

# Store merge video collections - shared with other modules
merge_collections = {}

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
            from plugins.merge_handler import handle_merge_collection
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