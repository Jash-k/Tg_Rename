from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType, ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.ffmpeg import take_screen_shot
from asyncio import sleep
from PIL import Image
import os, time, random, asyncio, shutil
from config import Config

# Initialize bot with optimized settings
app = Client(
    "rename_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=50,  # Increased workers for faster processing
    sleep_threshold=10
)


# ==================== START COMMAND ====================
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user = message.from_user
    text = f"""
👋 **Hello {user.mention}!**

I'm a **Lightning Fast File Rename Bot** ⚡

**Features:**
• ⚡ Ultra-fast processing
• 📁 Rename any file type
• 🎥 Auto thumbnail generation
• 📊 Progress tracking
• 🎯 Multiple format support

**How to use:**
1️⃣ Send me any file
2️⃣ Reply with new name
3️⃣ Choose format
4️⃣ Get renamed file!

**Supported Formats:**
📄 Documents • 🎬 Videos • 🎵 Audio

**Maximum file size:** 2GB

**Commands:**
/start - Start bot
/help - Get help
/about - About bot

**Developed with ❤️**
"""
    
    await message.reply_text(
        text=text,
        disable_web_page_preview=True,
        quote=True
    )


# ==================== HELP COMMAND ====================
@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    help_text = """
**📚 How to Use This Bot**

**Step 1:** Send me any file (Document/Video/Audio)

**Step 2:** I'll ask for a new filename

**Step 3:** Reply with your desired filename
- You can include or exclude extension
- If no extension, I'll auto-detect it

**Step 4:** Choose output format
- 📁 Document (original quality)
- 🎥 Video (with thumbnail)
- 🎵 Audio (with thumbnail)

**Step 5:** Wait for processing
- You'll see real-time progress
- Download & upload speed
- ETA for completion

**Tips for Faster Processing:**
• Use document format for fastest speed
• Smaller files process quicker
• Video format takes longer (thumbnail generation)

**Need Support?**
Contact: @YourSupportChannel
"""
    
    await message.reply_text(help_text, quote=True)


# ==================== ABOUT COMMAND ====================
@app.on_message(filters.command("about") & filters.private)
async def about_cmd(client, message):
    about_text = """
**🤖 About This Bot**

**Bot Name:** File Rename Bot
**Version:** 2.0 Production
**Framework:** Pyrogram
**Language:** Python 3.11

**Features:**
✅ Fast file processing
✅ Auto thumbnail generation
✅ Multiple format support
✅ Progress tracking
✅ Error handling

**Server:** Render.com
**Uptime:** 24/7

**Developer:** @YourChannel
**Support:** @YourSupportChannel

**Open Source:** Coming Soon!
"""
    
    await message.reply_text(about_text, quote=True)


