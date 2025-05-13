import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    ALLOWED_LANGUAGES = ['en', 'es']

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')
    
    # Bot settings
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'virus_scan_ai_bot')
    BOT_NAME = os.getenv('BOT_NAME', 'VScanAI')
    
    # Model settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'openai/gpt-4.1')
    MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT', 'https://models.github.ai/inference')
    
    # Virus scan settings
    SCAN_TIMEOUT = int(os.getenv('SCAN_TIMEOUT', 30))  # seconds
    FILE_LOCATION = os.getenv("FILE_LOCATION", "bot/tmp_files")
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5242880))  # 5MB in bytes
    VT_API_KEY = os.getenv('VT_API_KEY')
    VT_API_TIMEOUT = int(os.getenv('VT_API_TIMEOUT', 500))

config = Config()
