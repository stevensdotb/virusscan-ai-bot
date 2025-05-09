# Virus Scan AI Bot

A Telegram bot that uses AI to analyze files and URLs for potential malware threats.

## Features

- File and URL analysis using GitHub models
- Support for files up to 5MB
- Easy-to-use interface
- Multi-language support (English and Spanish)
- Real-time analysis with VirusTotal integration
- Secure file handling without storage

## Requirements

- Python 3.12+
- Azure Inference SDK
- Telegram Bot Token
- GitHub Models API Key
- VirusTotal API Key

## Installation

1. Clone the repository:
```bash
git clone [URL_DEL_REPOSITORIO]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your API keys:
  - `TELEGRAM_BOT_TOKEN`
  - `OPENAI_API_KEY`
  - `VT_API_KEY`

4. Run the bot:
```bash
python -m bot.main
```

## Usage

1. Start a conversation with the bot on Telegram
2. Send a file or URL for analysis
3. The bot will respond with a detailed analysis using GitHub models

## Security Notes

- Never send personal or sensitive files
- The bot can only analyze files up to 5MB
- Files are analyzed in memory and not stored
- All analysis is done in real-time without storage
- The bot uses secure API endpoints for all operations

## Technical Details

- Uses GitHub models through Azure Inference SDK
- Integrates with VirusTotal for file and URL scanning
- Supports multiple languages through gettext translations
- Implements proper resource cleanup and error handling
- Uses async/await for efficient operation

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
