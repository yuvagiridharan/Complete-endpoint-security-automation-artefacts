#!/bin/bash
TARGET=$1
echo "[+] Killing suspicious process on: $TARGET"

if [ "$TARGET" = "172.16.120.132" ]; then
    ssh -o StrictHostKeyChecking=no \
        -o ConnectTimeout=10 \
        -i /root/.ssh/lab_key \
        attacker@$TARGET \
        "powershell -Command \"
        \$procs = Get-Process | Where-Object {
            \$_.Name -match 'powershell|cmd|nc|ncat|mimikatz'
        }
        foreach (\$p in \$procs) {
            Write-Host 'Killing:' \$p.Name \$p.Id
            Stop-Process -Id \$p.Id -Force -ErrorAction SilentlyContinue
        }
        Write-Host 'KILL_COMPLETE'
        \""
fi
