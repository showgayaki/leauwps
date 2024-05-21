import requests
from logging import getLogger


logger = getLogger(__name__)


class LineNotify:
    """
    LINE通知用class
    https://notify-bot.line.me/ja/
        ログインして、[マイページ] - [トークンを発行する]
    payload = {
        'message': [メッセージ],
        'stickerPackageId': [STKPKGID],
        'stickerId': [STKID]
    }
    スタンプID: https://devdocs.line.me/files/sticker_list.pdf
    """
    def __init__(self, access_token: str) -> None:
        self.api_url = 'https://notify-api.line.me/api/notify'
        self.headers = {'Authorization': 'Bearer ' + access_token}

    def send_message(self, message: str):
        payload = {
            'message': message,
        }

        try:
            res = requests.post(self.api_url, headers=self.headers, data=payload)
            status_code = res.status_code
            logger.info(f'StatusCode: {status_code}')
        except Exception as e:
            logger.critical(e)
        finally:
            res.close()
