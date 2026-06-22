# MITRE ATT&CK Mapping

## Linux Detections

| Attack | Technique | Rule | Remediation |
|---|---|---|---|
| SSH Brute Force | T1110 | 2502 | disable_account + isolate_host |
| Privilege Escalation | T1548.003 | 100003 | logged |
| Crontab Persistence | T1053.003 | 100004 | kill_session + remove_cron |
| SSH Lateral Movement | T1021 | 100005 | logged |

## Windows Detections

| Attack | Technique | Rule | Remediation |
|---|---|---|---|
| Encoded PowerShell | T1059.001 | 100001 | isolate_host |
| Suspicious PowerShell | T1059.001 | 100009 | kill_process |
| CMD Execution | T1059.003 | 100010 | kill_process |
