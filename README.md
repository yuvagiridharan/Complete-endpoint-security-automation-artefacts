# B9CY110 Endpoint Security Lab
## Automated Incident Response and Remediation

**Student:** Yuvagiridharan U | **Module:** B9CY110
**Programme:** MSc Cybersecurity | **Institution:** Dublin Business School

---

## Lab Environment

| VM | OS | IP | Role |
|---|---|---|---|
| wazuh-server | Ubuntu 22.04 ARM64 | 172.16.120.131 | SIEM + Docker AI stack |
| linux-endpoint | Ubuntu 22.04 ARM64 | 172.16.120.134 | Attack target |
| windows-endpoint | Windows 11 ARM64 | 172.16.120.132 | Attack target |

---

## Quick Start

```bash
cd remediation-stack
docker-compose up -d
curl http://localhost:5001/health
curl http://localhost:5003/health
curl http://localhost:5002/health
```

---

## Detection Rules

| Rule | Level | Platform | MITRE | Description |
|---|---|---|---|---|
| 2502 | 10 | Linux | T1110 | SSH brute force |
| 100003 | 9 | Linux | T1548 | Shadow file accessed |
| 100004 | 10 | Linux | T1053 | Crontab modified |
| 100001 | 12 | Windows | T1059 | Encoded PowerShell |
| 100009 | 12 | Windows | T1059 | Suspicious PowerShell |
| 100010 | 10 | Windows | T1059 | CMD by attacker |

---

## Automated Remediation Actions

| Script | Trigger | Platform |
|---|---|---|
| disable_account.sh | Brute force | Linux |
| enable_account.sh | SOC recovery | Linux |
| isolate_host.sh | Brute force | Linux |
| unisolate_host.sh | SOC recovery | Linux |
| kill_process.sh | Suspicious process | Windows |
| kill_session.sh | Crontab persistence | Linux |
| remove_cron.sh | Crontab persistence | Linux |
| restore_cron.sh | SOC recovery | Linux |

---

## References

- MITRE ATT&CK: https://attack.mitre.org
- Wazuh Documentation: https://documentation.wazuh.com
- NIST SP 800-61: https://nvlpubs.nist.gov
