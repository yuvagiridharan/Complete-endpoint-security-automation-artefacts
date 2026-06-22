#!/bin/bash
TARGET=$1
echo "[+] Killing user sessions on: $TARGET"
ssh -i /root/.ssh/lab_key \
    -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 \
    labuser@$TARGET \
    "sudo pkill -u user01 && \
     sudo who | grep user01 | \
     awk '{print \$2}' | \
     xargs -I{} sudo pkill -t {} 2>/dev/null; \
     echo SESSION_KILLED"
