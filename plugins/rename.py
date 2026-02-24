from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.utils import progress_for_pyrogram, convert, humanbytes
from asyncio import sleep
from PIL import Image
from config import Config
import os, time, random, shutil


# ==================== FILE RECEIVE ====================
@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name

    if file.file_size > Config.MAX_FILE_SIZE:
        return await message.reply_text(
            "❌ Sorry! Files bigger than 2GB are not supported.",
            quote=True
        )

    try:
        await message.reply_text(
            text=f"**📝 Please Enter New Filename...**\n\n"
                 f"**Old File Name :-** `{filename}`\n"
                 f"**File Size :-** {humanbytes(file.file_size)}",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**📝 Please Enter New Filename...**\n\n"
                 f"**Old File Name :-** `{filename}`",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except Exception as e:
        print(f"Error: {e}")


# ==================== NEW NAME HANDLER ====================
@Client.on_message(filters.private & filters.reply & filters.text)
async def refunc(client, message):
    reply_message = message.reply_to_message

    if not (reply_message.reply_markup and isinstance(reply_message.reply_markup, ForceReply)):
        return

    new_name = message.text.strip()

    # Validate filename
    if len(new_name) > 200:
        return await message.reply_text("❌ Filename too long! Max 200 characters.")

    # Remove invalid characters
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        new_name = new_name.replace(char, '')

    await message.delete()

    # Get original file
    try:
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
    except Exception as e:
        return await message.reply_text(f"❌ Error: Could not find original file.\n`{e}`")

    # Auto-detect extension
    if "." not in new_name:
        if "." in media.file_name:
            extn = media.file_name.rsplit('.', 1)[-1]
        else:
            extn = "mkv"
        new_name = new_name + "." + extn

    await reply_message.delete()

    # Format selection buttons
    button = [[InlineKeyboardButton("📁 Document", callback_data="upload_document")]]

    if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
        button.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
    elif file.media == MessageMediaType.AUDIO:
        button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])

    button.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])

    await message.reply(
        text=f"**Select The Output File Type**\n\n**File Name :-** `{new_name}`",
        reply_to_message_id=file.id,
        reply_markup=InlineKeyboardMarkup(button)
    )


# ==================== UPLOAD HANDLER ====================
@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    user_id = update.from_user.id

    # Extract new filename from message
    try:
        new_name = update.message.text
        new_filename = new_name.split(":-")[1].strip().strip("`")
    except Exception:
        return await update.message.edit("❌ Error: Could not extract filename.")

    # Create download directory
    download_dir = f"downloads/{user_id}"
    os.makedirs(download_dir, exist_ok=True)

    file_path = f"{download_dir}/{new_filename}"
    file = update.message.reply_to_message

    # ==================== DOWNLOAD ====================
    ms = await update.message.edit("🚀 **Downloading...** ⚡")

    c_time = time.time()
    try:
        path = await bot.download_media(
            message=file,
            file_name=file_path,
            progress=progress_for_pyrogram,
            progress_args=("🚀 **Downloading...** ⚡", ms, c_time)
        )
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        return await ms.edit(f"❌ **Download Failed**\n\n`{e}`")

    # ==================== GET METADATA ====================
    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
    except Exception:
        pass

    # ==================== THUMBNAIL ====================
    ph_path = None
    media = getattr(file, file.media.value)

    if media.thumbs:
        try:
            if duration > 0:
                ph_path_ = await take_screen_shot(
                    file_path,
                    os.path.dirname(os.path.abspath(file_path)),
                    random.randint(0, duration - 1) if duration > 1 else 0
                )
            else:
                ph_path_ = None

            if ph_path_:
                width, height, ph_path = await fix_thumb(ph_path_)
        except Exception as e:
            ph_path = None
            print(f"Thumbnail error: {e}")

    # ==================== CAPTION ====================
    caption = f"**{new_filename}**"

    # ==================== UPLOAD ====================
    await ms.edit("💠 **Uploading...** ⚡")

    upload_type = update.data.split("_")[1]
    c_time = time.time()

    try:
        if upload_type == "document":
            await bot.send_document(
                update.message.chat.id,
                document=file_path,
                thumb=ph_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=("💠 **Uploading...** ⚡", ms, c_time)
            )

        elif upload_type == "video":
            await bot.send_video(
                update.message.chat.id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("💠 **Uploading...** ⚡", ms, c_time)
            )

        elif upload_type == "audio":
            await bot.send_audio(
                update.message.chat.id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("💠 **Uploading...** ⚡", ms, c_time)
            )

    except Exception as e:
        try:
            await ms.edit(f"❌ **Upload Failed**\n\n`{e}`")
        except:
            pass
        return
    finally:
        # Cleanup files
        if os.path.exists(file_path):
            os.remove(file_path)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
        # Remove empty directory
        shutil.rmtree(download_dir, ignore_errors=True)

    await ms.delete()

    # Log to channel
    if Config.LOG_CHANNEL:
        try:
            await bot.send_message(
                Config.LOG_CHANNEL,
                f"✅ **File Renamed**\n\n"
                f"**User:** {update.from_user.mention} (`{user_id}`)\n"
                f"**File:** `{new_filename}`\n"
                f"**Size:** {humanbytes(media.file_size)}\n"
                f"**Type:** {upload_type}"
            )
        except:
            pass


# ==================== CANCEL HANDLER ====================
@Client.on_callback_query(filters.regex("cancel"))
async def cancel(bot, update):
    try:
        await update.message.delete()
        await update.answer("❌ Cancelled!", show_alert=True)
    except:
        pass