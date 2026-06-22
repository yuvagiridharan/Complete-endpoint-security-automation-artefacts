#!/bin/bash
TARGET=$1
echo "[+] Disabling account on: $TARGET"
ssh -i /root/.ssh/lab_key \
    -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 \
    labuser@$TARGET \
    "sudo passwd -l user01 && \
     echo DISABLE_COMPLETE"
