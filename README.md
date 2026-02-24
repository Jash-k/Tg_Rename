# ⚡ Lightning Fast File Rename Bot

A high-performance Telegram bot for renaming files with real-time progress tracking.

## Features

- ⚡ Ultra-fast processing
- 📊 Real-time progress tracking
- 🎬 Auto thumbnail generation
- 📁 Multiple format support
- 🎯 Error handling
- 💾 Memory efficient

## Deployment

### Render.com (Recommended)

1. Fork this repository
2. Create account on [Render.com](https://render.com)
3. New → Web Service
4. Connect your repository
5. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
6. Add environment variables (see below)
7. Deploy!

### Environment Variables

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
ADMIN=your_user_id
LOG_CHANNEL=-100xxxxxxxxx (optional)
MAX_FILE_SIZE=2147483648 (optional)