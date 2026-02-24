import time
import math

async def progress_for_pyrogram(current, total, ud_type, message, start):
    """Optimized progress callback"""
    now = time.time()
    diff = now - start
    
    # Update every 3 seconds or when complete
    if round(diff % 3.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed) if speed > 0 else 0
        
        # Progress bar
        filled = int(percentage // 5)
        bar = "█" * filled + "░" * (20 - filled)
        
        # Format message
        text = f"{ud_type}\n\n"
        text += f"[{bar}] {percentage:.1f}%\n\n"
        text += f"📊 **Size:** {humanbytes(current)} / {humanbytes(total)}\n"
        text += f"⚡ **Speed:** {humanbytes(speed)}/s\n"
        text += f"⏱ **ETA:** {format_time(time_to_completion)}\n"
        text += f"⏳ **Elapsed:** {format_time(elapsed_time)}"
        
        try:
            await message.edit(text=text)
        except Exception as e:
            pass


def humanbytes(size):
    """Convert bytes to human readable format"""
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"


def format_time(seconds):
    """Format seconds to readable time"""
    if seconds == 0:
        return "0s"
    
    periods = [
        ('d', 86400),
        ('h', 3600),
        ('m', 60),
        ('s', 1)
    ]
    
    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f"{int(period_value)}{period_name}")
    
    return ' '.join(result[:2])  # Show max 2 units


def convert(seconds):
    """Convert seconds to HH:MM:SS"""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)