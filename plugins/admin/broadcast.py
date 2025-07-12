from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging
import asyncio

logger = logging.getLogger(__name__)
db = Database()

def admin_only(func):
    """Decorator to restrict commands to admins only"""
    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id not in Config.ADMINS:
            await message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return
        return await func(client, message)
    return wrapper

@Client.on_message(filters.command("broadcast") & filters.private)
@admin_only
async def broadcast_command(client: Client, message: Message):
    """Handle /broadcast command"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ**\n\n"
                "**ᴜsᴀɢᴇ:** `/broadcast <message>`\n"
                "**ᴇxᴀᴍᴘʟᴇ:** `/broadcast Hello everyone!`"
            )
            return
        
        broadcast_message = message.text.split(None, 1)[1]
        
        # Get confirmation
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴄᴏɴꜰɪʀᴍ", callback_data=f"broadcast_confirm_{message.id}")],
            [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="broadcast_cancel")]
        ])
        
        await message.reply_text(
            f"📢 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏɴꜰɪʀᴍᴀᴛɪᴏɴ**\n\n"
            f"**ᴍᴇssᴀɢᴇ:**\n{broadcast_message}\n\n"
            f"ᴄᴏɴꜰɪʀᴍ ᴛᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs.",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in broadcast command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴍᴀɴᴅ.")

@Client.on_callback_query(filters.regex(r"^broadcast_confirm_(\d+)$"))
async def broadcast_confirm_callback(client: Client, callback_query: CallbackQuery):
    """Handle broadcast confirmation"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        
        message_id = int(callback_query.matches[0].group(1))
        
        # Get original message
        original_message = await client.get_messages(callback_query.message.chat.id, message_id)
        broadcast_message = original_message.text.split(None, 1)[1]
        
        # Start broadcast
        await callback_query.edit_message_text(
            "📢 **ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ**\n\n"
            "sᴇɴᴅɪɴɢ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs..."
        )
        
        # Get all users
        users = await db.users.find({}).to_list(None)
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await client.send_message(
                    user["user_id"],
                    f"📢 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ**\n\n{broadcast_message}"
                )
                sent_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {user['user_id']}: {e}")
        
        # Update status
        await callback_query.edit_message_text(
            f"📢 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
            f"**ᴛᴏᴛᴀʟ ᴜsᴇʀs:** {len(users)}\n"
            f"**sᴇɴᴛ:** {sent_count}\n"
            f"**ꜰᴀɪʟᴇᴅ:** {failed_count}"
        )
        
    except Exception as e:
        logger.error(f"Error in broadcast confirm: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ", show_alert=True)

@Client.on_callback_query(filters.regex("^broadcast_cancel$"))
async def broadcast_cancel_callback(client: Client, callback_query: CallbackQuery):
    """Handle broadcast cancellation"""
    if callback_query.from_user.id not in Config.ADMINS:
        await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
        return
    
    await callback_query.edit_message_text("❌ **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ**")