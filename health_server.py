#!/usr/bin/env python3
"""
Simple health check server
"""
import http.server
import socketserver
import json
import os
from threading import Thread

PORT = int(os.getenv("PORT", 8080))

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/health', '/status']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "Telegram Video Bot",
                "message": "Bot is running successfully!",
                "port": PORT
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

def start_health_server():
    """Start a simple health check server"""
    try:
        with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
            print(f"Health server running on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start health server: {e}")

if __name__ == "__main__":
    start_health_server()