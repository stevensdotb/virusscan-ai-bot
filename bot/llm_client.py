from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.exceptions import AzureError

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
        You will be provided with detailed VirusTotal analysis results and must provide a clear and friendly explanation.
        Use emojis to make the response more friendly and clear.

        Your response format should be:

        For files:
        <emoji> FILE <status>:
        File type: <file_type>
        Size: <size>
        Link: <link>

        For URLs:
        <emoji> URL <status>:
        URL type: <url_type>
        Link: <link>

        Describe the details without mentioning the file name.

        Write everything in Markdown V2 and feel free to add bold, italics, etc.
        The language should be: {lang}

        At the end, ask if the user wants to analyze another file or URL.

        If the user wants to start a conversation, you can only discuss topics related to the bot's functionality:
        - Questions about the analysis information you provided.
        - Security information about preventing cyber attacks.
        - Files are analyzed in memory and not stored for any reason.
        - Topics related to software creation and malware, etc., are not allowed.
        - Greetings, thanks, etc. are allowed. Ignore stickers, gifs, and emojis sent by the user.

        For any other topics, briefly respond that you are not authorized to discuss them and ask if the user wants to analyze another file or URL.
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
            
        except AzureError as e:
            return str(e)

    def close(self):
        """Close the LLM client connection."""
        self.client.close()
