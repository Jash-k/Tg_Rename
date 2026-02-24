import asyncio
import os

async def take_screen_shot(video_file, output_directory, ttl):
    """Generate thumbnail from video at given timestamp"""
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