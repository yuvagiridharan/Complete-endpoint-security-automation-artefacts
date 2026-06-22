#!/bin/bash
TARGET=$1
echo "[+] Re-enabling account on: $TARGET"
ssh -i /root/.ssh/lab_key \
    -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 \
    labuser@$TARGET << 'SSHEOF'
sudo usermod -U user01
sudo usermod --expiredate '' user01
sudo chage -I -1 -m 0 -M 99999 -E -1 user01
sudo faillock --user user01 --reset 2>/dev/null
echo 'user01:User123' | sudo chpasswd
sudo passwd -S user01
echo ENABLE_COMPLETE
SSHEOF
