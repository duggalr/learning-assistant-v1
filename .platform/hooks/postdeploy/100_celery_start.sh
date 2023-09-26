#!/usr/bin/env bash

# Create the celery systemd service file
echo "[Unit]
Name=Celery
Description=GPT Learning Assistant Celery Worker
After=network.target
StartLimitInterval=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=/var/app/current
ExecStart=$PYTHONPATH/celery -A gpt_learning_assistant worker -l info --logfile=celery.worker.log
EnvironmentFile=/opt/elasticbeanstalk/deployment/env

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/celery.service

# Start celery service
systemctl start celery.service

# Enable celery service to load on system start
systemctl enable celery.service
