from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import Database
from info import Config
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^admin_backup$"))
async def admin_backup_panel(client: Client, callback_query: CallbackQuery):
    """Backup panel"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        text = f"""
💾 **ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ**

ᴄʀᴇᴀᴛᴇ ᴀɴᴅ ᴍᴀɴᴀɢᴇ ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘs.

**ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:**
• ʙᴀᴄᴋᴜᴘs ɪɴᴄʟᴜᴅᴇ ᴀʟʟ ᴜsᴇʀ ᴅᴀᴛᴀ
• ᴏᴘᴇʀᴀᴛɪᴏɴ ʜɪsᴛᴏʀʏ ɪs ɪɴᴄʟᴜᴅᴇᴅ
• ꜰɪʟᴇs ᴀʀᴇ ɴᴏᴛ ʙᴀᴄᴋᴇᴅ ᴜᴘ
• ʙᴀᴄᴋᴜᴘs ᴀʀᴇ ɪɴ ᴊsᴏɴ ꜰᴏʀᴍᴀᴛ

⏰ **ʟᴀsᴛ ᴜᴘᴅᴀᴛᴇ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📥 ᴄʀᴇᴀᴛᴇ ʙᴀᴄᴋᴜᴘ", callback_data="admin_create_backup"),
                InlineKeyboardButton("📊 ʙᴀᴄᴋᴜᴘ ɪɴꜰᴏ", callback_data="admin_backup_info")
            ],
            [
                InlineKeyboardButton("🔄 ᴀᴜᴛᴏ ʙᴀᴄᴋᴜᴘ", callback_data="admin_auto_backup"),
                InlineKeyboardButton("📋 ᴇxᴘᴏʀᴛ ᴜsᴇʀs", callback_data="admin_export_users")
            ],
            [
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_main")
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin backup panel: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_create_backup$"))
async def admin_create_backup_callback(client: Client, callback_query: CallbackQuery):
    """Create database backup"""
    try:
        if callback_query.from_user.id not in Config.ADMINS:
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
            
        await callback_query.answer("🔄 ᴄʀᴇᴀᴛɪɴɢ ʙᴀᴄᴋᴜᴘ...")
        
        # Create backup
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "users": [],
            "operations": [],
            "premium_codes": []
        }
        
        # Export users
        users = await db.users.find({}).to_list(None) if db.users is not None else []
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            backup_data["users"].append(user)
        
        # Export operations (last 1000)
        operations = await db.operations.find({}).sort("date", -1).limit(1000).to_list(None) if db.operations is not None else []
        for op in operations:
            op['_id'] = str(op['_id'])
            backup_data["operations"].append(op)
        
        # Export premium codes
        codes = await db.premium_codes.find({}).to_list(None) if db.premium_codes is not None else []
        for code in codes:
            code['_id'] = str(code['_id'])
            backup_data["premium_codes"].append(code)
        
        # Save backup file
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(Config.TEMP_DIR, backup_filename)
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        # Send backup file
        await client.send_document(
            callback_query.from_user.id,
            backup_path,
            caption=f"💾 **ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ**\n\n"
                   f"**ᴜsᴇʀs:** {len(backup_data['users'])}\n"
                   f"**ᴏᴘᴇʀᴀᴛɪᴏɴs:** {len(backup_data['operations'])}\n"
                   f"**ᴄᴏᴅᴇs:** {len(backup_data['premium_codes'])}\n"
                   f"**ᴄʀᴇᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        # Clean up
        os.remove(backup_path)
        
        await callback_query.answer("✅ ʙᴀᴄᴋᴜᴘ ᴄʀᴇᴀᴛᴇᴅ!")
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        await callback_query.answer("❌ ʙᴀᴄᴋᴜᴘ ꜰᴀɪʟᴇᴅ", show_alert=True)