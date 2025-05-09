import os
import json
from urllib.parse import urlparse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
import httpx

from .config import config
from .llm_client import LLMClient
from .vt_client import VTClient
from .file_handler import FileHandler
from .locale_manager import locale_manager
from .utils.logging import logger


class Handlers:
    """Class to handle all bot commands and messages."""

    def __init__(self):
        """Initialize the handlers."""
        self.llm_client = LLMClient()
        self.vt_client = VTClient()
        self.http_client = httpx.AsyncClient()

        self._response_message = None
        self._lang = None

    def _get_translation(self, lang: str):
        """Get translation for the given language."""
        return locale_manager.get_translation(lang)
    
    async def _get_public_ip(self) -> str:
        """Get the user's public IP address."""
        try:
            response = await self.http_client.get('https://api.ipify.org?format=json')
            response.raise_for_status()
            return response.json()['ip']
        except Exception as e:
            logger.error(_(f"Error getting public IP: {str(e)}"))

    def _is_url(self, text: str) -> bool:
        """Check if the given text is a valid URL."""
        try:
            result = urlparse(text)
            if not all([result.scheme, result.netloc]):
                return False
            if result.scheme not in ['http', 'https']:
                return False
            if '.' not in result.netloc:
                return False
            if result.path and result.path == '/':
                return False

            return True
        except Exception:
            return False
    
    def _set_lang(self, lang: str) -> None:
        """Set the language for the bot."""
        if self._lang is None:
            self._lang = lang
    
    def _ai_response(self, text: str):
        """Get the AI response for the given text."""
        return self.llm_client.analyze_vt_results(text, self._lang)
        
    async def close(self):
        """Close the handlers."""
        try:
            await self.vt_client.close()
            await self.http_client.aclose()
        except Exception as e:
            logger.error(f"Error closing handlers: {str(e)}")
            self._response_message = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        self._set_lang(update.effective_user.language_code)
        _ = self._get_translation(self._lang[:2]).gettext

        keyboard = [
            [
                InlineKeyboardButton(_("BOT_BUTTON_CHECK_IP"), callback_data='check_ip')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            _("BOT_WELCOME_MESSAGE").format(user=update.effective_user, config=config) + "\n\n"
            + _("BOT_FUNCTION_DESCRIPTION") + "\n\n"
            + _("BOT_REQUEST_FILE_OR_URL"),
            reply_markup=reply_markup
        )

    async def button_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button presses."""
        query = update.callback_query
        _ = self._get_translation(self._lang[:2]).gettext
        
        # CallbackQueries need to be answered, even if no notification to the user is needed
        await query.answer()

        if query.data == 'check_ip':
            try:
                ip = await self._get_public_ip()
                await update.effective_message.reply_text(
                    _("BOT_PUBLIC_IP").format(ip=ip)
                )
            except Exception as e:
                await update.effective_message.reply_text(
                    _("BOT_ERROR_IP_RETRIEVAL")
                )
                logger.error(_(f"Error getting public IP: {str(e)}"))

    async def bot_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle bot messages (user text, files, urls)."""
        self._set_lang(update.effective_user.language_code)
        _ = self._get_translation(self._lang[:2]).gettext

        user_message = update.message.text

        if self._is_url(user_message):
            user_message = json.dumps(await self.get_url_analysis(update, user_message))
        
        if file := await FileHandler.get_file(update.message):
            user_message = json.dumps(await self.get_file_analysis(update, file))
        
        response = self._ai_response(user_message)
        escaped_text = escape_markdown(response, version=2)
    
        if self._response_message is not None:
            await self._response_message.edit_text(escaped_text, parse_mode=ParseMode.MARKDOWN_V2)
            self._response_message = None
        else:
            await update.message.reply_text(response)

    async def get_file_analysis(self, update: Update, file) -> None:
        """Handle file uploads."""
        _ = self._get_translation(self._lang[:2]).gettext

        self._response_message = await update.message.reply_text(_("BOT_STATUS_ANALYZING_FILE"))

        # Path to save the file
        file_path = os.path.join(config.FILE_LOCATION, file.file_path.split('/')[-1])

        try:
            # Save the file
            await FileHandler.save_file(file, file_path)
            # Analyze the file with VirusTotal
            return await FileHandler.analyze_file(file_path, self.vt_client)
        except Exception as e:
            logger.exception(f"Error with VirusTotal File analysis: {str(e)}")
            await self._response_message.edit_text(_("BOT_ERROR_FILE_ANALYSIS"))
        finally:
            #Clean up
            os.remove(file_path)

    async def get_url_analysis(self, update: Update, url: str) -> None:
        """Handle URL messages."""
        _ = self._get_translation(self._lang[:2]).gettext
        self._response_message = await update.message.reply_text(_("BOT_STATUS_ANALYZING_URL"))
        try:
            # Analyze the URL with VirusTotal
            return await self.vt_client.analyze_url(url)
        except Exception as e:
            logger.error(f"Error with VirusTotal URL analysis: {str(e)}")
            await self._response_message.edit_text(_("BOT_ERROR_URL_ANALYSIS"))

    @classmethod
    async def close_all(cls):
        """Close all instances of handlers."""
        if hasattr(cls, '_instance') and cls._instance:
            await cls._instance.close()

Handlers._instance = Handlers()
