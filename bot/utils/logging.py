import logging
import os
from pathlib import Path

def setup_logging():
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Create a rotating file handler
    log_file = logs_dir / 'bot.log'
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

# Set up logging when this module is imported
setup_logging()

# Create a root logger for the bot
logger = get_logger('bot')
