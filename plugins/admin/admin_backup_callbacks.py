from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from info import Config
from .admin_utils import admin_callback_only
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)
db = Database()

# Missing callback handlers for admin backup panel

@Client.on_callback_query(filters.regex("^admin_create_backup$"))
@admin_callback_only
async def admin_create_backup_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin create backup callback"""
    try:
        await callback_query.answer("🔄 ᴄʀᴇᴀᴛɪɴɢ ʙᴀᴄᴋᴜᴘ...", show_alert=True)
        
        # Get all collections data
        users = await db.users.find({}).to_list(None)
        operations = await db.operations.find({}).to_list(None)
        premium_codes = await db.premium_codes.find({}).to_list(None)
        referrals = await db.referrals.find({}).to_list(None)
        
        backup_data = {
            "users": users,
            "operations": operations,
            "premium_codes": premium_codes,
            "referrals": referrals,
            "backup_date": datetime.now().isoformat(),
            "bot_version": "v2.0",
            "total_records": len(users) + len(operations) + len(premium_codes) + len(referrals)
        }
        
        # Convert to JSON
        backup_json = json.dumps(backup_data, default=str, indent=2)
        
        # Save to file
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(Config.TEMP_DIR, backup_filename)
        
        # Ensure temp directory exists
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_json)
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        file_size_mb = file_size / (1024 * 1024)
        
        text = f"""
📥 **ʙᴀᴄᴋᴜᴘ ᴄʀᴇᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ**

**ꜰɪʟᴇ ɪɴꜰᴏ:**
• **ɴᴀᴍᴇ:** {backup_filename}
• **sɪᴢᴇ:** {file_size_mb:.2f} MB
• **ʀᴇᴄᴏʀᴅs:** {backup_data['total_records']}

**ɪɴᴄʟᴜᴅᴇᴅ ᴅᴀᴛᴀ:**
• **ᴜsᴇʀs:** {len(users)}
• **ᴏᴘᴇʀᴀᴛɪᴏɴs:** {len(operations)}
• **ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs:** {len(premium_codes)}
• **ʀᴇꜰᴇʀʀᴀʟs:** {len(referrals)}

⏰ **ᴄʀᴇᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

**ɴᴏᴛᴇ:** ʙᴀᴄᴋᴜᴘ ꜰɪʟᴇ ɪs sᴀᴠᴇᴅ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ.
ᴅᴏᴡɴʟᴏᴀᴅ ɪᴛ sᴏᴏɴ ᴀs ɪᴛ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", callback_data=f"download_backup_{backup_filename}")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_backup")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        # Send backup file
        try:
            await client.send_document(
                chat_id=callback_query.from_user.id,
                document=backup_path,
                caption=f"💾 **ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ**\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n📊 {backup_data['total_records']} ʀᴇᴄᴏʀᴅs"
            )
            
            # Clean up the backup file after sending
            os.remove(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to send backup file: {e}")
            await callback_query.answer("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʙᴀᴄᴋᴜᴘ ꜰɪʟᴇ", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in admin create backup callback: {e}")
        await callback_query.answer("❌ ʙᴀᴄᴋᴜᴘ ꜰᴀɪʟᴇᴅ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_backup_info$"))
@admin_callback_only
async def admin_backup_info_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin backup info callback"""
    try:
        # Get database size info
        users_count = await db.users.count_documents({})
        operations_count = await db.operations.count_documents({})
        premium_codes_count = await db.premium_codes.count_documents({})
        referrals_count = await db.referrals.count_documents({})
        
        total_records = users_count + operations_count + premium_codes_count + referrals_count
        
        # Estimate backup size (rough calculation)
        estimated_size_mb = total_records * 0.001  # Rough estimate
        
        text = f"""
📊 **ʙᴀᴄᴋᴜᴘ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**

**ᴄᴜʀʀᴇɴᴛ ᴅᴀᴛᴀʙᴀsᴇ sɪᴢᴇ:**
• **ᴜsᴇʀs:** {users_count:,} ʀᴇᴄᴏʀᴅs
• **ᴏᴘᴇʀᴀᴛɪᴏɴs:** {operations_count:,} ʀᴇᴄᴏʀᴅs
• **ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs:** {premium_codes_count:,} ʀᴇᴄᴏʀᴅs
• **ʀᴇꜰᴇʀʀᴀʟs:** {referrals_count:,} ʀᴇᴄᴏʀᴅs

**ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅs:** {total_records:,}
**ᴇsᴛɪᴍᴀᴛᴇᴅ ʙᴀᴄᴋᴜᴘ sɪᴢᴇ:** ~{estimated_size_mb:.1f} MB

**ᴡʜᴀᴛ's ɪɴᴄʟᴜᴅᴇᴅ:**
• ᴀʟʟ ᴜsᴇʀ ᴀᴄᴄᴏᴜɴᴛs ᴀɴᴅ sᴇᴛᴛɪɴɢs
• ᴄᴏᴍᴘʟᴇᴛᴇ ᴏᴘᴇʀᴀᴛɪᴏɴ ʜɪsᴛᴏʀʏ
• ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇs ᴀɴᴅ ᴛʜᴇɪʀ sᴛᴀᴛᴜs
• ʀᴇꜰᴇʀʀᴀʟ ʀᴇʟᴀᴛɪᴏɴsʜɪᴘs

**ɴᴏᴛ ɪɴᴄʟᴜᴅᴇᴅ:**
• ᴀᴄᴛᴜᴀʟ ᴍᴇᴅɪᴀ ꜰɪʟᴇs
• ᴛᴇᴍᴘᴏʀᴀʀʏ ꜰɪʟᴇs
• sᴇssɪᴏɴ ᴅᴀᴛᴀ

⏰ **ᴜᴘᴅᴀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 ᴄʀᴇᴀᴛᴇ ʙᴀᴄᴋᴜᴘ", callback_data="admin_create_backup")],
            [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data="admin_backup_info")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_backup")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin backup info callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_auto_backup$"))
