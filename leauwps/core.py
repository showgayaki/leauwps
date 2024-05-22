import json
from pathlib import Path
from logging import config, getLogger

from env import Env
from aws import SecurityGroup, Ssm
from line import LineNotify


# log設定の読み込み
current_dir = Path(__file__).parent.resolve()
log_config = Path.joinpath(current_dir, 'log', 'config.json')
with open(log_config) as f:
    config.dictConfig(json.load(f))

logger = getLogger(__name__)
env = Env()


def check_valid_days(ssm: Ssm) -> int:
    logger.info('Check valid days.')

    command = 'certbot certificates'
    valid_days = -1

    status, output = ssm.run_command(command)
    if status:
        for line in output.split('\n'):
            line = line.strip()
            # Expiry Date: 2024-**-** **:**:**+00:00 (VALID: ** days)
            if 'Expiry Date: ' in line:
                valid_days = int(line.split(' ')[5])
                logger.info(f'Valid [{valid_days}] days.')
                break

    return valid_days


def commands() -> list:
    return [
        f'certbot certonly --standalone -d {env.LETS_ENCRYPT_DOMAIN} -m {env.LETS_ENCRYPT_MAIL} --agree-tos -n',
        'certbot certificates',
        'systemctl restart postfix',
        'systemctl status postfix',
        'systemctl restart dovecot',
        'systemctl status dovecot',
    ]


def parse_output(command: str, output: str) -> str:
    for line in output.split('\n'):
        # 前後のスペースや改行などを削除
        line = line.strip()

        # 各コマンドごとの処理
        if 'certbot certonly --standalone' in command:
            if 'Successfully received certificate.' in line:
                return 'Let\'s Enctryptの更新に成功しました\n'
        elif 'certbot certificates' in command:
            # line: Expiry Date: 2024-**-** **:**:**+00:00 (VALID: ** days)
            if 'Expiry Date: ' in line:
                line_splited = line.split(' ')
                return f'次の期限は\n{line_splited[2]} {line_splited[3]}です\n'
        elif 'systemctl status postfix' in command:
            # line: Active: active (running)
            if 'Active:' in line:
                return f'\nPostfix Status\n{" ".join(line.split(" ")[:3])}\n'
        elif 'systemctl status dovecot' in command:
            if 'Active:' in line:
                return f'\nDovecot Status\n{" ".join(line.split(" ")[:3])}'


def main() -> None:
    ssm = Ssm(env.EC2_INSTANCE_ID)

    # 更新できるのは、30日以内に期限切れになる証明書のみ
    THRESHOLD_DAYS_UPDATE_CERTIFICATE = 30
    valid_days = check_valid_days(ssm)
    if 0 < valid_days < THRESHOLD_DAYS_UPDATE_CERTIFICATE:
        pass
    else:
        logger.info('Certificate not yet due for renewal.')
        return

    security_group = SecurityGroup(
        env.AWS_DEFAULT_REGION,
        env.SECURITY_GROUP_ID,
        env.ALLOW_PORT,
        env.ALLOW_CIDR_IP,
        env.ALLOW_PROTOCOL,
    )
    # インバウンドルール作成
    add_result = security_group.add_inbound_rule()

    if add_result:
        message = '\n'
        line = LineNotify(env.LINE_NOTIFY_ACCESS_TOKEN)
        ssm = Ssm(env.EC2_INSTANCE_ID)

        for command in commands():
            status, output = ssm.run_command(command)
            if status:
                if output:
                    message += parse_output(command, output)
            else:
                # statusが空のときは、コマンドの結果取得ができていない
                message += f'コマンド：\n{command}\nの実行結果を取得できませんでした'
        # メッセージ送信
        line.send_message(message)
    else:
        return

    # インバウンドルール削除
    security_group.delete_inbound_rule()


if __name__ == '__main__':
    logger.info('===== Leauwps started =====')
    main()
    logger.info('===== Leauwps end =====')
