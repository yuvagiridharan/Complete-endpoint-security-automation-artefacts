#!/bin/bash
TARGET=$1
echo "[+] Restoring cron on: $TARGET"
ssh -i /root/.ssh/lab_key -o StrictHostKeyChecking=no -o ConnectTimeout=10 labuser@$TARGET "sudo crontab /tmp/cron_backup.txt 2>/dev/null && echo RESTORE_COMPLETE"
