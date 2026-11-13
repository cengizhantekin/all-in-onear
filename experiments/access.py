"""Analyze real local NEAR Sandbox key permissions. Replay needs only Python."""
import base64
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import signal
import subprocess
import threading
from pathlib import Path
from .common import metric

ROOT = Path(__file__).resolve().parent.parent
SANDBOX_SLOT = threading.BoundedSemaphore(1)
CHECKS = (
    ('owner_control', 'Full key: blocked method', 'Success: blocked', 'blocked'),
    ('allowed_call', 'Limited key: allowed method', 'Success: allowed', 'allowed'),
    ('denied_method', 'Limited key: other method', 'MethodNameMismatch', 'allowed'),
    ('denied_receiver', 'Limited key: other contract', 'ReceiverMismatch', 'allowed'),
    ('denied_deposit', 'Limited key: attached deposit', 'DepositWithFunctionCall', 'allowed'),
    ('denied_transfer', 'Limited key: transfer action', 'RequiresFullAccess', 'allowed'),
    ('revoked_call', 'Removed key: allowed method', 'AccessKeyNotFound', 'allowed'),
    ('owner_after_revoke', 'Full key: after revocation', 'Success: allowed', 'allowed'),
)


def availability():
    if platform.system() not in ('Linux', 'Darwin'):
        return False, 'Fresh sandbox requires Linux/WSL or macOS ARM64. Use the setup instructions to capture a result; Python replay needs no Node.js.'
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if hard != resource.RLIM_INFINITY and hard < 65535:
        return False, f'Official Sandbox requires a file limit of at least 65535; this environment has a fixed hard limit of {hard}. No runtime result is substituted.'
    if not shutil.which('node') or not (ROOT / 'sandbox/node_modules/near-sandbox/package.json').exists():
        return False, 'Fresh sandbox needs Node.js >=22.22.2 and npm ci --ignore-scripts in the sandbox folder.'
    return True, 'Fresh local runtime is available. A new run creates temporary keys and uses only local test balances.'


def collect():
    return collect_script("access-keys.mjs")


def collect_script(script):
    if not SANDBOX_SLOT.acquire(blocking=False):
        raise RuntimeError('A local sandbox experiment is already running; retry when it finishes.')
    try:
        return _collect(script)
    finally:
        SANDBOX_SLOT.release()


def _collect(script):
    available, reason = availability()
    if not available:
        raise RuntimeError(reason)
    node = shutil.which('node')
    if not node or not (ROOT / 'sandbox/node_modules/near-sandbox/package.json').exists():
        raise RuntimeError('Sandbox dependencies missing. In Linux/WSL with Node >=22.22.2: cd sandbox && npm ci --ignore-scripts. Or choose Recorded sandbox.')
    spec = importlib.util.spec_from_file_location('onear_sandbox_download', ROOT / 'sandbox/download_binary.py')
    downloader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(downloader)
    downloader.ensure_binary()
    environment = os.environ.copy()
    # This subprocess needs no user credentials; never pass AI credentials to it.
    for name in ('NEAR_AI_API_KEY', 'NEAR_AI_MODEL'):
        environment.pop(name, None)
    process = subprocess.Popen([node, str(ROOT / 'sandbox' / script)], cwd=ROOT / 'sandbox',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
        env=environment, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=270)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise RuntimeError('Sandbox timed out; no recorded success was substituted.') from None
    if process.returncode != 0:
        # Avoid exposing dependency objects, process environment or temporary test keys.
        raise RuntimeError(f'The local sandbox did not complete. Run node sandbox/{script} for its diagnostic, or select Recorded sandbox.')
    if len(stdout) > 4_000_000:
        raise ValueError('Sandbox output exceeds the evidence limit')
    evidence = json.loads(stdout)
    if evidence.get('environment') != 'near-sandbox':
        raise ValueError('Unexpected sandbox output')
    return evidence


def response(record):
    return record['response']


def enum_names(value):
    """Rust RPC enums may be object keys or string-valued unit variants."""
    names = set()
    if isinstance(value, dict):
        for key, item in value.items():
            names.add(key)
            names.update(enum_names(item))
    elif isinstance(value, list):
        for item in value:
            names.update(enum_names(item))
    elif isinstance(value, str):
        names.add(value)
    return names


def outcome(record):
    raw = response(record)
    if 'error' in raw:
        labels = enum_names(raw['error'])
        for name in ('MethodNameMismatch', 'ReceiverMismatch', 'DepositWithFunctionCall',
                     'RequiresFullAccess', 'AccessKeyNotFound'):
            if name in labels:
                return name
        return 'Other RPC error'
    status = raw.get('result', {}).get('status', {})
    if 'SuccessValue' in status:
        try:
            value = json.loads(base64.b64decode(status['SuccessValue'], validate=True))
        except (ValueError, TypeError):
            return 'Other execution result'
        return 'Success: ' + str(value)
    return 'Execution failure'


def view_value(record):
    raw = response(record)
    if 'error' in raw:
        raise ValueError('State view failed; cannot establish the post-call state')
    return json.loads(bytes(raw['result']['result']).decode())


