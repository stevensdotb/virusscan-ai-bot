import os

from telegram import Message, File

class FileHandler:
    @staticmethod
    async def get_file(file_msg: Message) -> tuple[File, str] | None:
        """Get file from message."""
        if file_msg.photo:
            return await file_msg.photo[-1].get_file(), "Image"
        elif file_msg.video:
            return await file_msg.video.get_file(), "Video"
        elif file_msg.audio:
            return await file_msg.audio.get_file(), "Audio"
        elif file_msg.document:
            mime_type = file_msg.document.mime_type

            # Ignore gifs sent from telegram chat
            if mime_type == 'video/mp4':
                return None

            file_type = "Document" if mime_type != "image/gif" else "Animation/GIF"
            return await file_msg.document.get_file(), file_type
        else:
            return None

    @staticmethod
    async def save_file(file: File, file_path: str):
        """Save file to disk."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await file.download_to_drive(file_path)

    @staticmethod
    async def analyze_file(file_path: str, vt_client) -> dict[str, any]:
        """Analyze file using VirusTotal."""
        return await vt_client.analyze_file(file_path)

    @staticmethod
    async def analyze_url(url: str, vt_client) -> dict[str, any]:
        """Analyze URL using VirusTotal."""
        return await vt_client.analyze_url(url)
