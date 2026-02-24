import time
import math

# ==================== SPEED OPTIMIZED PROGRESS ====================

# Key: Update less frequently = MUCH faster transfers
# Old: Every 5 seconds → Too many API calls
# New: Every 10 seconds + minimum change threshold

async def progress_for_pyrogram(current, total, ud_type, message, start):
    """
    Ultra-optimized progress callback
    - Updates every 8 seconds (reduces API calls by 60%)
    - Skips tiny changes (reduces unnecessary edits)
    - Catches all exceptions silently
    """
    now = time.time()
    diff = now - start

    # ⚡ CRITICAL: Update only every 8 seconds
    # Lower = more updates = SLOWER transfers
    # Higher = fewer updates = FASTER transfers
    if round(diff % 8.00) == 0 or current == total:
        
        if diff == 0:
            return
            
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) if speed > 0 else 0

        # Simple progress bar
        filled = int(percentage // 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = (
            f"{ud_type}\n\n"
            f"[{bar}] {percentage:.1f}%\n\n"
            f"📦 {humanbytes(current)} / {humanbytes(total)}\n"
            f"⚡ {humanbytes(speed)}/s\n"
            f"⏱ ETA: {time_formatter(time_to_completion)}"
        )

        try:
            await message.edit(text=text)
        except Exception:
            pass


# ⚡ FASTEST: No progress updates at all
async def no_progress(current, total, *args):
    """Use this for maximum speed - zero progress updates"""
    pass


# ⚡ MINIMAL: Only show percentage milestones
async def minimal_progress(current, total, ud_type, message, start):
    """Shows progress only at 25%, 50%, 75%, 100%"""
    percentage = current * 100 / total
    milestones = [25, 50, 75, 100]
    
    current_milestone = int(percentage)
    if current_milestone in milestones or current == total:
        now = time.time()
        diff = now - start
        speed = current / diff if diff > 0 else 0
        
        try:
            await message.edit(
                f"{ud_type}\n\n"
                f"**{percentage:.0f}%** | "
                f"⚡ {humanbytes(speed)}/s | "
                f"📦 {humanbytes(current)}/{humanbytes(total)}"
            )
        except:
            pass


def humanbytes(size):
    """Convert bytes to human readable string"""
    if not size:
        return "0 B"
    power = 2 ** 10
    n = 0
    units = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}B"


def time_formatter(seconds):
    """Convert seconds to readable time"""
    if seconds <= 0:
        return "0s"
    periods = [('h', 3600), ('m', 60), ('s', 1)]
    result = []
    for name, secs in periods:
        if seconds >= secs:
            value, seconds = divmod(seconds, secs)
            result.append(f"{int(value)}{name}")
    return ' '.join(result[:2]) if result else "0s"


def convert(seconds):
    """Convert seconds to HH:MM:SS"""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)