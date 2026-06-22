#!/bin/bash
TARGET=$1
echo "[+] Isolating host: $TARGET"

# Block on wazuh-server FORWARD chain only
iptables -I FORWARD -s $TARGET -j DROP 2>/dev/null
iptables -I FORWARD -d $TARGET -j DROP 2>/dev/null

# Also block INPUT/OUTPUT on wazuh-server
iptables -I INPUT -s $TARGET -j DROP 2>/dev/null
iptables -I OUTPUT -d $TARGET -j DROP 2>/dev/null

echo "ISOLATION_COMPLETE: $TARGET blocked"
