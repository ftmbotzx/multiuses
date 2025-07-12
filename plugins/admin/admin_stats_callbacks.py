from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
db = Database()

# Missing callback handlers for admin statistics panel

@Client.on_callback_query(filters.regex("^admin_trends$"))
@admin_callback_only
async def admin_trends_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin trends callback"""
    try:
        # Get trends data for different time periods
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User trends
        users_today = await db.users.count_documents({"joined_date": {"$gte": today}})
        users_yesterday = await db.users.count_documents({
            "joined_date": {"$gte": yesterday, "$lt": today}
        })
        users_week = await db.users.count_documents({"joined_date": {"$gte": week_ago}})
        users_month = await db.users.count_documents({"joined_date": {"$gte": month_ago}})
        
        # Operation trends
        ops_today = await db.operations.count_documents({"date": {"$gte": today}})
        ops_yesterday = await db.operations.count_documents({
            "date": {"$gte": yesterday, "$lt": today}
        })
        ops_week = await db.operations.count_documents({"date": {"$gte": week_ago}})
        ops_month = await db.operations.count_documents({"date": {"$gte": month_ago}})
        
        text = f"""
📈 **ᴜsᴀɢᴇ ᴛʀᴇɴᴅs**

**ɴᴇᴡ ᴜsᴇʀs:**
• **ᴛᴏᴅᴀʏ:** {users_today}
• **ʏᴇsᴛᴇʀᴅᴀʏ:** {users_yesterday}
• **ᴛʜɪs ᴡᴇᴇᴋ:** {users_week}
• **ᴛʜɪs ᴍᴏɴᴛʜ:** {users_month}

**ᴏᴘᴇʀᴀᴛɪᴏɴs:**
• **ᴛᴏᴅᴀʏ:** {ops_today}
• **ʏᴇsᴛᴇʀᴅᴀʏ:** {ops_yesterday}
• **ᴛʜɪs ᴡᴇᴇᴋ:** {ops_week}
• **ᴛʜɪs ᴍᴏɴᴛʜ:** {ops_month}

**ɢʀᴏᴡᴛʜ:**
• **ᴅᴀɪʟʏ ᴜsᴇʀs:** {'+' if users_today > users_yesterday else '-'}{abs(users_today - users_yesterday)}
• **ᴅᴀɪʟʏ ᴏᴘs:** {'+' if ops_today > ops_yesterday else '-'}{abs(ops_today - ops_yesterday)}

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_trends")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_stats")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin trends callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_detailed_stats$"))
@admin_callback_only
async def admin_detailed_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin detailed stats callback"""
    try:
        # Get detailed statistics
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({
            "last_activity": {"$gte": datetime.now() - timedelta(days=7)}
        })
        premium_users = await db.users.count_documents({"premium_until": {"$gt": datetime.now()}})
        banned_users = await db.users.count_documents({"banned": True})
        
        # Operation stats by type
        operations_by_type = {}
        operation_types = ["trim", "compress", "watermark", "mute", "reverse", "extract_audio", "screenshot"]
        
        for op_type in operation_types:
            count = await db.operations.count_documents({"operation_type": op_type})
            operations_by_type[op_type] = count
        
        # Success/failure rates
        total_ops = await db.operations.count_documents({})
        successful_ops = await db.operations.count_documents({"status": "completed"})
        failed_ops = await db.operations.count_documents({"status": "failed"})
        
        success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
        
        text = f"""
🔍 **ᴅᴇᴛᴀɪʟᴇᴅ sᴛᴀᴛɪsᴛɪᴄs**

**ᴜsᴇʀ ʙʀᴇᴀᴋᴅᴏᴡɴ:**
• **ᴛᴏᴛᴀʟ:** {total_users}
• **ᴀᴄᴛɪᴠᴇ (7ᴅ):** {active_users} ({active_users/total_users*100:.1f}%)
• **ᴘʀᴇᴍɪᴜᴍ:** {premium_users} ({premium_users/total_users*100:.1f}%)
• **ʙᴀɴɴᴇᴅ:** {banned_users} ({banned_users/total_users*100:.1f}%)

**ᴏᴘᴇʀᴀᴛɪᴏɴ ʙʀᴇᴀᴋᴅᴏᴡɴ:**
• **ᴛʀɪᴍ:** {operations_by_type.get('trim', 0)}
• **ᴄᴏᴍᴘʀᴇss:** {operations_by_type.get('compress', 0)}
• **ᴡᴀᴛᴇʀᴍᴀʀᴋ:** {operations_by_type.get('watermark', 0)}
• **ᴍᴜᴛᴇ:** {operations_by_type.get('mute', 0)}
• **ʀᴇᴠᴇʀsᴇ:** {operations_by_type.get('reverse', 0)}
• **ᴇxᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ:** {operations_by_type.get('extract_audio', 0)}
• **sᴄʀᴇᴇɴsʜᴏᴛ:** {operations_by_type.get('screenshot', 0)}

**ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ:**
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {total_ops}
• **sᴜᴄᴄᴇssꜰᴜʟ:** {successful_ops}
• **ꜰᴀɪʟᴇᴅ:** {failed_ops}
• **sᴜᴄᴄᴇss ʀᴀᴛᴇ:** {success_rate:.1f}%

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_detailed_stats")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_stats")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin detailed stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_operation_stats$"))
@admin_callback_only
async def admin_operation_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin operation stats callback"""
    try:
        # Get operation statistics
        total_operations = await db.operations.count_documents({})
        today_operations = await db.operations.count_documents({
            "date": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        # Status breakdown
        completed_ops = await db.operations.count_documents({"status": "completed"})
        failed_ops = await db.operations.count_documents({"status": "failed"})
        pending_ops = await db.operations.count_documents({"status": "pending"})
        
        # Recent operations
        recent_ops = await db.operations.find({}).sort("date", -1).limit(10).to_list(None)
        
        text = f"""
⚡ **ᴏᴘᴇʀᴀᴛɪᴏɴ sᴛᴀᴛɪsᴛɪᴄs**

**ᴏᴠᴇʀᴀʟʟ:**
• **ᴛᴏᴛᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴs:** {total_operations}
• **ᴛᴏᴅᴀʏ:** {today_operations}

**sᴛᴀᴛᴜs ʙʀᴇᴀᴋᴅᴏᴡɴ:**
• **ᴄᴏᴍᴘʟᴇᴛᴇᴅ:** {completed_ops} ({completed_ops/total_operations*100:.1f}%)
• **ꜰᴀɪʟᴇᴅ:** {failed_ops} ({failed_ops/total_operations*100:.1f}%)
• **ᴘᴇɴᴅɪɴɢ:** {pending_ops} ({pending_ops/total_operations*100:.1f}%)

**ʀᴇᴄᴇɴᴛ ᴀᴄᴛɪᴠɪᴛʏ:**
"""
        
        if recent_ops:
            for i, op in enumerate(recent_ops[:5], 1):
                user_id = op.get("user_id", "Unknown")
                operation_type = op.get("operation_type", "Unknown")
                status = op.get("status", "Unknown")
                date = op.get("date", datetime.now())
                
                status_emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                
                text += f"`{i}.` {status_emoji} **{operation_type}** - `{user_id}` ({date.strftime('%H:%M')})\n"
        else:
            text += "ɴᴏ ʀᴇᴄᴇɴᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs."
        
        text += f"\n⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_operation_stats")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_stats")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin operation stats callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)