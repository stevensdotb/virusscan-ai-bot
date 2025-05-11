from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.exceptions import HttpResponseError

from .config import config
from .utils.logging import logger

class LLMClient:
    def __init__(self):
        """Initialize the LLM client."""
        self.client = ChatCompletionsClient(
            endpoint=config.MODEL_ENDPOINT,
            credential=AzureKeyCredential(config.OPENAI_API_KEY)
        )
        self.VT_LINK_ASK = "Provide the VirusTotal link of the analysis."

    def analyze_vt_results(self, vt_result_or_text: str, lang: str) -> str:
        """
        Analyze a file using GitHub model to determine if it might be malicious.
        """
        system_prompt = f"""
        You are a bot named "{config.BOT_NAME}" that analyzes files and URLs to determine if they are malicious.
        You will be provided with the VirusTotal analysis results and must provide a clear, concise explanation.
        
        Your response format should be:

        For files (without the file name):
        <emoji> FILE <status>:
        File type: <file_type> <KB/MB/GB>
        Size: <size>

        For URLs:
        <emoji> URL <status>:
        URL type: <url_type>

        Write the analysis results for files and urls in HTML format as telegram docs suggest https://core.telegram.org/bots/api#html-style 
        - Add bold, italics, etc.
        - For breaklines do it directly instead of using <br>.
        - No nested tags are allowed.
        - Use emojis without tag-emojis tag.
        - Currently supported tags are: <b>, <strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>, <span class="tg-spoiler">, <tg-spoiler>, <a>, <tg-emoji>, <code>, <pre>, <blockquote>, <blockquote expandable>

        For the file status use the following emojis:
        - ✅: For safe files/urls
        - ⚠️: For suspicious files/urls
        - ❌: For malicious files/urls

        At the end, add the <link> tag to the VirusTotal analysis and ask if the user wants to analyze another file or URL.

        The bot language should be '{lang}'.

        For other topics to discuss, you can only:
        - Talk about Bot's functionality:
        - Answer questions about the analysis information you provided.
        - Provide security information about preventing cyber attacks.
        - Inform that files are analyzed in memory and not stored for any reason.
        - Inform that topics related to software creation and malware, etc., are not allowed.
        
        Greetings, thanks, etc. are allowed. Ignore stickers, gifs, and emojis sent by the user and don't respond to them.

        For any other topics, briefly respond that you are not authorized to discuss them and ask if the user wants to analyze another file or URL.
        You will always respond in first person and will use emojis to make the responses more friendly.
        """
        try:
            # Call GitHub model API
            response = self.client.complete(
                model=config.MODEL_NAME,
                messages=[
                    SystemMessage(system_prompt),
                    UserMessage(vt_result_or_text)
                ]
            )
            return response.choices[0].message.content
            
        except HttpResponseError as e:
            logger.error(f"Error with GitHub model: {e.status_code} ({e.reason})")
            logger.error(f"{e.message}") 
            return e.message

    def close(self):
        """Close the LLM client connection."""
        self.client.close()
