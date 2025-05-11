from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update

from .handlers import Handlers
from .config import config
from .utils.logging import logger


async def init_bot():
    """Create and initialize the Application"""
    handlers = Handlers._instance
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Initialize the application
    await application.initialize()

    # Add handlers directly to the application
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
    
    return application


# Initialize the Telegram bot and add all the handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    global application
    application = await init_bot()
    yield
    pass


app = FastAPI(lifespan=lifespan)


application: Application = None

async def get_bot_app() -> Application:
    if application is None:
        raise RuntimeError("Application not initialized")
    return application


@app.post("/webhook")
async def webhook(request: Request, bot_app: Application = Depends(get_bot_app)):
    try:
        # Get the raw data from the request
        data = await request.json()
        
        # Process the update
        update = Update.de_json(data, bot_app.bot)
        await bot_app.process_update(update)
        
        return JSONResponse(status_code=200, content={"status": "success"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "healthy"})
