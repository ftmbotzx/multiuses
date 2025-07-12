from pyrogram.types import Message, CallbackQuery
from info import Config
import functools

def admin_only(func):
    """Decorator to restrict commands to admins only"""
    @functools.wraps(func)
    async def wrapper(client, message: Message):
        user_id = message.from_user.id
        if user_id not in Config.ADMINS:
            await message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return
        return await func(client, message)
    return wrapper

def admin_callback_only(func):
    """Decorator to restrict callback queries to admins only"""
    @functools.wraps(func)
    async def wrapper(client, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        if user_id not in Config.ADMINS:
            await callback_query.answer("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.", show_alert=True)
            return
        return await func(client, callback_query)
    return wrapper

def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return user_id in Config.ADMINS