import os
import logging
from pathlib import Path
from types import NoneType
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import httpx
import gettext
from .config import config
from .llm_client import LLMClient
from .vt_client import VTClient


logger = logging.getLogger(__name__)
# Set up gettext
localedir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
print(localedir)

def get_translation(lang: str):
    return gettext.translation('messages', localedir=localedir, languages=[lang], fallback=True)

class FileHandler:
    @staticmethod
    async def get_file(file_msg: Message):
        if file_msg.photo:
            return await file_msg.photo[-1].get_file(), "Photo"
        elif file_msg.video:
            return await file_msg.animation.get_file(), "Video"
        elif file_msg.audio:
            return await file_msg.audio.get_file(), "Audio"
        elif file_msg.document:
            mime_type = file_msg.document.mime_type
            
            if mime_type == 'video/mp4':
                return None, None

            file_type = "Document" if mime_type != "image/gif" else "Animation/GIF"
            return await file_msg.document.get_file(), file_type
        else:
            return None, None

class Handlers:
    def __init__(self):
        self.vt_client = VTClient()
        self.llm_client = LLMClient()
        self.http_client = httpx.AsyncClient()

    async def close(self):
        await self.vt_client.close()
        await self.http_client.aclose()

    async def button_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button presses."""
        query = update.callback_query
        _ = get_translation(update.effective_user.language_code[:2]).gettext
        
        # CallbackQueries need to be answered, even if no notification to the user is needed
        await query.answer()

        if query.data == 'check_ip':
            try:
                ip = await self.get_public_ip()
                await update.effective_message.reply_text(
                    _("BOT_PUBLIC_IP").format(ip=ip)
                )
            except Exception as e:
                await update.effective_message.reply_text(
                    _("BOT_ERROR_IP_RETRIEVAL")
                )
                logging.error(_(f"Error getting public IP: {str(e)}"))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        _ = get_translation(user.language_code[:2]).gettext
        keyboard = [
            [
                InlineKeyboardButton(_("BOT_BUTTON_CHECK_IP"), callback_data='check_ip')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            _("BOT_WELCOME_MESSAGE").format(user=user, config=config) + "\n\n"
            + _("BOT_FUNCTION_DESCRIPTION") + "\n\n"
            + _("BOT_REQUEST_FILE_OR_URL"),
            reply_markup=reply_markup
        )

    async def get_public_ip(self) -> str:
        """Get the user's public IP address."""
        try:
            response = await self.http_client.get('https://api.ipify.org?format=json')
            response.raise_for_status()
            return response.json()['ip']
        except Exception as e:
            logging.error(_(f"Error getting public IP: {str(e)}"))


    async def url_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle URL analysis."""
        _ = get_translation(update.effective_user.language_code[:2]).gettext

        try:
            # Get the URL from the message
            url = update.message.text
            
            # Validate URL format
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                await update.message.reply_text(
                    _("❌ Invalid URL. Please make sure the URL includes (http:// or https://).\nExample: https://google.com")
                )
                return
            
            response_message = await update.message.reply_text(_("⏳ Analyzing URL..."))

            # Analyze the URL with VirusTotal
            vt_result = await self.vt_client.analyze_url(url)

            await response_message.edit_text(vt_result)

        except Exception as e:
            logging.error(_(f"Error with VirusTotal URL analysis: {str(e)}"))
            await response_message.edit_text(_("❌ Sorry, there was an error analyzing the URL."))

    async def file_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle file uploads."""
        
        file, file_type = await FileHandler.get_file(update.message)    
        
        if file is not None:
            # Path to save the file
            file_path = os.path.join(config.FILE_LOCATION, file.file_path.split('/')[-1])

            try:
                if file.file_size > config.MAX_FILE_SIZE:
                    await update.message.reply_text(_("BOT_ERROR_FILE_TOO_LARGE"))
                    return
                    
                response_message = await update.message.reply_text(_("BOT_STATUS_ANALYZING_FILE"))

                #Download the file
                await file.download_to_drive(file_path)

                # Analyze the file with VirusTotal
                vt_result = await self.vt_client.analyze_file(file_path)
                is_malicious = vt_result['stats']['malicious'] >= 3
                is_suspicious = vt_result['stats']['suspicious'] > 0 or (vt_result['stats']['malicious'] >= 1 and vt_result['stats']['malicious'] < 3)

                # Format the response
                safety_status = _("BOT_FILE_STATUS_SAFE")
                
                if is_malicious:
                    safety_status = _("BOT_FILE_STATUS_DANGEROUS")
                
                if is_suspicious:
                    safety_status = _("BOT_FILE_STATUS_SUSPICIOUS")
                    safety_status += _("BOT_FILE_SUSPICIOUS_WARNING")

                response = f"{safety_status}\n\n"
                response += _("BOT_FILE_TYPE").format(file_type=file_type) + "\n"
                response += _("BOT_FILE_SIZE").format(vt_result=vt_result) + "\n"
                response += _("BOT_DETECTION_RESULTS") + "\n"
                
                response += self._format_detection_details(vt_result['results'])
                await response_message.edit_text(response)

            except Exception as e:
                logging.error(f"Error with VirusTotal analysis: {str(e)}")
                await update.message.reply_text(_("BOT_ERROR_FILE_ANALYSIS"))
            finally:
                #Clean up
                os.remove(file_path)

    def _format_detection_details(self, details: Dict[str, Any]) -> str:
        """Format detection details from VirusTotal."""
        formatted = []
        for engine, result in details.items():
            if result['category'] == 'malicious':
                formatted.append(f"- {engine}: {result['result']}")
        return '\n'.join(formatted) if formatted else _("BOT_NO_THREATS")

handlers = Handlers()
