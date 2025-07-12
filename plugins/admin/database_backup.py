from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging
import json
from datetime import datetime

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

@Client.on_message(filters.command("dbbackup") & filters.private)
@admin_only
async def database_backup_command(client: Client, message: Message):
    """Handle /dbbackup command"""
    try:
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
            "backup_date": datetime.now().isoformat()
        }
        
        # Convert to JSON
        backup_json = json.dumps(backup_data, default=str, indent=2)
        
        # Save to file
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = f"{Config.TEMP_DIR}/{backup_filename}"
        
        with open(backup_path, 'w') as f:
            f.write(backup_json)
        
        # Send file
        await client.send_document(
            message.chat.id,
            backup_path,
            caption=f"📦 **ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ**\n\n"
                   f"**ᴅᴀᴛᴇ:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                   f"**ᴜsᴇʀs:** {len(users)}\n"
                   f"**ᴏᴘᴇʀᴀᴛɪᴏɴs:** {len(operations)}\n"
                   f"**ᴄᴏᴅᴇs:** {len(premium_codes)}\n"
                   f"**ʀᴇꜰᴇʀʀᴀʟs:** {len(referrals)}"
        )
        
        # Clean up
        import os
        try:
            os.remove(backup_path)
        except:
            pass
        
    except Exception as e:
        logger.error(f"Error in dbbackup command: {e}")
        await message.reply_text("❌ ᴇʀʀᴏʀ ᴄʀᴇᴀᴛɪɴɢ ʙᴀᴄᴋᴜᴘ.")