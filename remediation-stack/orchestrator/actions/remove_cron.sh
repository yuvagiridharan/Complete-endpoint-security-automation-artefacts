#!/bin/bash
TARGET=$1
echo "[+] Removing cron on: $TARGET"
ssh -i /root/.ssh/lab_key -o StrictHostKeyChecking=no -o ConnectTimeout=10 labuser@$TARGET "sudo crontab -l > /tmp/cron_backup.txt 2>/dev/null; sudo crontab -r 2>/dev/null; echo CRON_REMOVE_COMPLETE"
