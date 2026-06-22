from flask import Flask, request, jsonify
import requests
import json
import os
import re
import logging
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://172.18.0.1:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2:1b')

last_action = {}
COOLDOWN_SECONDS = 300

RULE_ACTION_MAP = {
    '2502':   ('HIGH', 'disable_account'),
    '5551':   ('HIGH', 'disable_account'),
    '40112':  ('HIGH', 'disable_account'),
    '100004': ('HIGH', 'kill_session'),
    '100012': ('HIGH', 'kill_session'),
    '2833':   ('HIGH', 'kill_session'),
}

def clean_json(raw):
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)
    raw = raw.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return match.group(0)
    return raw

def query_ollama(prompt):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200}
            },
            timeout=60
        )
        raw = response.json().get('response', '{}')
        return clean_json(raw)
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return '{}'

def is_cooldown(target, action):
    key = f"{target}:{action}"
    now = time.time()
    if key in last_action:
        elapsed = now - last_action[key]
        if elapsed < COOLDOWN_SECONDS:
            logger.info(f"COOLDOWN: {key} ({int(elapsed)}s)")
            return True
    last_action[key] = now
    return False

@app.route('/health', methods=['GET'])
def health():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except:
        ollama_ok = False
    return {"status": "healthy", "ollama_connected": ollama_ok}

@app.route('/classify', methods=['POST'])
def classify():
    alert = request.json
    description = alert.get('rule', {}).get('description', '')
    level = int(alert.get('rule', {}).get('level', 0))
    rule_id = str(alert.get('rule', {}).get('id', ''))
    agent_ip = alert.get('agent', {}).get('ip', 'unknown')
    agent_name = alert.get('agent', {}).get('name', 'unknown')

    pre_severity = 'LOW'
    pre_action = 'none'

    if rule_id in RULE_ACTION_MAP:
        pre_severity, pre_action = RULE_ACTION_MAP[rule_id]

    logger.info(f"Rule:{rule_id} Level:{level} Pre:{pre_severity}/{pre_action}")

    if pre_action != 'none' and is_cooldown(agent_ip, pre_action):
        return {"severity": pre_severity, "summary": description,
                "action": "none", "rationale": "Cooldown active"}

    prompt = f"""Security alert:
Rule:{rule_id} Level:{level}
Description:{description}
Respond ONLY JSON:
{{"severity":"{pre_severity}","action":"{pre_action}","rationale":"reason"}}"""

    raw = query_ollama(prompt)

    try:
        result = json.loads(raw)
        if rule_id in RULE_ACTION_MAP:
            result['severity'] = pre_severity
            result['action'] = pre_action
        return result
    except:
        return {"severity": pre_severity, "action": pre_action,
                "rationale": f"Rule-based level {level}"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