def analyze(evidence):
    if evidence.get('schema') != 1 or evidence.get('environment') != 'near-sandbox':
        raise ValueError('Expected real NEAR Sandbox evidence schema')
    runtime = response(evidence['runtime'])['result']
    if runtime.get('chain_id') != 'onear-access-keys-sandbox' or evidence.get('configured_version') != '2.14.0':
        raise ValueError('Unexpected sandbox chain/version')
    if runtime.get('version', {}).get('version') != '2.14.0':
        raise ValueError('Running node does not match the pinned sandbox version')
    contract = evidence['contract']
    wasm = base64.b64decode(contract['wasm_base64'], validate=True)
    if hashlib.sha256(wasm).hexdigest() != contract['wasm_sha256']:
        raise ValueError('Contract bytecode checksum mismatch')
    before = response(evidence['key_before'])['result']['permission']['FunctionCall']
    if (before.get('receiver_id') != evidence['target_account'] or before.get('method_names') != ['allowed']
            or before.get('allowance') != str(10**23)):
        raise ValueError('Grant does not match the declared limited permission')
    after = response(evidence['key_after_call'])['result']['permission']['FunctionCall']
    if not 0 < int(after['allowance']) < int(before['allowance']):
        raise ValueError('Successful limited call did not demonstrate consumption of its gas allowance')
    revoked_response = response(evidence['key_after_revoke'])
    structured_missing = 'UNKNOWN_ACCESS_KEY' in enum_names(revoked_response.get('error'))
    # This node also returns the older query-error envelope inside result.
    legacy_result = revoked_response.get('result', {})
    legacy_missing = (legacy_result.get('error') ==
                      f"access key {evidence['limited_public_key']} does not exist while viewing"
                      and 'permission' not in legacy_result and 'nonce' not in legacy_result
                      and isinstance(legacy_result.get('block_height'), int))
    if not (structured_missing or legacy_missing):
        raise ValueError('Revoked key is still visible or the key query failed unexpectedly')
    if response(evidence['owner_key_after'])['result']['permission'] != 'FullAccess':
        raise ValueError('Owner full-access key missing after revocation')
    if view_value(evidence['initial_state']) != 'none' or view_value(evidence['initial_other_state']) != 'none':
        raise ValueError('Probe contracts were not initially empty')
    checks = evidence['checks']
    if [item.get('id') for item in checks] != [item[0] for item in CHECKS]:
        raise ValueError('Incomplete or reordered permission checks')
    rows = []
    matched = 0
    for item, (key, title, expected, expected_state) in zip(checks, CHECKS):
        if item['observation']['request']['method'] != 'broadcast_tx_commit':
            raise ValueError('The probe was not submitted to the local node')
        expected_signer = evidence['owner_public_key'] if key in ('owner_control', 'owner_after_revoke') else evidence['limited_public_key']
        expected_receiver = evidence['other_account'] if key in ('denied_receiver', 'denied_transfer') else evidence['target_account']
        if (item['signer_public_key'] != expected_signer or item['receiver_id'] != expected_receiver
                or item['observation']['request']['params'] != [item['signed_transaction_base64']]):
            raise ValueError('Probe signer, receiver or submitted bytes do not match the declared case')
        observed = outcome(item['observation'])
        state = view_value(item['state_after'])
        other_state = view_value(item['other_state_after'])
        passed = observed == expected and state == expected_state and other_state == 'none'
        matched += passed
        rows.append({'Case': title, 'Expected': expected, 'Observed': observed,
                     'Target state': state, 'Other contract state': other_state,
                     'Check': 'Matched' if passed else 'Mismatch'})
    return {
        'headline': 'A key with limits, and an owner in control.',
        'summary': f'{matched} of {len(CHECKS)} expected outcomes matched in a real local NEAR Sandbox {runtime["version"]["version"]} node. '
                   'The rows distinguish actual node responses and post-call state from the expected policy.',
        'metrics': [metric('Checks', len(CHECKS)), metric('Expected outcomes matched', matched),
                    metric('Planned negative cases', 5), metric('Node protocol', runtime['protocol_version'])],
        'rows': rows,
        'supports': ('This local runtime enforced the selected method, receiver, deposit and action restrictions, and rejected the removed key.'
                     if matched == len(CHECKS) else 'Some observed outcomes differ from the expected permission policy; inspect every row before using this capture.'),
        'investment_link': 'Protocol-level, revocable permissions give applications a concrete building block for delegating bounded actions to agents while retaining an owner key. This experiment tests that building block, not adoption or token demand.',
        'limits': 'Local sandbox with temporary accounts and a minimal probe contract; not mainnet and not an LLM-controlled agent. '
                  'It tests these explicit cases only, not every permission interaction or protection from contract bugs. '
                  'Allowance is a gas budget, not a general limit on assets a called contract may control. Public view calls remain public. '
                  'Transactions use only local test balances; no production wallet or real funds were used.',
        'environment': 'near-sandbox', 'matched': matched, 'total': len(CHECKS),
    }
