# leauwps
EC2のセキュリティグループで80番ポートを開いて、Let’s Encryptの証明書を更新をして  
結果をLINEで通知します

## .env
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

AWS_DEFAULT_REGION=
SECURITY_GROUP_ID=

ALLOW_PORT=80
ALLOW_CIDR_IP=0.0.0.0/0
ALLOW_PROTOCOL=tcp

EC2_INSTANCE_ID=

LETS_ENCRYPT_DOMAIN=
LETS_ENCRYPT_MAIL=

LINE_NOTIFY_ACCESS_TOKEN=
```

## systemd
`chmod 755 run.sh`  
### service
`sudo vi /lib/systemd/system/leauwps.service`  
```
[Unit]
Description=leauwps

[Service]
Type=simple
User=[user name]
ExecStart=[path to]/leauwps/run.sh

[Install]
WantedBy=multi-user.target
```
### timer 
`sudo vi /lib/systemd/system/leauwps.timer`  
```
[Unit]
Description=leauwps-timer

[Timer]
OnCalendar=*-*-01 00:00:00

[Install]
WantedBy=timers.target
```