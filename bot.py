#!/usr/bin/env python3
import sys
import asyncio
import warnings
import threading

print(f"🐍 Python Version: {sys.version}")

# ==================== PYTHON 3.14 FIX ====================
# This MUST be before ANY pyrogram import
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Create event loop BEFORE pyrogram loads
try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Patch asyncio.get_event_loop globally
_original = asyncio.get_event_loop

def _patched():
    try:
        lo = _original()
        if lo.is_closed():
            raise RuntimeError()
        return lo
    except RuntimeError:
        lo = asyncio.new_event_loop()
        asyncio.set_event_loop(lo)
        return lo

asyncio.get_event_loop = _patched

# Also patch the events module directly
try:
    import asyncio.events
    asyncio.events._get_event_loop = _patched
    
    # Patch BaseDefaultEventLoopPolicy
    _orig_policy_get = asyncio.DefaultEventLoopPolicy.get_event_loop
    
    def _patched_policy_get(self):
        try:
            return _orig_policy_get(self)
        except RuntimeError:
            lo = self.new_event_loop()
            self.set_event_loop(lo)
            return lo
    
    asyncio.DefaultEventLoopPolicy.get_event_loop = _patched_policy_get
except Exception as e:
    print(f"⚠️ Partial patch: {e}")

print("✅ Event loop patch applied")

# ==================== HEALTH CHECK SERVER ====================
# Render requires an open port for Web Services
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 10000))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    print(f"✅ Health server started on port {PORT}")
    server.serve_forever()

# Start health server in background thread
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()

# ==================== NOW IMPORT PYROGRAM ====================
from pyrogram import Client
from config import Config

print("✅ Pyrogram imported successfully!")

app = Client(
    name="rename_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=50,
    plugins=dict(root="plugins"),
    sleep_threshold=10
)

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 File Rename Bot Starting...")
    print(f"🌐 Health check: http://0.0.0.0:{PORT}")
    print("=" * 50)
    app.run()