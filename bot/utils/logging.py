import logging

def setup_logging():
    """Set up logging configuration."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
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
