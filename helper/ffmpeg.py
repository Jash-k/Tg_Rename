import asyncio
import os
from PIL import Image


async def take_screen_shot(video_file, output_directory, ttl):
    """Generate screenshot from video at given timestamp"""
    out_put_file_name = os.path.join(output_directory, f"{ttl}.jpg")

    cmd = [
        "ffmpeg",
        "-ss", str(ttl),
        "-i", video_file,
        "-vframes", "1",
        "-q:v", "2",
        out_put_file_name,
        "-y"
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await process.communicate()

    if os.path.exists(out_put_file_name):
        return out_put_file_name
    return None


async def fix_thumb(thumb_path):
    """Fix and resize thumbnail"""
    if not thumb_path or not os.path.exists(thumb_path):
        return 0, 0, None

    try:
        img = Image.open(thumb_path)

        # Calculate new dimensions (max 320px)
        if img.width > img.height:
            width = 320
            height = int((img.height / img.width) * 320)
        else:
            height = 320
            width = int((img.width / img.height) * 320)

        # Resize and save
        img = img.resize((width, height))
        img.save(thumb_path, "JPEG")

        return width, height, thumb_path
    except Exception as e:
        print(f"Thumb fix error: {e}")
        return 0, 0, None