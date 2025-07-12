from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

async def show_trim_options(client, callback_query: CallbackQuery, video_message: Message):
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

async def show_compress_options(client, callback_query: CallbackQuery, video_message: Message):
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

async def show_rotate_options(client, callback_query: CallbackQuery, video_message: Message):
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
    text += f"sᴇʟᴇᴄᴛ ʀᴏᴛᴀᴛɪᴏɴ ᴏʀ ꜰʟɪᴘ ᴏᴘᴛɪᴏɴ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_merge_options(client, callback_query: CallbackQuery, video_message: Message):
    """Show merge options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 sᴛᴀʀᴛ ᴄᴏʟʟᴇᴄᴛɪɴɢ", callback_data=f"merge_start_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"🔗 **ᴍᴇʀɢᴇ ᴠɪᴅᴇᴏs**\n\n"
    text += f"ɪ'ʟʟ ᴄᴏʟʟᴇᴄᴛ ᴍᴜʟᴛɪᴘʟᴇ ᴠɪᴅᴇᴏs ꜰʀᴏᴍ ʏᴏᴜ ᴀɴᴅ ᴍᴇʀɢᴇ ᴛʜᴇᴍ ɪɴᴛᴏ ᴀ sɪɴɢʟᴇ ᴠɪᴅᴇᴏ.\n\n"
    text += f"ᴄʟɪᴄᴋ 'sᴛᴀʀᴛ ᴄᴏʟʟᴇᴄᴛɪɴɢ' ᴀɴᴅ sᴇɴᴅ ᴍᴇ ᴍᴏʀᴇ ᴠɪᴅᴇᴏs."

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_watermark_options(client, callback_query: CallbackQuery, video_message: Message):
    """Show watermark options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💧 ᴛᴇxᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data=f"watermark_text_{video_message.id}"),
            InlineKeyboardButton("🖼️ ɪᴍᴀɢᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data=f"watermark_image_{video_message.id}")
        ],
        [
            InlineKeyboardButton("🏷️ ʟᴏɢᴏ ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data=f"process_watermark_logo_{video_message.id}"),
            InlineKeyboardButton("⏰ ᴛɪᴍᴇsᴛᴀᴍᴘ", callback_data=f"process_watermark_timestamp_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"💧 **ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"sᴇʟᴇᴄᴛ ᴛʏᴘᴇ ᴏꜰ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴏ ᴀᴅᴅ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_screenshot_options(client, callback_query: CallbackQuery, video_message: Message):
    """Show screenshot options"""
    duration = video_message.video.duration
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📸 1 sᴄʀᴇᴇɴsʜᴏᴛ", callback_data=f"process_screenshot_1_medium_{video_message.id}"),
            InlineKeyboardButton("📸 3 sᴄʀᴇᴇɴsʜᴏᴛs", callback_data=f"process_screenshot_3_medium_{video_message.id}")
        ],
        [
            InlineKeyboardButton("📸 5 sᴄʀᴇᴇɴsʜᴏᴛs", callback_data=f"process_screenshot_5_medium_{video_message.id}"),
            InlineKeyboardButton("📸 10 sᴄʀᴇᴇɴsʜᴏᴛs", callback_data=f"process_screenshot_10_medium_{video_message.id}")
        ],
        [
            InlineKeyboardButton("📸 ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇ", callback_data=f"screenshot_custom_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"📸 **sᴄʀᴇᴇɴsʜᴏᴛ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"**ᴠɪᴅᴇᴏ ᴅᴜʀᴀᴛɪᴏɴ:** {duration // 60}:{duration % 60:02d}\n\n"
    text += f"sᴇʟᴇᴄᴛ ʜᴏᴡ ᴍᴀɴʏ sᴄʀᴇᴇɴsʜᴏᴛs ᴛᴏ ᴛᴀᴋᴇ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_resolution_options(client, callback_query: CallbackQuery, video_message: Message):
    """Show resolution options"""
    current_width = video_message.video.width
    current_height = video_message.video.height
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📏 480ᴘ", callback_data=f"process_resolution_480p_{video_message.id}"),
            InlineKeyboardButton("📏 720ᴘ", callback_data=f"process_resolution_720p_{video_message.id}")
        ],
        [
            InlineKeyboardButton("📏 1080ᴘ", callback_data=f"process_resolution_1080p_{video_message.id}"),
            InlineKeyboardButton("📏 2160ᴘ (4ᴋ)", callback_data=f"process_resolution_2160p_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"📏 **ʀᴇsᴏʟᴜᴛɪᴏɴ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"**ᴄᴜʀʀᴇɴᴛ ʀᴇsᴏʟᴜᴛɪᴏɴ:** {current_width}x{current_height}\n\n"
    text += f"sᴇʟᴇᴄᴛ ɴᴇᴡ ʀᴇsᴏʟᴜᴛɪᴏɴ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_extract_audio_options(client, callback_query: CallbackQuery, video_message: Message):
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

async def show_subtitles_options(client, callback_query: CallbackQuery, video_message: Message):
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

    text = f"📝 **sᴜʙᴛɪᴛʟᴇ ᴏᴘᴛɪᴏɴs**\n\n"
    text += f"sᴇʟᴇᴄᴛ sᴜʙᴛɪᴛʟᴇ ᴛʏᴘᴇ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)

async def show_replace_audio_options(client, callback_query: CallbackQuery, video_message: Message):
    """Show replace audio options"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴜᴘʟᴏᴀᴅ ᴀᴜᴅɪᴏ", callback_data=f"replace_audio_custom_{video_message.id}")
        ],
        [
            InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data=f"back_to_options_{video_message.id}")
        ]
    ])

    text = f"🎵 **ʀᴇᴘʟᴀᴄᴇ ᴀᴜᴅɪᴏ**\n\n"
    text += f"ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ᴀᴜᴅɪᴏ ꜰɪʟᴇ:"

    await callback_query.edit_message_text(text, reply_markup=keyboard)