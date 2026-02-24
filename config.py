import os

class Config:
    # Required
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Optional
    ADMIN = list(set(int(x) for x in os.environ.get("ADMIN", "0").split()))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    
    # File size limit (in bytes) - 2GB default
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))
    
    # Download location
    DOWNLOAD_LOCATION = "./downloads"