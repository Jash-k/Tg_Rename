from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ForceReply
from helper.utils import progress_for_pyrogram, humanbytes
from config import Config
from asyncio import sleep
import os, time, shutil


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name

    if file.file_size > Config.MAX_FILE_SIZE:
        return await message.reply_text("❌ Files bigger than 2GB not supported.", quote=True)

    try:
        await message.reply_text(
            text=f"**📝 Enter New Filename**\n\n**Old Name :-** `{filename}`\n**Size :-** {humanbytes(file.file_size)}",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except FloodWait as e:
        await sleep(e.value)
    except:
        pass


@Client.on_message(filters.private & filters.reply & filters.text)
async def refunc(client, message):
    reply_message = message.reply_to_message

    if not (reply_message.reply_markup and isinstance(reply_message.reply_markup, ForceReply)):
        return

    new_name = message.text.strip()

    if len(new_name) > 200:
        return await message.reply_text("❌ Filename too long!")

    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        new_name = new_name.replace(char, '')

    await message.delete()

    try:
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
    except:
        return await message.reply_text("❌ File not found. Send again.")

    if "." not in new_name:
        if "." in media.file_name:
            extn = media.file_name.rsplit('.', 1)[-1]
        else:
            extn = "mkv"
        new_name = new_name + "." + extn

    await reply_message.delete()

    user_id = message.from_user.id
    file_size = media.file_size
    download_dir = f"downloads/{user_id}"
    os.makedirs(download_dir, exist_ok=True)
    file_path = f"{download_dir}/{new_name}"

    # ==================== DOWNLOAD ====================
    ms = await message.reply(f"🚀 **Downloading...** ⚡\n\n📁 `{new_name}`")

    c_time = time.time()
    try:
        if file_size < 50 * 1024 * 1024:
            await client.download_media(message=file, file_name=file_path)
        else:
            await client.download_media(
                message=file,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=("🚀 **Downloading...** ⚡", ms, c_time)
            )
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        return await ms.edit(f"❌ Download Failed\n\n`{e}`")

    download_time = time.time() - c_time

    # ==================== UPLOAD ====================
    await ms.edit(f"💠 **Uploading...** ⚡\n\n📁 `{new_name}`")

    c_time = time.time()
    try:
        if file_size < 50 * 1024 * 1024:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=f"**{new_name}**",
                force_document=True
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=f"**{new_name}**",
                force_document=True,
                progress=progress_for_pyrogram,
                progress_args=("💠 **Uploading...** ⚡", ms, c_time)
            )
    except Exception as e:
        await ms.edit(f"❌ Upload Failed\n\n`{e}`")
        return
    finally:
        shutil.rmtree(download_dir, ignore_errors=True)

    # Done
    upload_time = time.time() - c_time
    total_time = download_time + upload_time

    try:
        await ms.edit(
            f"✅ **Done!**\n\n"
            f"📁 `{new_name}`\n"
            f"📦 {humanbytes(file_size)} | ⏱ {round(total_time)}s"
        )
    except:
        try:
            await ms.delete()
        except:
            pass