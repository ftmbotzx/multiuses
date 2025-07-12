from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
db = Database()

# Missing callback handlers for admin logs panel

@Client.on_callback_query(filters.regex("^admin_full_logs$"))
@admin_callback_only
async def admin_full_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin full logs callback"""
    try:
        # Get more operations (last 50)
        recent_ops = await db.operations.find({}).sort("date", -1).limit(50).to_list(None)
        
        text = "📊 **ꜰᴜʟʟ ᴏᴘᴇʀᴀᴛɪᴏɴ ʟᴏɢs (ʟᴀsᴛ 50)**\n\n"
        
        if recent_ops:
            for i, op in enumerate(recent_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                status = op.get("status", "Unknown")
                date = op.get("date", datetime.now())
                
                status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                
                text += f"`{i:2d}.` {status_emoji} **{operation_type}** - ᴜsᴇʀ: `{user_id}`\n"
                text += f"      📅 {date.strftime('%d/%m %H:%M:%S')}\n"
                
                # Add some spacing every 10 entries for readability
                if i % 10 == 0:
                    text += "\n"
        else:
            text += "ɴᴏ ᴏᴘᴇʀᴀᴛɪᴏɴs ꜰᴏᴜɴᴅ."
        
        # Split message if too long (Telegram limit)
        if len(text) > 4000:
            text = text[:4000] + "\n\n... (ᴛʀᴜɴᴄᴀᴛᴇᴅ)"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_full_logs")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_logs")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin full logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_filter_logs$"))
@admin_callback_only
async def admin_filter_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin filter logs callback"""
    try:
        text = """
🔍 **ꜰɪʟᴛᴇʀ ʟᴏɢs**

sᴇʟᴇᴄᴛ ᴀ ꜰɪʟᴛᴇʀ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ:
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ sᴜᴄᴄᴇss", callback_data="admin_success_logs"),
                InlineKeyboardButton("❌ ꜰᴀɪʟᴇᴅ", callback_data="admin_error_logs")
            ],
            [
                InlineKeyboardButton("⏳ ᴘᴇɴᴅɪɴɢ", callback_data="admin_pending_logs"),
                InlineKeyboardButton("📅 ᴛᴏᴅᴀʏ", callback_data="admin_today_logs")
            ],
            [
                InlineKeyboardButton("🎬 ᴠɪᴅᴇᴏ ᴏᴘs", callback_data="admin_video_logs"),
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴏɴʟʏ", callback_data="admin_premium_logs")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_logs")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin filter logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_error_logs$"))
@admin_callback_only
async def admin_error_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin error logs callback"""
    try:
        # Get failed operations
        failed_ops = await db.operations.find({"status": "failed"}).sort("date", -1).limit(20).to_list(None)
        
        text = "❌ **ꜰᴀɪʟᴇᴅ ᴏᴘᴇʀᴀᴛɪᴏɴs**\n\n"
        
        if failed_ops:
            for i, op in enumerate(failed_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                date = op.get("date", datetime.now())
                error_message = op.get("error_message", "Unknown error")
                
                text += f"`{i}.` **{operation_type}** - ᴜsᴇʀ: `{user_id}`\n"
                text += f"   📅 {date.strftime('%d/%m %H:%M')}\n"
                text += f"   ❌ {error_message[:50]}{'...' if len(error_message) > 50 else ''}\n\n"
        else:
            text += "✅ ɴᴏ ꜰᴀɪʟᴇᴅ ᴏᴘᴇʀᴀᴛɪᴏɴs ꜰᴏᴜɴᴅ!"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_error_logs")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_filter_logs")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin error logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_success_logs$"))
@admin_callback_only
async def admin_success_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin success logs callback"""
    try:
        # Get successful operations
        success_ops = await db.operations.find({"status": "completed"}).sort("date", -1).limit(20).to_list(None)
        
        text = "✅ **sᴜᴄᴄᴇssꜰᴜʟ ᴏᴘᴇʀᴀᴛɪᴏɴs**\n\n"
        
        if success_ops:
            for i, op in enumerate(success_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                date = op.get("date", datetime.now())
                
                text += f"`{i}.` **{operation_type}** - ᴜsᴇʀ: `{user_id}`\n"
                text += f"   📅 {date.strftime('%d/%m %H:%M')}\n\n"
        else:
            text += "ɴᴏ sᴜᴄᴄᴇssꜰᴜʟ ᴏᴘᴇʀᴀᴛɪᴏɴs ꜰᴏᴜɴᴅ."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_success_logs")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_filter_logs")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin success logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_pending_logs$"))
@admin_callback_only
async def admin_pending_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin pending logs callback"""
    try:
        # Get pending operations
        pending_ops = await db.operations.find({"status": "pending"}).sort("date", -1).limit(20).to_list(None)
        
        text = "⏳ **ᴘᴇɴᴅɪɴɢ ᴏᴘᴇʀᴀᴛɪᴏɴs**\n\n"
        
        if pending_ops:
            for i, op in enumerate(pending_ops, 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                date = op.get("date", datetime.now())
                
                # Calculate time since started
                time_elapsed = datetime.now() - date
                minutes_elapsed = int(time_elapsed.total_seconds() / 60)
                
                text += f"`{i}.` **{operation_type}** - ᴜsᴇʀ: `{user_id}`\n"
                text += f"   📅 {date.strftime('%d/%m %H:%M')} ({minutes_elapsed}ᴍ ᴀɢᴏ)\n\n"
        else:
            text += "✅ ɴᴏ ᴘᴇɴᴅɪɴɢ ᴏᴘᴇʀᴀᴛɪᴏɴs!"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_pending_logs")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_filter_logs")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin pending logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_today_logs$"))
@admin_callback_only
async def admin_today_logs_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin today logs callback"""
    try:
        # Get today's operations
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_ops = await db.operations.find({"date": {"$gte": today}}).sort("date", -1).to_list(None)
        
        text = f"📅 **ᴛᴏᴅᴀʏ's ᴏᴘᴇʀᴀᴛɪᴏɴs ({len(today_ops)})**\n\n"
        
        if today_ops:
            # Show stats first
            completed = len([op for op in today_ops if op.get("status") == "completed"])
            failed = len([op for op in today_ops if op.get("status") == "failed"])
            pending = len([op for op in today_ops if op.get("status") == "pending"])
            
            text += f"**sᴛᴀᴛs:**\n"
            text += f"• ✅ ᴄᴏᴍᴘʟᴇᴛᴇᴅ: {completed}\n"
            text += f"• ❌ ꜰᴀɪʟᴇᴅ: {failed}\n"
            text += f"• ⏳ ᴘᴇɴᴅɪɴɢ: {pending}\n\n"
            
            text += "**ʀᴇᴄᴇɴᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs:**\n"
            for i, op in enumerate(today_ops[:15], 1):  # Show last 15
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                status = op.get("status", "Unknown")
                date = op.get("date", datetime.now())
                
                status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                
                text += f"`{i}.` {status_emoji} **{operation_type}** - `{user_id}` ({date.strftime('%H:%M')})\n"
        else:
            text += "ɴᴏ ᴏᴘᴇʀᴀᴛɪᴏɴs ᴛᴏᴅᴀʏ."
        
        # Split message if too long
        if len(text) > 4000:
            text = text[:4000] + "\n\n... (ᴛʀᴜɴᴄᴀᴛᴇᴅ)"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_today_logs")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_filter_logs")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin today logs callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)