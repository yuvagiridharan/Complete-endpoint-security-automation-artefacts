from flask import Flask, request, jsonify
import subprocess
import json
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_ACTIONS = os.environ.get(
    'ALLOWED_ACTIONS',
    'isolate_host,disable_account,kill_process,remove_cron'
).split(',')

ALLOWED_TARGETS = os.environ.get(
    'ALLOWED_TARGETS', ''
).split(',')

AUDIT_LOG = '/audit_log/remediation_audit.jsonl'

def write_audit(entry):
    entry['timestamp'] = datetime.utcnow().isoformat()
    os.makedirs('/audit_log', exist_ok=True)
    with open(AUDIT_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    logger.info(f"AUDIT: {json.dumps(entry)}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'allowed_actions': ALLOWED_ACTIONS,
        'allowed_targets': ALLOWED_TARGETS
    })

@app.route('/rollback', methods=['POST'])
def rollback():
    req = request.json
    action = req.get('original_action', '')
    target = req.get('target', '')

    rollback_map = {
        'isolate_host': 'unisolate_host',
        'disable_account': 'enable_account',
        'remove_cron': 'restore_cron'
    }

    rollback_script = rollback_map.get(action)
    if not rollback_script:
        return jsonify({
            'status': 'no_rollback_available',
            'action': action
        })

    script_path = f"/app/actions/{rollback_script}.sh"
    if not os.path.exists(script_path):
        return jsonify({
            'status': 'rollback_script_missing'
        })

    result = subprocess.run(
        ['bash', script_path, target],
        capture_output=True,
        text=True,
        timeout=30
    )

    write_audit({
        'event': 'ROLLBACK',
        'original_action': action,
        'rollback_action': rollback_script,
        'target': target,
        'success': result.returncode == 0,
        'output': result.stdout
    })

    return jsonify({
        'status': 'success',
        'rollback_action': rollback_script,
        'output': result.stdout
    })

@app.route('/execute', methods=['POST'])
def execute():
    req = request.json
    action = req.get('action', '')
    target = req.get('target', '')
    alert_id = req.get('alert_id', 'unknown')
    justification = req.get('justification', '')

    # Check 1: Action allowlist
    if action not in ALLOWED_ACTIONS:
        write_audit({
            'event': 'DENIED',
            'reason': 'action_not_allowed',
            'action': action,
            'target': target,
            'alert_id': alert_id
        })
        return jsonify({
            'status': 'denied',
            'reason': f'action [{action}] not in allowlist'
        }), 403

    # Check 2: Target allowlist
    if ALLOWED_TARGETS[0] and target not in ALLOWED_TARGETS:
        write_audit({
            'event': 'DENIED',
            'reason': 'target_not_allowed',
            'action': action,
            'target': target,
            'alert_id': alert_id
        })
        return jsonify({
            'status': 'denied',
            'reason': f'target [{target}] not in allowlist'
        }), 403

    script_path = f"/app/actions/{action}.sh"

    try:
        result = subprocess.run(
            ['bash', script_path, target],
            capture_output=True,
            text=True,
            timeout=30
        )
        success = result.returncode == 0
        verified = 'COMPLETE' in result.stdout or \
                   'SUCCESS' in result.stdout

        write_audit({
            'event': 'EXECUTED',
            'action': action,
            'target': target,
            'alert_id': alert_id,
            'justification': justification,
            'success': success,
            'verified': verified,
            'stdout': result.stdout,
            'stderr': result.stderr
        })

        return jsonify({
            'status': 'success' if success else 'failed',
            'action': action,
            'target': target,
            'verified': verified,
            'output': result.stdout,
            'rollback_available': action in [
                'isolate_host',
                'disable_account',
                'remove_cron'
            ]
        })

    except subprocess.TimeoutExpired:
        write_audit({
            'event': 'TIMEOUT',
            'action': action,
            'target': target,
            'alert_id': alert_id
        })
        return jsonify({'status': 'timeout'}), 500

    except Exception as e:
        write_audit({
            'event': 'ERROR',
            'action': action,
            'target': target,
            'error': str(e)
        })
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
