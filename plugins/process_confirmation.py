from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex(r"^process_"))
async def handle_process_callback(client: Client, callback_query: CallbackQuery):
    """Handle video processing callbacks"""
    try:
        # Ensure database is connected
        if not db._connected:
            await db.connect()

        user_id = callback_query.from_user.id
        data = callback_query.data

        # Parse callback data
        parts = data.split("_")
        if len(parts) < 3:
            await callback_query.answer("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ", show_alert=True)
            return

        operation = "_".join(parts[1:-1])
        message_id = int(parts[-1])

        # Get user
        user = await db.get_user(user_id)
        if not user:
            await callback_query.answer("❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Check if user is banned
        if await db.is_user_banned(user_id):
            await callback_query.answer("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ", show_alert=True)
            return

        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin

        # Check credits only for non-privileged users
        if not bypass_limits and user.get("credits", 0) < Config.PROCESS_COST:
            await callback_query.answer(
                f"❌ ɪɴsᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛs!\nʏᴏᴜ ɴᴇᴇᴅ {Config.PROCESS_COST} ᴄʀᴇᴅɪᴛs ʙᴜᴛ ʜᴀᴠᴇ {user.get('credits', 0)}",
                show_alert=True
            )
            return

        # Check daily limit only for non-privileged users
        if not bypass_limits and not await db.check_daily_limit(user_id):
            await callback_query.answer("⏰ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ", show_alert=True)
            return

        # Get original video message
        try:
            video_message = await client.get_messages(callback_query.message.chat.id, message_id)
            if not video_message.video:
                await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
                return
        except Exception as e:
            await callback_query.answer("❌ ᴠɪᴅᴇᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
            return

        # Import start_processing function
        from plugins.video_processing import start_processing
        
        # Start processing
        await start_processing(client, callback_query, video_message, operation)

    except Exception as e:
        logger.error(f"Error in process callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ᴘʀᴏᴄᴇss", show_alert=True)