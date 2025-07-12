from pyrogram import Client
from pyrogram.types import Message
from database.db import Database
from info import Config
import logging

logger = logging.getLogger(__name__)
db = Database()

async def start_watermark_processing(client: Client, reply_message: Message, video_message: Message, watermark_type: str, watermark_data: str):
    """Start watermark processing with specific type and data"""
    try:
        user_id = reply_message.from_user.id
        
        # Check user privileges
        user = await db.get_user(user_id)
        # Check if user is premium or admin
        is_premium = await db.is_user_premium(user_id)
        is_admin = user_id in Config.ADMINS
        bypass_limits = is_premium or is_admin
        
        if not bypass_limits:
            if not user:
                await reply_message.reply_text("❌ User not found. Please use /start first.")
                return
                
            if user.get("credits", 0) < Config.PROCESS_COST:
                await reply_message.reply_text(
                    f"❌ **Insufficient Credits**\n\n"
                    f"You need {Config.PROCESS_COST} credits for this operation.\n"
                    f"Your balance: {user.get('credits', 0)} credits\n\n"
                    f"Use /referral to earn more credits or /premium to get unlimited access."
                )
                return
        
        # Create processing operation based on watermark type
        if watermark_type == "text":
            operation = f"watermark_text:{watermark_data}"
        elif watermark_type == "image":
            operation = f"watermark_image:{watermark_data}"
        else:
            operation = "watermark_default"
        
        # Create operation record
        operation_id = await db.add_operation(user_id, f"watermark_{watermark_type}")
        
        # Start processing using start_processing_with_params
        from plugins.video_processing import start_processing_with_params
        await start_processing_with_params(
            client, 
            reply_message, 
            video_message, 
            operation, 
            {}
        )
        
    except Exception as e:
        logger.error(f"Error starting watermark processing: {e}")
        await reply_message.reply_text("❌ **Error starting watermark processing**")