# ==================== FILE HANDLER ====================
@app.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = file.file_size
    
    # Check file size
    if filesize > Config.MAX_FILE_SIZE:
        return await message.reply_text(
            f"⚠️ **File Too Large!**\n\n"
            f"**Your file:** {humanbytes(filesize)}\n"
            f"**Maximum allowed:** {humanbytes(Config.MAX_FILE_SIZE)}\n\n"
            f"Please send a smaller file.",
            quote=True
        )
    
    # Log to channel if configured
    if Config.LOG_CHANNEL:
        try:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"**New File Received**\n\n"
                f"**User:** {message.from_user.mention} (`{message.from_user.id}`)\n"
                f"**Filename:** `{filename}`\n"
                f"**Size:** {humanbytes(filesize)}\n"
                f"**Type:** {message.media.value}"
            )
        except:
            pass

    try:
        await message.reply_text(
            text=f"**📝 Please Enter New Filename**\n\n"
                 f"**Current Name:** `{filename}`\n"
                 f"**Size:** {humanbytes(filesize)}\n\n"
                 f"Send the new filename as a reply to this message.",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**📝 Please Enter New Filename**\n\n"
                 f"**Current Name:** `{filename}`\n"
                 f"**Size:** {humanbytes(filesize)}",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except Exception as e:
        print(f"Error in rename_start: {e}")
        await message.reply_text(
            "❌ An error occurred. Please try again.",
            quote=True
        )


# ==================== NEW NAME HANDLER ====================
@app.on_message(filters.private & filters.reply & filters.text)
async def refunc(client, message):
    reply_message = message.reply_to_message
    
    # Check if it's our ForceReply
    if not (reply_message.reply_markup and isinstance(reply_message.reply_markup, ForceReply)):
        return
    
    new_name = message.text.strip()
    
    # Validate filename
    if len(new_name) > 200:
        return await message.reply_text(
            "❌ Filename too long! Maximum 200 characters.",
            quote=True
        )
    
    # Remove invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        new_name = new_name.replace(char, '')
    
    await message.delete()
    
    # Get original file message
    try:
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
    except:
        return await message.reply_text(
            "❌ Could not find the original file. Please send it again.",
            quote=True
        )
    
    # Add extension if missing
    if "." not in new_name:
        if "." in media.file_name:
            extn = media.file_name.rsplit('.', 1)[-1]
        else:
            # Default extensions based on media type
            default_ext = {
                MessageMediaType.VIDEO: "mkv",
                MessageMediaType.AUDIO: "mp3",
                MessageMediaType.DOCUMENT: "file"
            }
            extn = default_ext.get(file.media, "file")
        new_name = new_name + "." + extn
    
    await reply_message.delete()

    # Create format selection buttons
    buttons = []
    
    # Document button (always available)
    buttons.append([InlineKeyboardButton("📁 Document", callback_data="upload_document")])
    
    # Video button for video and document files
    if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
        buttons.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
    
    # Audio button for audio files
    if file.media == MessageMediaType.AUDIO:
        buttons.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])
    
    # Cancel button
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    
    await message.reply(
        text=f"**✅ New Filename Set**\n\n"
             f"**Filename:** `{new_name}`\n"
             f"**Size:** {humanbytes(media.file_size)}\n\n"
             f"**Select output format:**",
        reply_to_message_id=file.id,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==================== UPLOAD HANDLER ====================
@app.on_callback_query(filters.regex("upload"))
async def doc(client, update):
    # Check if callback is from file owner
    if update.message.reply_to_message.from_user.id != update.from_user.id:
        return await update.answer("❌ This is not your file!", show_alert=True)
    
    user_id = update.from_user.id
    upload_type = update.data.split("_")[1]
    
    # Extract filename from message
    try:
        text = update.message.text
        new_filename = text.split("**Filename:** `")[1].split("`")[0]
    except:
        return await update.message.edit("❌ Error: Could not extract filename.")
    
    file = update.message.reply_to_message
    media = getattr(file, file.media.value)
    
    # Create user-specific download directory
    download_path = os.path.join(Config.DOWNLOAD_LOCATION, str(user_id))
    os.makedirs(download_path, exist_ok=True)
    
    file_path = os.path.join(download_path, new_filename)
    
    ms = await update.message.edit("⚙️ **Processing your request...**")
    
    # Download file
    c_time = time.time()
    try:
        await ms.edit("⏬ **Downloading...**\n\n0%")
        path = await client.download_media(
            message=file,
            file_name=file_path,
            progress=progress_for_pyrogram,
            progress_args=("⏬ **Downloading...**", ms, c_time)
        )
    except Exception as e:
        try:
            await ms.edit(f"❌ **Download Error:**\n\n`{e}`")
        except:
            pass
        # Cleanup
        if os.path.exists(download_path):
            shutil.rmtree(download_path)
        return

    # Get file metadata
    duration = 0
    width = 0
    height = 0
    
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata:
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
    except:
        pass

    # Generate thumbnail for video
    ph_path = None
    if upload_type == "video" and duration > 0:
        try:
            await ms.edit("🎬 **Generating thumbnail...**")
            ph_path = await take_screen_shot(
                file_path,
                download_path,
                random.randint(0, duration - 1) if duration > 1 else 0
            )
            
            # Resize thumbnail
            if ph_path:
                img = Image.open(ph_path)
                img.thumbnail((320, 320))
                img.save(ph_path, "JPEG")
        except Exception as e:
            print(f"Thumbnail generation error: {e}")
            ph_path = None

    # Create caption
    caption = f"**{new_filename}**\n\n"
    caption += f"**📊 Size:** {humanbytes(media.file_size)}\n"
    if duration:
        caption += f"**⏱ Duration:** {convert(duration)}\n"
    caption += f"\n**Renamed by:** @YourBotUsername"

    # Upload file
    c_time = time.time()
    
    try:
        await ms.edit("⏫ **Uploading...**\n\n0%")
        
        if upload_type == "document":
            sent_message = await client.send_document(
                chat_id=update.message.chat.id,
                document=file_path,
                thumb=ph_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=("⏫ **Uploading...**", ms, c_time)
            )
        
        elif upload_type == "video":
            sent_message = await client.send_video(
                chat_id=update.message.chat.id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                width=width,
                height=height,
                progress=progress_for_pyrogram,
                progress_args=("⏫ **Uploading...**", ms, c_time)
            )
        
        elif upload_type == "audio":
            sent_message = await client.send_audio(
                chat_id=update.message.chat.id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("⏫ **Uploading...**", ms, c_time)
            )
        
        # Success message
        try:
            await ms.edit(
                f"✅ **File Renamed Successfully!**\n\n"
                f"**New Name:** `{new_filename}`\n"
                f"**Size:** {humanbytes(media.file_size)}\n"
                f"**Type:** {upload_type.title()}"
            )
        except:
            await ms.delete()
        
        # Log to channel
        if Config.LOG_CHANNEL:
            try:
                await client.send_message(
                    Config.LOG_CHANNEL,
                    f"**✅ File Renamed**\n\n"
                    f"**User:** {update.from_user.mention} (`{user_id}`)\n"
                    f"**Filename:** `{new_filename}`\n"
                    f"**Size:** {humanbytes(media.file_size)}\n"
                    f"**Format:** {upload_type.title()}"
                )
            except:
                pass
        
    except Exception as e:
        try:
            await ms.edit(f"❌ **Upload Error:**\n\n`{e}`")
        except:
            pass
        print(f"Upload error: {e}")
    
    finally:
        # Cleanup
        try:
            if os.path.exists(download_path):
                shutil.rmtree(download_path)
        except Exception as e:
            print(f"Cleanup error: {e}")


# ==================== CANCEL HANDLER ====================
@app.on_callback_query(filters.regex("cancel"))
async def cancel(client, update):
    try:
        await update.message.delete()
        await update.answer("❌ Cancelled!", show_alert=True)
    except:
        pass


# ==================== ADMIN COMMANDS ====================
@app.on_message(filters.command("stats") & filters.user(Config.ADMIN))
async def stats(client, message):
    total_users = await client.get_users("me")
    await message.reply_text(
        f"**📊 Bot Statistics**\n\n"
        f"**Bot:** @{(await client.get_me()).username}\n"
        f"**Uptime:** Running\n"
        f"**Server:** Render.com"
    )


@app.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast(client, message):
    msg = message.reply_to_message
    users = []  # Implement user storage if needed
    
    if not users:
        return await message.reply_text("❌ No users to broadcast to.")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await msg.copy(user_id)
            success += 1
        except:
            failed += 1
    
    await message.reply_text(
        f"**Broadcast Complete**\n\n"
        f"**Success:** {success}\n"
        f"**Failed:** {failed}"
    )


# ==================== ERROR HANDLER ====================
@app.on_message(filters.private & filters.command("") & ~filters.text)
async def unknown_command(client, message):
    await message.reply_text(
        "❓ **Unknown command!**\n\n"
        "Use /help to see available commands."
    )


# ==================== CLEANUP ON START ====================
async def cleanup_downloads():
    """Clean up download folder on startup"""
    if os.path.exists(Config.DOWNLOAD_LOCATION):
        try:
            shutil.rmtree(Config.DOWNLOAD_LOCATION)
        except:
            pass
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)


# ==================== BOT STARTUP ====================
async def main():
    await cleanup_downloads()
    print("=" * 50)
    print("🚀 Bot Started Successfully!")
    print("=" * 50)
    print(f"📱 Bot Username: @{(await app.get_me()).username}")
    print(f"👤 Bot Name: {(await app.get_me()).first_name}")
    print("=" * 50)


if __name__ == "__main__":
    app.start()
    asyncio.get_event_loop().run_until_complete(main())
    print("✅ Bot is running... Press Ctrl+C to stop")
    from pyrogram import idle
    idle()