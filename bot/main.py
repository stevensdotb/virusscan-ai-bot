import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update

from .handlers import Handlers
from .config import config
from .utils.logging import logger

# Global application instance and initialization event
application: Application = None
bot_ready = asyncio.Event()

async def init_bot():
    """Create and initialize the Application"""
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
        app.add_handler(CallbackQueryHandler(handlers.button_options))

        # Signal that the bot is ready
        bot_ready.set()
        logger.info("Bot initialized successfully.")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")
        bot_ready.clear()
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global application
    try:
        application = await init_bot()
        if application:
            yield
        else:
            raise RuntimeError("Bot initialization failed.")
    finally:
        if application:
            await application.stop()
            logger.info("Bot shutdown completed.")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Wait until the bot is fully initialized
        await bot_ready.wait()
        if not application:
            raise RuntimeError("Bot application is not initialized.")

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
