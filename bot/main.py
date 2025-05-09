from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update

from .handlers import Handlers
from .config import config
from .utils.logging import logger

def main():
    """Run the bot."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build() 
    
    handlers = Handlers._instance

    application.add_handler(CommandHandler("start", handlers.start_command))

    application.add_handler(
        MessageHandler(
            (filters.TEXT
            | filters.Document.ALL
            | filters.PHOTO
            | filters.VIDEO
            | filters.AUDIO)
            & ~filters.COMMAND,
            handlers.bot_handler
        )
    )
    
    application.add_handler(CallbackQueryHandler(handlers.button_options)) 

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot is shutting down...")
        handlers.close_all()
        logger.info("Bot has been shut down cleanly")
    finally:
        application.shutdown()
        application.update_queue.put(None)

if __name__ == "__main__":
    main()
