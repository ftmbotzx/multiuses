"""
Simple web server for bot health checks and monitoring
"""
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "Telegram Video Bot",
        "message": "Bot is running successfully!"
    })

async def web_server():
    """Create and configure the web server"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', health_check)
    
    logger.info("Web server configured with health check endpoints")
    return app