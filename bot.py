#!/usr/bin/env python3
import sys
import asyncio
import warnings
import threading
import os

print(f"🐍 Python Version: {sys.version}")

# ==================== PYTHON 3.14 FIX ====================
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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

try:
    import asyncio.events
    asyncio.events._get_event_loop = _patched
    _orig_policy_get = asyncio.DefaultEventLoopPolicy.get_event_loop
    def _patched_policy_get(self):
        try:
            return _orig_policy_get(self)
        except RuntimeError:
            lo = self.new_event_loop()
            self.set_event_loop(lo)
            return lo
    asyncio.DefaultEventLoopPolicy.get_event_loop = _patched_policy_get
except:
    pass

print("✅ Event loop patch applied")

# ==================== HEALTH SERVER ====================
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 10000))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot Running!")
    def log_message(self, format, *args):
        pass

def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    server.serve_forever()

health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()
print(f"✅ Health server on port {PORT}")

# ==================== BOT WITH SPEED OPTIMIZATIONS ====================
from pyrogram import Client
from config import Config

app = Client(
    name="rename_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=200,          # ⚡ Maximum concurrent workers
    sleep_threshold=30,   # ⚡ Higher threshold = fewer delays
    max_concurrent_transmissions=10,  # ⚡ Parallel file transfers
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Fast Rename Bot Starting...")
    print("⚡ Workers: 200")
    print("⚡ Max Concurrent Transfers: 10")
    print("=" * 50)
    app.run()