import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import Database
from config import Config
from helpers.utils import FileUtils

logger = logging.getLogger(__name__)
db = Database()

# Store user thumbnails
user_thumbnails = {}

@Client.on_message(filters.command("setthumbnail") & filters.private)
async def set_thumbnail_command(client: Client, message: Message):
    """Handle /setthumbnail command"""
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
        
        await message.reply_text(
            "🖼️ **sᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ**\n\n"
            "📤 sᴇɴᴅ ᴀɴ ɪᴍᴀɢᴇ (ᴊᴘɢ/ᴘɴɢ) ᴛᴏ sᴇᴛ ᴀs ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ.\n\n"
            "ᴛʜɪs ᴛʜᴜᴍʙɴᴀɪʟ ᴡɪʟʟ ʙᴇ ᴜsᴇᴅ ꜰᴏʀ ᴀʟʟ ʏᴏᴜʀ ᴘʀᴏᴄᴇssᴇᴅ ᴠɪᴅᴇᴏs."
        )
        
        # Set user in waiting state
        user_thumbnails[user_id] = {"waiting": True}
        
    except Exception as e:
        logger.error(f"Error in set thumbnail command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ sᴇᴛᴛɪɴɢ ᴜᴘ ᴛʜᴜᴍʙɴᴀɪʟ.")

@Client.on_message(filters.command("deletethumbnail") & filters.private)
async def delete_thumbnail_command(client: Client, message: Message):
    """Handle /deletethumbnail command"""
    try:
        user_id = message.from_user.id
        
        if user_id in user_thumbnails and "path" in user_thumbnails[user_id]:
            # Delete thumbnail file
            try:
                os.remove(user_thumbnails[user_id]["path"])
            except:
                pass
            
            # Remove from memory
            del user_thumbnails[user_id]
            
            await message.reply_text(
                "🗑️ **ᴛʜᴜᴍʙɴᴀɪʟ ᴅᴇʟᴇᴛᴇᴅ**\n\n"
                "✅ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ."
            )
        else:
            await message.reply_text(
                "ℹ️ **ɴᴏ ᴛʜᴜᴍʙɴᴀɪʟ sᴇᴛ**\n\n"
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ sᴇᴛ."
            )
            
    except Exception as e:
        logger.error(f"Error in delete thumbnail command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴅᴇʟᴇᴛɪɴɢ ᴛʜᴜᴍʙɴᴀɪʟ.")

@Client.on_message(filters.command("showthumbnail") & filters.private)
async def show_thumbnail_command(client: Client, message: Message):
    """Handle /showthumbnail command"""
    try:
        user_id = message.from_user.id
        
        if user_id in user_thumbnails and "path" in user_thumbnails[user_id]:
            thumbnail_path = user_thumbnails[user_id]["path"]
            
            if os.path.exists(thumbnail_path):
                await client.send_photo(
                    user_id,
                    thumbnail_path,
                    caption="🖼️ **ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ**"
                )
            else:
                # Thumbnail file missing, remove from memory
                del user_thumbnails[user_id]
                await message.reply_text("❌ ᴛʜᴜᴍʙɴᴀɪʟ ꜰɪʟᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        else:
            await message.reply_text(
                "ℹ️ **ɴᴏ ᴛʜᴜᴍʙɴᴀɪʟ sᴇᴛ**\n\n"
                "ᴜsᴇ /setthumbnail ᴛᴏ sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ."
            )
            
    except Exception as e:
        logger.error(f"Error in show thumbnail command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ sʜᴏᴡɪɴɢ ᴛʜᴜᴍʙɴᴀɪʟ.")

@Client.on_message(filters.photo & filters.private)
async def handle_thumbnail_photo(client: Client, message: Message):
    """Handle photo uploads for thumbnail setting"""
    try:
        user_id = message.from_user.id
        
        # Check if user is waiting to set thumbnail
        if user_id in user_thumbnails and user_thumbnails[user_id].get("waiting", False):
            
            # Download the photo
            thumbnail_path = f"{Config.UPLOADS_DIR}/thumbnail_{user_id}.jpg"
            await client.download_media(message.photo, file_name=thumbnail_path)
            
            # Save thumbnail info
            user_thumbnails[user_id] = {
                "path": thumbnail_path,
                "waiting": False
            }
            
            await message.reply_text(
                "✅ **ᴛʜᴜᴍʙɴᴀɪʟ sᴇᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ**\n\n"
                "🖼️ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ ʜᴀs ʙᴇᴇɴ sᴀᴠᴇᴅ.\n"
                "ɪᴛ ᴡɪʟʟ ʙᴇ ᴜsᴇᴅ ꜰᴏʀ ᴀʟʟ ʏᴏᴜʀ ꜰᴜᴛᴜʀᴇ ᴘʀᴏᴄᴇssᴇᴅ ᴠɪᴅᴇᴏs.\n\n"
                "ᴜsᴇ /showthumbnail ᴛᴏ ᴠɪᴇᴡ ᴏʀ /deletethumbnail ᴛᴏ ʀᴇᴍᴏᴠᴇ."
            )
            
    except Exception as e:
        logger.error(f"Error handling thumbnail photo: {e}")
        if user_id in user_thumbnails and user_thumbnails[user_id].get("waiting", False):
            await message.reply_text("❌ ᴇʀʀᴏʀ sᴀᴠɪɴɢ ᴛʜᴜᴍʙɴᴀɪʟ.")

def get_user_thumbnail(user_id: int) -> str:
    """Get user's custom thumbnail path"""
    if user_id in user_thumbnails and "path" in user_thumbnails[user_id]:
        thumbnail_path = user_thumbnails[user_id]["path"]
        if os.path.exists(thumbnail_path):
            return thumbnail_path
    return None