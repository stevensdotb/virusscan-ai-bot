import os
import base64

from vt import Client, APIError

from .config import config
from .utils.logging import logger
from .decorators import retry_on_reached_limit

class VTClient:
    def __init__(self):
        """Initialize the VirusTotal client."""
        self.client = Client(config.VT_API_KEY, timeout=config.VT_API_TIMEOUT)
        self._error_codes = {
            400: "Invalid API key",
            429: "Rate limit exceeded"
        }

    async def _handle_api_error(self, e: APIError, delay=None):
        if e.code == 429 and delay is not None:
            logger.info(f"{self._error_codes[e.code]}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
        else:
            raise Exception(f"{self._error_codes.get(e.code, f'API Error ({e.code})')}: {e.message}")

    @retry_on_reached_limit(APIError, exception_handler=_handle_api_error, retries=3, delay=10)
    async def analyze_file(self, file_path: str) -> dict[str,any]:
        """Analyze a file using VirusTotal."""
        # Upload the file
        with open(file_path, 'rb') as f:
            analysis = await self.client.scan_file_async(f, wait_for_completion=True)
        
        result = analysis.to_dict() 
        result.update({
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'link': self._get_analysis_url(analysis.id)
        })
        # Extract relevant information
        return result
    
    @retry_on_reached_limit(APIError, exception_handler=_handle_api_error, retries=3, delay=10)
    async def analyze_url(self, url: str) -> dict[str, any]:
        """Analyze a URL using VirusTotal."""
        # Get URL analysis
        analysis = await self.client.scan_url_async(url)
        result = analysis.to_dict()
        result.update({
            'url': url,
            'link': self._get_analysis_url(analysis.id)
        })
        # Extract relevant information
        return result

    def _get_analysis_url(self, analysis_id: str) -> str:
        # URL analysis
        if analysis_id.startswith('u-'):
            _, hash_value, _ = analysis_id.split('-')
            return f"https://www.virustotal.com/gui/url/{hash_value}"
        
        # File analysis
        decode_id = base64.b64decode(analysis_id).decode('utf-8')
        hash_value, _ = decode_id.split(':')
        return f"https://www.virustotal.com/gui/file/{hash_value}/analysis"

    async def close(self):
        """Close the VirusTotal client."""
        try:
            await self.client.close()
        except Exception as e:
            logger.error(f"Error closing VirusTotal client: {str(e)}")
