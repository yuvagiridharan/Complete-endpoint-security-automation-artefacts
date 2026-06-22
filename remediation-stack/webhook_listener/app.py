from flask import Flask, request, jsonify
import requests
import json
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AI_TRIAGE_URL = os.environ.get('AI_TRIAGE_URL', 'http://ai_triage:5003')
ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'http://orchestrator:5002')

def log(msg):
    timestamp = datetime.utcnow().isoformat()
    print(f"{timestamp} {msg}", flush=True)

def call_orchestrator(action, target, alert_id, justification):
    try:
        r = requests.post(
            f"{ORCHESTRATOR_URL}/execute",
            json={
                "action": action,
                "target": target,
                "alert_id": alert_id,
                "justification": justification
            },
            timeout=30
        )
        return r.json()
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        return {"status": "failed", "error": str(e)}

@app.route('/health', methods=['GET'])
def health():
    return {"status": "healthy",
            "timestamp": datetime.utcnow().isoformat()}

@app.route('/wazuh-alert', methods=['POST'])
def wazuh_alert():
    alert = request.json
    rule_id = str(alert.get('rule', {}).get('id', ''))
    level = int(alert.get('rule', {}).get('level', 0))
    alert_id = alert.get('id', 'unknown')
    agent_ip = alert.get('agent', {}).get('ip', 'unknown')
    agent_name = alert.get('agent', {}).get('name', 'unknown')
    description = alert.get('rule', {}).get('description', '')

    log(f"ALERT RECEIVED rule={rule_id} level={level} agent={agent_name}")

    log("CALLING AI TRIAGE")
    try:
        triage_r = requests.post(
            f"{AI_TRIAGE_URL}/classify",
            json=alert,
            timeout=60
        )
        triage = triage_r.json()
    except Exception as e:
        log(f"AI TRIAGE ERROR: {e}")
        return {"error": str(e)}, 500

    severity = triage.get('severity', 'LOW')
    action = triage.get('action', 'none')

    log(f"AI RESULT: severity={severity} action={action}")

    if severity != 'HIGH':
        log(f"SKIPPED: severity={severity}")
        return {"alert_id": alert_id, "triage": triage}

    if agent_ip == 'unknown':
        return {"alert_id": alert_id, "triage": triage}

    # BRUTE FORCE: disable + isolate
    if rule_id in ['2502', '5551', '40112']:
        log(f"BRUTE FORCE: disable + isolate on {agent_ip}")

        result1 = call_orchestrator(
            "disable_account", agent_ip,
            alert_id, "Brute force detected"
        )
        v1 = result1.get('verified', False)
        log(f"DISABLE_ACCOUNT: {'success' if v1 else 'failed'} verified={v1}")

        result2 = call_orchestrator(
            "isolate_host", agent_ip,
            alert_id, "Brute force isolation"
        )
        v2 = result2.get('verified', False)
        log(f"ISOLATE_HOST: {'success' if v2 else 'failed'} verified={v2}")

        if v1 and v2:
            log(f"BOTH REMEDIATIONS: success ✅")
        else:
            log(f"PARTIAL: disable={v1} isolate={v2}")

    # CRONTAB: kill session + disable account
    elif rule_id in ['100004', '100012', '2833']:
        log(f"CRONTAB DETECTED: kill session + disable on {agent_ip}")

        result1 = call_orchestrator(
            "kill_session", agent_ip,
            alert_id, "Crontab persistence detected"
        )
        v1 = result1.get('verified', False)
        log(f"KILL_SESSION: {'success' if v1 else 'failed'} verified={v1}")

        result2 = call_orchestrator(
            "disable_account", agent_ip,
            alert_id, "Crontab account lock"
        )
        v2 = result2.get('verified', False)
        log(f"DISABLE_ACCOUNT: {'success' if v2 else 'failed'} verified={v2}")

        if v1 and v2:
            log(f"CRONTAB REMEDIATION: success ✅")
        else:
            log(f"PARTIAL: session={v1} disable={v2}")

    # OTHER HIGH alerts
    else:
        log(f"TRIGGERING: {action} on {agent_ip}")
        result = call_orchestrator(
            action, agent_ip,
            alert_id, "High severity alert"
        )
        v = result.get('verified', False)
        log(f"REMEDIATION: {'success' if v else 'failed'} verified={v}")

    return {"alert_id": alert_id, "triage": triage}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
