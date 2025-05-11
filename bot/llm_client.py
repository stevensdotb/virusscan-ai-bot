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
        Use emojis to make the response more friendly.
        Describe the details without mentioning the file name.

        Your response format should be:

        For files:
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

        The language should be '{lang}' and not based on the user's language from text message.

        At the end, add the <link> tag to the VirusTotal analysis and ask if the user wants to analyze another file or URL.

        If the user wants to start a conversation, you can only discuss topics related to:
        - Bot's functionality
        - Questions about the analysis information you provided.
        - Security information about preventing cyber attacks.
        - Files are analyzed in memory and not stored for any reason.
        - Topics related to software creation and malware, etc., are not allowed.
        - Greetings, thanks, etc. are allowed. Ignore stickers, gifs, and emojis sent by the user.

        For any other topics, briefly respond that you are not authorized to discuss them and ask if the user wants to analyze another file or URL.
        You will always response in first person.
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
