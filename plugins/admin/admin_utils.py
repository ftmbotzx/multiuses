from pyrogram.types import Message, CallbackQuery
from info import Config
import functools
import time

# Cache admin status to reduce VPS load
_admin_cache = {}
_cache_ttl = 300  # 5 minutes cache

def clear_admin_cache():
    """Clear the admin cache"""
    global _admin_cache
    _admin_cache = {}

def is_admin(user_id: int) -> bool:
    """Optimized admin check with caching to reduce VPS load"""
    current_time = time.time()
    
    # Check cache first
    if user_id in _admin_cache:
        cached_result, cached_time = _admin_cache[user_id]
        if current_time - cached_time < _cache_ttl:
            return cached_result
    
    # Check admin status and cache result
    result = user_id in Config.ADMINS
    _admin_cache[user_id] = (result, current_time)
    
    # Clean old cache entries
    if len(_admin_cache) > 100:  # Prevent memory bloat
        expired_keys = [k for k, (_, t) in _admin_cache.items() if current_time - t > _cache_ttl]
        for k in expired_keys:
            del _admin_cache[k]
    
    return result

def admin_only(func):
    """Optimized decorator to restrict commands to admins only"""
    @functools.wraps(func)
    async def wrapper(client, message: Message):
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
            return
        return await func(client, message)
    return wrapper

def admin_callback_only(func):
    """Optimized decorator to restrict callback queries to admins only"""
    @functools.wraps(func)
    async def wrapper(client, callback_query: CallbackQuery):
        if not is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", show_alert=True)
            return
        return await func(client, callback_query)
    return wrapper