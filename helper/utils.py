import time
import math


async def progress_for_pyrogram(current, total, ud_type, message, start):
    """Progress callback with optimized updates"""
    now = time.time()
    diff = now - start

    # Update every 5 seconds to avoid flood
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed) if speed > 0 else 0

        # Progress bar
        filled = int(percentage // 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = f"{ud_type}\n\n"
        text += f"[{bar}]\n"
        text += f"**Progress:** {percentage:.1f}%\n"
        text += f"**Done:** {humanbytes(current)} / {humanbytes(total)}\n"
        text += f"**Speed:** {humanbytes(speed)}/s\n"
        text += f"**ETA:** {time_formatter(time_to_completion)}"

        try:
            await message.edit(text=text)
        except Exception:
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
    """Convert seconds to readable time string"""
    if seconds <= 0:
        return "0s"

    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = []

    for name, secs in periods:
        if seconds >= secs:
            value, seconds = divmod(seconds, secs)
            result.append(f"{int(value)}{name}")

    return ' '.join(result[:2]) if result else "0s"


def convert(seconds):
    """Convert seconds to HH:MM:SS format"""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)