from pyrogram import Client, filters


@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        f"👋 **Hello {message.from_user.mention}!**\n\n"
        "I'm a **Fast File Rename Bot** ⚡\n\n"
        "📤 Send me any file\n"
        "✏️ Enter new name\n"
        "✅ Get renamed file!\n\n"
        "**Simple. Fast. No extra steps.**",
        quote=True
    )