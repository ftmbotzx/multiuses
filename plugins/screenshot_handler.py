from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import logging

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^screenshot_"))
async def handle_screenshot_callback(client: Client, callback_query: CallbackQuery):
    """Handle screenshot option callbacks"""
    try:
        data = callback_query.data
        
        # Handle screenshot quality/count selection
        if data.startswith("screenshot_qty_") or data.startswith("screenshot_quality_"):
            # These are handled by the process_confirmation module
            # Convert to process_ format for compatibility
            new_data = data.replace("screenshot_", "process_screenshot_")
            callback_query.data = new_data
            
            # Import and call process handler
            from plugins.process_confirmation import handle_process_callback
            await handle_process_callback(client, callback_query)
        
    except Exception as e:
        logger.error(f"Error in screenshot callback: {e}")
        await callback_query.answer("❌ ᴇʀʀᴏʀ", show_alert=True)