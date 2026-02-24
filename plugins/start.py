from pyrogram import Client, filters
from config import Config


@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    text = f"""
👋 **Hello {message.from_user.mention}!**

I'm a **Fast File Rename Bot** ⚡

**How to Use:**
1️⃣ Send me any file
2️⃣ Enter new filename
3️⃣ Choose output format
4️⃣ Get your renamed file!

**Supported:**
📄 Documents | 🎬 Videos | 🎵 Audio

**Max Size:** 2GB

**Commands:**
/start - Start
/help - Help

**Fast & Simple - No Login Required!**
"""
    await message.reply_text(text, quote=True)


@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    text = """
**📚 How To Rename Files**

**Step 1:** Send any file to me
**Step 2:** I'll show current filename
**Step 3:** Reply with new filename
**Step 4:** Choose format (Document/Video/Audio)
**Step 5:** Wait for download & upload

**Tips:**
• No need to add extension - auto detected!
• Choose 📁 Document for fastest speed
• 🎥 Video format generates thumbnail

**Example:**
Old: video_2024_01_15.mkv
New: Avengers Endgame 2019 1080p
Result: Avengers Endgame 2019 1080p.mkv

text

"""
    await message.reply_text(text, quote=True)