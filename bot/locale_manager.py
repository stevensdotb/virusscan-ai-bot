import gettext
from pathlib import Path

from config import config

class LocaleManager:
    """Class to manage locale translations."""

    def __init__(self):
        """Initialize the locale manager."""
        # Get the path to the locales directory
        self.localedir = Path(__file__).parent.parent / 'locales'
        
        # Create the locales directory if it doesn't exist
        self.localedir.mkdir(parents=True, exist_ok=True)

    def get_translation(self, lang: str) -> gettext.GNUTranslations:
        """Get translation for the given language."""
        translation = gettext.translation(
            'messages',
            localedir=str(self.localedir),
            languages=[lang if lang in config.ALLOWED_LANGUAGES else 'en'],
            fallback=True
        )
        return translation

# Create a singleton instance
locale_manager = LocaleManager()
