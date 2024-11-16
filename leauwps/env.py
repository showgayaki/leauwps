import os
from dotenv import load_dotenv


class Env:
    def __init__(self) -> None:
        load_dotenv()

        self.AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
        self.SECURITY_GROUP_ID = os.getenv('SECURITY_GROUP_ID')
        self.ALLOW_PORT = int(os.getenv('ALLOW_PORT'))
        self.ALLOW_CIDR_IP = os.getenv('ALLOW_CIDR_IP')
        self.ALLOW_PROTOCOL = os.getenv('ALLOW_PROTOCOL')
        self.EC2_INSTANCE_ID = os.getenv('EC2_INSTANCE_ID')
        self.LETS_ENCRYPT_DOMAIN = os.getenv('LETS_ENCRYPT_DOMAIN')
        self.LETS_ENCRYPT_MAIL = os.getenv('LETS_ENCRYPT_MAIL')
        self.LINE_NOTIFY_ACCESS_TOKEN = os.getenv('LINE_NOTIFY_ACCESS_TOKEN')
        self.DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
