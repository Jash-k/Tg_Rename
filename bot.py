#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
import warnings

# ==================== Python 3.14 Fix ====================
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

_orig_get_loop = asyncio.get_event_loop

def _patched_get_event_loop():
    try:
        l = _orig_get_loop()
        if l.is_closed():
            raise RuntimeError()
        return l
    except RuntimeError:
        l = asyncio.new_event_loop()
        asyncio.set_event_loop(l)
        return l

asyncio.get_event_loop = _patched_get_event_loop

print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - Event loop ready")

# ==================== Bot Setup ====================
from pyrogram import Client
from config import Config

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
    print("=" * 50)
    app.run()