@admin_callback_only
async def admin_auto_backup_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin auto backup callback"""
    try:
        text = """
🔄 **ᴀᴜᴛᴏᴍᴀᴛɪᴄ ʙᴀᴄᴋᴜᴘ**

**ꜰᴇᴀᴛᴜʀᴇ ɴᴏᴛ ʏᴇᴛ ɪᴍᴘʟᴇᴍᴇɴᴛᴇᴅ**

ᴀᴜᴛᴏᴍᴀᴛɪᴄ ʙᴀᴄᴋᴜᴘs ᴡᴏᴜʟᴅ ɪɴᴄʟᴜᴅᴇ:
• sᴄʜᴇᴅᴜʟᴇᴅ ᴅᴀɪʟʏ/ᴡᴇᴇᴋʟʏ ʙᴀᴄᴋᴜᴘs
• ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴄʟᴏᴜᴅ sᴛᴏʀᴀɢᴇ ᴜᴘʟᴏᴀᴅ
• ʙᴀᴄᴋᴜᴘ ʀᴇᴛᴇɴᴛɪᴏɴ ᴘᴏʟɪᴄɪᴇs
• ɪɴᴄʀᴇᴍᴇɴᴛᴀʟ ʙᴀᴄᴋᴜᴘs

ꜰᴏʀ ɴᴏᴡ, ᴜsᴇ ᴍᴀɴᴜᴀʟ ʙᴀᴄᴋᴜᴘs.
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 ᴍᴀɴᴜᴀʟ ʙᴀᴄᴋᴜᴘ", callback_data="admin_create_backup")],
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_backup")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in admin auto backup callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)

@Client.on_callback_query(filters.regex("^admin_export_users$"))
@admin_callback_only
async def admin_export_users_callback(client: Client, callback_query: CallbackQuery):
    """Handle admin export users callback"""
    try:
        await callback_query.answer("📊 ᴇxᴘᴏʀᴛɪɴɢ ᴜsᴇʀ ᴅᴀᴛᴀ...", show_alert=True)
        
        # Get user data
        users = await db.users.find({}).to_list(None)
        
        # Create simplified user export
        user_export = []
        for user in users:
            user_export.append({
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "credits": user.get("credits", 0),
                "premium_until": user.get("premium_until"),
                "banned": user.get("banned", False),
                "joined_date": user.get("joined_date"),
                "total_operations": user.get("total_operations", 0),
                "referred_by": user.get("referred_by")
            })
        
        export_data = {
            "export_type": "users_only",
            "export_date": datetime.now().isoformat(),
            "total_users": len(user_export),
            "users": user_export
        }
        
        # Convert to JSON
        export_json = json.dumps(export_data, default=str, indent=2)
        
        # Save to file
        export_filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_path = os.path.join(Config.TEMP_DIR, export_filename)
        
        # Ensure temp directory exists
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(export_json)
        
        # Get file size
        file_size = os.path.getsize(export_path)
        file_size_mb = file_size / (1024 * 1024)
        
        text = f"""
📋 **ᴜsᴇʀ ᴅᴀᴛᴀ ᴇxᴘᴏʀᴛᴇᴅ**

**ᴇxᴘᴏʀᴛ ɪɴꜰᴏ:**
• **ꜰɪʟᴇ:** {export_filename}
• **sɪᴢᴇ:** {file_size_mb:.2f} MB
• **ᴜsᴇʀs:** {len(user_export)}

**ɪɴᴄʟᴜᴅᴇᴅ ꜰɪᴇʟᴅs:**
• ᴜsᴇʀ ɪᴅ ᴀɴᴅ ʙᴀsɪᴄ ɪɴꜰᴏ
• ᴄʀᴇᴅɪᴛs ᴀɴᴅ ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs
• ᴊᴏɪɴ ᴅᴀᴛᴇ ᴀɴᴅ ᴀᴄᴛɪᴠɪᴛʏ
• ʀᴇꜰᴇʀʀᴀʟ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ

⏰ **ᴇxᴘᴏʀᴛᴇᴅ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data="admin_backup")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        # Send export file
        try:
            await client.send_document(
                chat_id=callback_query.from_user.id,
                document=export_path,
                caption=f"📋 **ᴜsᴇʀ ᴅᴀᴛᴀ ᴇxᴘᴏʀᴛ**\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n👥 {len(user_export)} ᴜsᴇʀs"
            )
            
            # Clean up the export file after sending
            os.remove(export_path)
            
        except Exception as e:
            logger.error(f"Failed to send export file: {e}")
            await callback_query.answer("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴇxᴘᴏʀᴛ ꜰɪʟᴇ", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in admin export users callback: {e}")
        await callback_query.answer("❌ ᴇxᴘᴏʀᴛ ꜰᴀɪʟᴇᴅ", show_alert=True)