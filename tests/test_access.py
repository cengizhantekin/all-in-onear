"""Synthetic parser/boundary tests. No fixture here is a captured NEAR runtime result."""
import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import runner
from experiments import access


def raw(result=None, error=None):
    return {'response': {'result': result} if error is None else {'error': error}}


def state(value):
    return raw({'result': list(json.dumps(value).encode())})


def fixture():
    permission = {'receiver_id': 'probe.owner', 'method_names': ['allowed'], 'allowance': str(10**23)}
    wasm = b'\x00asm\x01\x00\x00\x00'
    evidence = {'schema': 1, 'environment': 'near-sandbox', 'configured_version': '2.14.0',
        'runtime': raw({'chain_id': 'onear-access-keys-sandbox', 'version': {'version': '2.14.0'}, 'protocol_version': 0}),
        'target_account': 'probe.owner', 'other_account': 'other.owner',
        'owner_public_key': 'SYNTHETIC_OWNER', 'limited_public_key': 'SYNTHETIC_LIMITED',
        'contract': {'wasm_base64': base64.b64encode(wasm).decode(), 'wasm_sha256': hashlib.sha256(wasm).hexdigest()},
        'key_before': raw({'permission': {'FunctionCall': permission}}),
        'key_after_call': raw({'permission': {'FunctionCall': {**permission, 'allowance': str(10**23-1)}}}),
        'key_after_revoke': raw(error={'cause': {'name': 'UNKNOWN_ACCESS_KEY'}}),
        'owner_key_after': raw({'permission': 'FullAccess'}),
        'initial_state': state('none'), 'initial_other_state': state('none'), 'checks': []}
    for key,title,expected,value in access.CHECKS:
        if expected.startswith('Success: '):
            observation = raw({'status': {'SuccessValue': base64.b64encode(json.dumps(expected[9:]).encode()).decode()}})
        else:
            observation = raw(error={'data': {'TxExecutionError': {'InvalidTxError': {'InvalidAccessKeyError': {expected: {}}}}}})
        observation['request']={'method':'broadcast_tx_commit','params':['SYNTHETIC_SIGNED_BYTES']}
        evidence['checks'].append({'id':key,'observation':observation,'state_after':state(value),
            'other_state_after':state('none'),'signed_transaction_base64':'SYNTHETIC_SIGNED_BYTES',
            'signer_public_key':'SYNTHETIC_OWNER' if key in ('owner_control','owner_after_revoke') else 'SYNTHETIC_LIMITED',
            'receiver_id':'other.owner' if key in ('denied_receiver','denied_transfer') else 'probe.owner'})
    return evidence


class AccessTests(unittest.TestCase):
    def test_legacy_missing_key_response_must_identify_the_removed_key(self):
        evidence = fixture()
        legacy = {'block_height': 18, 'error': 'access key SYNTHETIC_LIMITED does not exist while viewing', 'logs': []}
        evidence['key_after_revoke'] = raw(legacy)
        self.assertEqual(access.analyze(evidence)['matched'], 8)
        for change in ({'error': 'node unavailable'}, {'error': 'access key OTHER does not exist while viewing'},
                       {'permission': 'FullAccess'}, {'nonce': 0}):
            evidence['key_after_revoke'] = raw({**legacy, **change})
            with self.subTest(change=change), self.assertRaises(ValueError):
                access.analyze(evidence)

    def test_parser_distinguishes_expected_rejection_from_success(self):
        result=access.analyze(fixture())
        self.assertEqual(result['matched'],8)
        self.assertEqual(result['environment'],'near-sandbox')
        self.assertIn('MethodNameMismatch',result['rows'][2]['Observed'])
        self.assertEqual(len(result['rows']),8)

    def test_unexpected_error_is_not_a_passing_denial(self):
        evidence=fixture()
        evidence['checks'][2]['observation']['response']={'error':{'message':'node unavailable'}}
        result=access.analyze(evidence)
        self.assertEqual(result['matched'],7)
        self.assertEqual(result['rows'][2]['Check'],'Mismatch')
        self.assertNotIn('enforced the selected',result['supports'])

    def test_changed_contract_state_exposes_an_unexpected_execution(self):
        evidence=fixture();evidence['checks'][2]['state_after']=state('blocked')
        self.assertEqual(access.analyze(evidence)['rows'][2]['Check'],'Mismatch')
        evidence=fixture();evidence['checks'][3]['other_state_after']=state('allowed')
        self.assertEqual(access.analyze(evidence)['rows'][3]['Check'],'Mismatch')

    def test_bad_scope_environment_grant_and_revocation_rejected(self):
        for kind in ('chain','version','method','allowance','revocation','owner','bytecode','missing','signer','endpoint'):
            evidence=fixture()
            if kind=='chain':evidence['runtime']['response']['result']['chain_id']='mainnet'
            elif kind=='version':evidence['configured_version']='different'
            elif kind=='method':evidence['key_before']['response']['result']['permission']['FunctionCall']['method_names']=[]
            elif kind=='allowance':evidence['key_after_call']['response']['result']['permission']['FunctionCall']['allowance']=str(10**23)
            elif kind=='revocation':evidence['key_after_revoke']=raw({'permission':'FullAccess'})
            elif kind=='owner':evidence['owner_key_after']=raw({'permission':'restricted'})
            elif kind=='bytecode':evidence['contract']['wasm_sha256']='bad'
            elif kind=='missing':evidence['checks'].pop()
            elif kind=='signer':evidence['checks'][2]['signer_public_key']='SYNTHETIC_OWNER'
            else:evidence['checks'][2]['observation']['request']['method']='query'
            with self.subTest(kind=kind), self.assertRaises((ValueError,KeyError)):
                access.analyze(evidence)

    def test_missing_runtime_is_explicit_and_never_falls_back_to_fixture(self):
        with patch('experiments.access.availability',return_value=(False,'Setup needed')),patch('subprocess.Popen') as process:
            with self.assertRaisesRegex(RuntimeError,'Setup needed'):access.collect()
            process.assert_not_called()

    def test_replay_never_launches_node_or_downloads(self):
        evidence=fixture()
        saved={'schema_version':1,'experiment_id':'access','capture_mode':'sandbox','captured_at':'synthetic-time',
               'source_sha256':'synthetic-source','evidence_sha256':runner.digest(evidence),'evidence':evidence}
        with tempfile.TemporaryDirectory() as temp,patch.object(runner,'RECORDINGS',Path(temp)),patch('experiments.access.collect',side_effect=AssertionError('No node allowed')):
            Path(temp,'access.json').write_text(json.dumps(saved))
            out=runner.run('access','replay')
            self.assertEqual(out['mode'],'replay')
            saved['capture_mode']='live';Path(temp,'access.json').write_text(json.dumps(saved))
            with self.assertRaisesRegex(ValueError,'environment'):runner.run('access','replay')

    def test_sandbox_mode_is_separate_from_public_live_and_scenario(self):
        for name,mode in (('access','live'),('network','sandbox'),('access','scenario')):
            with self.subTest(name=name,mode=mode),self.assertRaises(ValueError):runner.run(name,mode)

    def test_missing_capture_does_not_use_a_fixture(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(runner,'RECORDINGS',Path(temp)):
            with self.assertRaisesRegex(ValueError,'No recorded observation'):
                runner.run('access','replay')
