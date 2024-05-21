import time
import boto3
from logging import getLogger


logger = getLogger(__name__)


class SecurityGroup:
    def __init__(self,
                 aws_default_region: str,
                 security_group_id: str,
                 allow_port: int,
                 allow_cidr_ip: str,
                 allow_protocol: str) -> None:
        self.aws_default_region = aws_default_region
        self.security_group_id = security_group_id
        self.allow_port = allow_port
        self.allow_cidr_ip = allow_cidr_ip
        self.allow_protocol = allow_protocol

        self.rule = f'Port: {self.allow_port}, Protocol: {self.allow_protocol}, CidrIp: {self.allow_cidr_ip}'
        self.ec2 = boto3.client('ec2')

    def add_inbound_rule(self) -> bool:
        logger.info('Start to fetch inbound rules.')
        try:
            # インバウンドルール一覧を取得
            inbound_rules = self.ec2.describe_security_groups(
                GroupIds=[self.security_group_id]
            )

            # すでに当独されているか確認
            is_exists = False
            for permission in inbound_rules['SecurityGroups'][0]['IpPermissions']:
                if permission['FromPort'] == self.allow_port and\
                    permission['IpRanges'][0]['CidrIp'] == self.allow_cidr_ip and\
                        permission['IpProtocol'] == self.allow_protocol:
                    is_exists = True
                    break

            # 登録されていなければ、追加
            if is_exists:
                logger.info(f'[{self.rule}] rule is already exists.')
            else:
                logger.info(f'[{self.rule}] rule is NOT exists.')

                # インバウンドルール追加
                logger.info(f'Start to add [{self.rule}] rule.')
                add_response = self.ec2.authorize_security_group_ingress(
                    GroupId=self.security_group_id,
                    IpPermissions=[
                        {
                            'FromPort': self.allow_port,
                            'IpProtocol': self.allow_protocol,
                            'IpRanges': [
                                {
                                    'CidrIp': self.allow_cidr_ip,
                                },
                            ],
                            'ToPort': self.allow_port,
                        },
                    ],
                )

                if 'Return' in add_response and add_response['Return']:
                    logger.info(f'Success: Add [{self.rule}] rule.')
                else:
                    logger.error(f'FAILED: Add [{self.rule}] rule.')
                    return False

            return True

        except Exception as e:
            logger.critical(e)
            return False

    def delete_inbound_rule(self) -> None:
        logger.info(f'Start to delete [{self.rule}] rule.')
        try:
            self.ec2.revoke_security_group_ingress(
                CidrIp=self.allow_cidr_ip,
                FromPort=self.allow_port,
                GroupId=self.security_group_id,
                IpProtocol=self.allow_protocol,
                ToPort=self.allow_port,
            )
            logger.info(f'Success: Deleted [{self.rule}] rule.')
        except Exception as e:
            logger.error(f'FAILED: Delete [{self.rule}] rule.')
            logger.error(e)


class Ssm:
    def __init__(self, instance_id: str) -> None:
        self.instance_id = instance_id
        self.ssm = boto3.client('ssm')

    def run_command(self, command: str) -> tuple[str, str]:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/list_command_invocations.html

        return:
            {
                'status': 'Success'|'TimedOut'|'Cancelled'|'Failed'|'',
                'output': [command output],
            }
        """
        RETRY_COUNT = 5
        WAITING_SECONDS = 5
        logger.info(f'Start to run command[{command}].')

        for count in range(RETRY_COUNT):
            logger.info(f'Command try count: {count + 1}/{RETRY_COUNT}')
            try:
                send_command_result = self.ssm.send_command(
                    InstanceIds=[self.instance_id],
                    DocumentName="AWS-RunShellScript",
                    Parameters={'commands': [command]},
                    # OutputS3Region=self.AWS_DEFAULT_REGION,
                    # OutputS3BucketName='leauwps',
                    # OutputS3KeyPrefix='leauwps',
                    TimeoutSeconds=30,
                )
                break
            except Exception as e:
                logger.critical(e)

        command_id = send_command_result['Command']['CommandId']
        logger.info(f'Start to fetch command[id: {command_id}] result.')
        for _ in range(RETRY_COUNT * 2):
            try:
                response = self.ssm.list_command_invocations(
                    CommandId=command_id,
                    Details=True,
                )

                if response['CommandInvocations'] == []:
                    logger.info(f'Command results is not returned yet. Pause {WAITING_SECONDS} seconds...')
                    time.sleep(WAITING_SECONDS)
                    continue
                else:
                    status = response['CommandInvocations'][0]['Status']
                    output = response['CommandInvocations'][0]['CommandPlugins'][0]['Output']

                    if status == 'Pending' or status == 'InProgress':
                        continue
                    elif status == 'Success':
                        logger.info(f'{status}: Run [{command}]')
                    else:
                        logger.error(f'{status}: Run [{command}]')

                    return status, output
            except Exception as e:
                logger.critical(e)

        return '', ''
