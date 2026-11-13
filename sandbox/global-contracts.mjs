/** Controlled deploy-by-hash comparison on a fresh local NEAR Sandbox. */
import { Sandbox, GenesisAccount } from 'near-sandbox';
import { KeyPair, KeyPairSigner, createTransaction, actions, baseDecode, baseEncode, decodeSignedTransaction } from 'near-api-js';
import wabtFactory from 'wabt';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const VERSION = '2.14.0';
const CHAIN_ID = 'onear-global-contracts-sandbox';
const PUBLISHER = 'publish';
const PAIRS = ['01', '02', '03'].map(id => ['local' + id, 'reuse' + id]);
const started = new Date().toISOString();
const digest = bytes => createHash('sha256').update(bytes).digest();
const wat = await readFile(new URL('permission-probe.wat', import.meta.url), 'utf8');
const wabt = await wabtFactory();
const parsed = wabt.parseWat('permission-probe.wat', wat, { bulk_memory: false, simd: false });
const wasm = parsed.toBinary({ canonicalize_lebs: true }).buffer;
parsed.destroy();
assert(WebAssembly.validate(wasm));
const codeHash = digest(wasm);

const key = KeyPair.fromRandom('ed25519');
const signer = new KeyPairSigner(key);
const publicKey = key.getPublicKey();
const normal = () => actions.deployContract(wasm);
const publish = () => actions.deployGlobalContract(wasm, 'codeHash');
const reuse = () => actions.useGlobalContract({ codeHash });
let sandbox;
let rpcId = 0;

async function rpc(method, params) {
  const url = new URL(sandbox.rpcUrl);
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1') throw new Error('Sandbox must use loopback RPC');
  const request = { jsonrpc: '2.0', id: ++rpcId, method, params };
  const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request), signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(method + ' returned HTTP ' + response.status);
  return { request, response: await response.json() };
}

function result(record) {
  const { response, request } = record;
  const failure = response.error ?? response.result?.error;
  if (failure || !response.result) throw new Error(request.method + ': ' + JSON.stringify(failure ?? 'Missing result').slice(0, 1000));
  return response.result;
}

const account = id => rpc('query', { request_type: 'view_account', finality: 'final', account_id: id });
const state = id => rpc('query', { request_type: 'call_function', finality: 'final',
  account_id: id, method_name: 'get_last', args_base64: 'e30=' });

async function signed(id, action, nonce, blockHash) {
  return (await signer.signTransaction(createTransaction(id, publicKey, id, nonce, [action], blockHash))).signedTransaction.encode();
}

async function transact(id, action) {
  const access = result(await rpc('query', { request_type: 'view_access_key', finality: 'final',
    account_id: id, public_key: publicKey.toString() }));
  const nonce = access.nonce;
  if (!((Number.isSafeInteger(nonce) && nonce >= 0) || (typeof nonce === 'string' && /^\d+$/.test(nonce)))) {
    throw new Error('Unexpected local account nonce');
  }
  const bytes = await signed(id, action, BigInt(nonce) + 1n, baseDecode(access.block_hash));
  const observation = await rpc('send_tx', { signed_tx_base64: Buffer.from(bytes).toString('base64'), wait_until: 'FINAL' });
  const outcome = result(observation);
  if (outcome.final_execution_status !== 'FINAL' || !outcome.status || !('SuccessValue' in outcome.status)) {
    throw new Error(id + ' transaction did not finalize successfully: ' + JSON.stringify(outcome.status).slice(0, 1000));
  }
  return observation;
}

async function measure(id, action) {
  const before = await account(id);
  result(before);
  const transaction = await transact(id, action);
  const after = await account(id);
  result(after);
  return { before, transaction, after };
}

async function experiment() {
  for (const name of ['SANDBOX_ARTIFACT_URL', 'NEAR_SANDBOX_BIN_PATH', 'DIR_TO_DOWNLOAD_BINARY']) {
    if (process.env[name]) throw new Error('Remove Sandbox binary overrides for this fixed-version experiment');
  }
  if (!['linux', 'darwin'].includes(process.platform)) throw new Error('Use Linux/WSL or macOS ARM64');
  if (process.platform === 'linux') {
    const limits = await readFile('/proc/self/limits', 'utf8');
    const hard = limits.match(/^Max open files\s+\S+\s+(\S+)/m)?.[1];
    if (hard && hard !== 'unlimited' && Number(hard) < 65535) throw new Error('Official Sandbox needs a hard open-file limit of at least 65535');
  }
  console.error('Starting the local global-contract comparison.');
  const ids = [PUBLISHER, ...PAIRS.flat()];
  sandbox = await Sandbox.start({ version: VERSION, config: {
    additionalGenesis: { chain_id: CHAIN_ID },
    additionalAccounts: ids.map(id => new GenesisAccount(id, publicKey.toString(), key.toString(), 10n * 10n ** 24n)),
    additionalConfig: { network: { boot_nodes: '' } },
  } });
  const runtime = await rpc('status', []);
  if (result(runtime).chain_id !== CHAIN_ID) throw new Error('Unexpected chain ID');
  const config = await rpc('EXPERIMENTAL_protocol_config', { finality: 'final' });
  result(config);
  const publication = await measure(PUBLISHER, publish());
  const pairs = [];
  for (const [local, shared] of PAIRS) {
    pairs.push({ local: await measure(local, normal()), global: await measure(shared, reuse()) });
  }
  const initial = {};
  for (const id of PAIRS.flat()) initial[id] = await state(id);
  const writes = [];
  for (const id of PAIRS[0]) writes.push(await transact(id, actions.functionCall('allowed', {}, 30n * 10n ** 12n, 0n)));
  const final = {};
  for (const id of PAIRS.flat()) final[id] = await state(id);
  return { schema: 1, environment: 'near-sandbox', started_at: started, finished_at: new Date().toISOString(),
    runtime, config, publication, pairs, initial, writes, final,
    contract: { wasm_base64: Buffer.from(wasm).toString('base64'), wasm_sha256: codeHash.toString('hex'),
      code_hash_base58: baseEncode(codeHash) },
    binary_sha256: digest(await readFile(new URL('node_modules/near-sandbox/bin/near-sandbox-2.14.0/near-sandbox', import.meta.url))).toString('hex') };
}

if (process.argv[2] === '--check' && process.argv.length === 3) {
  for (const [name, action] of [['deployContract', normal()], ['deployGlobalContract', publish()], ['useGlobalContract', reuse()]]) {
    const bytes = await signed(PUBLISHER, action, 1n, new Uint8Array(32));
    const decoded = decodeSignedTransaction(bytes);
    assert(decoded.transaction.actions[0][name], name);
  }
  console.log('Compiled identical WASM and verified all three signed action encodings offline.');
} else {
  if (process.argv.length !== 2) throw new Error('This fixed experiment accepts no arguments');
  const timer = setTimeout(async () => {
    console.error('Global-contract experiment timed out.');
    try { if (sandbox) await sandbox.tearDown(); } finally { process.exit(1); }
  }, 240000);
  try {
    const evidence = await experiment();
    await sandbox.tearDown();
    sandbox = null;
    console.log(JSON.stringify(evidence));
  } catch (error) {
    console.error('Global-contract experiment failed:', error instanceof Error ? error.message.slice(0, 1500) : 'unknown error');
    if (sandbox) await sandbox.tearDown().catch(() => {});
    process.exitCode = 1;
  } finally {
    clearTimeout(timer);
  }
}
