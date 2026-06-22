#!/bin/bash
TARGET=$1
echo "[+] Unisolating host: $TARGET"

iptables -D FORWARD -s $TARGET -j DROP 2>/dev/null
iptables -D FORWARD -d $TARGET -j DROP 2>/dev/null
iptables -D INPUT -s $TARGET -j DROP 2>/dev/null
iptables -D OUTPUT -d $TARGET -j DROP 2>/dev/null

echo "UNISOLATE_COMPLETE: $TARGET unblocked"
