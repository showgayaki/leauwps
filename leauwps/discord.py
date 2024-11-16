from pathlib import Path
import requests
from logging import getLogger


logger = getLogger(__name__)


class Discord:
    def __init__(self, url: str) -> None:
        self.webhuook_url = url
        logger.info(f'Discord Webhook URL: {self.webhuook_url}.')

    def post(self, content: str, files: list[Path] = []) -> None:
        # https://discord.com/developers/docs/resources/webhook
        data = {
            'content': content,
        }

        multiple_files = []
        if len(files):
            logger.info(f'Post files: {files}.')
            for file in files:
                file_name = file.name
                with open(str(file), 'rb') as f:
                    file_binary = f.read()
                multiple_files.append(
                    (file_name, (file_name, file_binary))
                )

        try:
            logger.info('Start to post Discord.')
            response = requests.post(self.webhuook_url, data=data, files=multiple_files)
            logger.info(f'Status Code: {response.status_code}')
        except Exception as e:
            logger.critical(e)
