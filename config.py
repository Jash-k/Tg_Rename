import os

class Config:
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    ADMIN = int(os.environ.get("ADMIN", "0"))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    DOWNLOAD_LOCATION = "./downloads"
    MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB