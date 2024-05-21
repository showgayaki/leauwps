# leauwps
EC2のセキュリティグループで80番ポートを開いて、Let’s Encryptの証明書更新をします

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