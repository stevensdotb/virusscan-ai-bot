# Virus Scan AI Bot

A Telegram bot that uses AI to analyze files and URLs for potential malware threats.

## Features

- Real-time File and URL analysis using VirusTotal
- Tips and recommendations based on the analysis
- Multi-language support (English and Spanish)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/stevensdotb/virusscan-ai-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your API keys:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_WEBHOOK_URL`
  - `VT_API_KEY`
  - `OPENAI_API_KEY` (Github Personal [Fine grained] Access Token)

4. Run the bot:
```bash
uvicorn bot.main:app --reload
```

## Usage

1. Start a conversation with the bot on Telegram
2. Send a file or URL for analysis
3. The bot will respond with a detailed analysis result from VirusTotal
4. Ask the bot for tips and recommendations to avoid cyber threats

## Security Notes

- Never send personal or sensitive files
- All analysis is done in real-time without storage

## Technical Details

- Uses GitHub models through Azure Inference SDK
- Integrates with VirusTotal for file and URL scanning
- Supports multiple languages through gettext translations
- Implements proper resource cleanup and error handling
- Uses async/await for efficient operation

## Contributing

Feel free to submit issues and enhancement requests!
