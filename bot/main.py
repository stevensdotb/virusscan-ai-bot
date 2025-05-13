import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from telegram.error import TelegramError

from .handlers import Handlers
from .config import config
from .utils.logging import logger

# Global application instance and condition variable for initialization
application: Application = None
bot_ready = asyncio.Condition()

async def refresh_webhook():
    """Refresh the webhook for a fresh start."""
    try:
        await application.bot.delete_webhook()
        await application.bot.set_webhook(config.TELEGRAM_WEBHOOK_URL)
    except TelegramError as e:
        logger.error(f"Failed to set/delete webhook: {str(e)}")

async def init_bot():
    """Create and initialize the Telegram bot application."""
    handlers = Handlers._instance
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    try:
        # Initialize the application
        await app.initialize()

        # Add handlers
        app.add_handler(CommandHandler("start", handlers.start_command))
        app.add_handler(
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

        # Signal that the bot is ready
        async with bot_ready:
            global application
            application = app
            await refresh_webhook()
            bot_ready.notify_all()
        
        logger.info("Telegram bot initialized successfully.")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_bot()
        yield
    finally:
        if application.running:
            await application.stop()
            logger.info("Telegram bot shutdown completed.")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Wait for the bot to be fully initialized
        async with bot_ready:
            await bot_ready.wait_for(lambda: application is not None)

        # Get the raw data from the request
        data = await request.json()
        update = Update.de_json(data, application.bot)

        # Process the update
        await application.process_update(update)

        return JSONResponse(status_code=200, content={"status": "success"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "healthy"})
