/** Real local node experiment. No account/key from a public network is loaded. */
import { Sandbox, GenesisAccount } from 'near-sandbox';
import { KeyPair, KeyPairSigner, createTransaction, actions, baseDecode, baseEncode } from 'near-api-js';
import wabtFactory from 'wabt';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const VERSION = '2.14.0';
const CHAIN_ID = 'onear-access-keys-sandbox';
const ALLOWANCE = 10n ** 23n; // 0.1 local NEAR gas budget, not a token transfer limit.
const GAS = 30n * 10n ** 12n;
const ownerId = 'owner';
const target = 'probe.owner';
const other = 'other.owner';
let sandbox;
let rpcId = 0;
const ownerKey = KeyPair.fromRandom('ed25519');
const limitedKey = KeyPair.fromRandom('ed25519');
const nonceCache = new Map();
const now = () => new Date().toISOString();
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');

async function rpc(method, params) {
  const url = new URL(sandbox.rpcUrl);
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1') throw new Error('Local RPC invariant violated');
  const request = { jsonrpc: '2.0', id: ++rpcId, method, params };
  const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request), signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Local RPC HTTP ${response.status}`);
  return { request, response: await response.json(), observed_at: now() };
}
function result(record) {
  if (record.response.error || record.response.result?.error || !('result' in record.response)) {
    // Only node RPC responses are printed, never SDK objects or genesis keys.
    const context = [record.request.method, record.request.params?.request_type,
      record.request.params?.account_id].filter(Boolean).join('/');
    const detail = JSON.stringify(record.response.error ?? record.response.result?.error ?? { message: 'Missing RPC result' });
    throw new Error(`Local setup/query failed [${context}]: ${detail.slice(0, 1400)}`);
  }
  return record.response.result;
}
const accessKey = (key) => rpc('query', { request_type: 'view_access_key', finality: 'optimistic',
  account_id: ownerId, public_key: key.getPublicKey().toString() });
async function view(account = target) {
  return rpc('query', { request_type: 'call_function', finality: 'optimistic', account_id: account,
    method_name: 'get_last', args_base64: 'e30=' });
}
async function submit(key, receiver, txActions, label) {
  const pk = key.getPublicKey().toString();
  const keyState = await accessKey(key);
  let nonce;
  if (keyState.response.result && !keyState.response.result.error) {
    const n = keyState.response.result.nonce;
    if (!(typeof n === 'number' && Number.isSafeInteger(n) && n >= 0) &&
        !(typeof n === 'string' && /^(0|[1-9][0-9]*)$/.test(n))) {
      throw new Error('Invalid nonce in local access-key response');
    }
    const chainNonce = BigInt(n);
    const cachedNonce = nonceCache.get(pk) ?? 0n;
    nonce = (chainNonce > cachedNonce ? chainNonce : cachedNonce) + 1n;
  } else {
    // Intentionally submit the revoked key to the node; do NOT reject it in the SDK.
    if (!nonceCache.has(pk)) { result(keyState); throw new Error('Missing nonce for revoked-key probe'); }
    nonce = nonceCache.get(pk) + 1n;
  }
  const block = result(await rpc('block', { finality: 'final' }));
  const tx = createTransaction(ownerId, key.getPublicKey(), receiver, nonce, txActions, baseDecode(block.header.hash));
  const { signedTransaction, txHash } = await new KeyPairSigner(key).signTransaction(tx);
  nonceCache.set(pk, nonce);
  const signed = Buffer.from(signedTransaction.encode()).toString('base64');
  const started = now();
  const observation = await rpc('broadcast_tx_commit', [signed]);
  return { id: label, signer_public_key: pk, receiver_id: receiver, nonce: nonce.toString(),
    transaction_hash: baseEncode(txHash), signed_transaction_base64: signed,
    started_at: started, finished_at: now(), observation };
}
function setupSucceeded(item) {
  const r = result(item.observation);
  if (r.status?.Failure || !r.status || !('SuccessValue' in r.status)) {
    throw new Error(`Setup transaction failed [${item.id}]: ${JSON.stringify(r.status).slice(0, 1400)}`);
  }
}
const call = (method, deposit = 0n) => actions.functionCall(method, {}, GAS, deposit);
async function probe(id, key, receiver, action) {
  const item = await submit(key, receiver, [action], id);
  item.state_after = await view();
  item.other_state_after = await view(other);
  return item;
}

async function main() {
  if (process.argv.length !== 2) throw new Error('This fixed experiment accepts no arguments');
  for (const key of ['SANDBOX_ARTIFACT_URL', 'NEAR_SANDBOX_BIN_PATH', 'DIR_TO_DOWNLOAD_BINARY']) {
    if (process.env[key]) throw new Error('Remove sandbox binary overrides for this fixed-version experiment');
  }
  if (!['linux', 'darwin'].includes(process.platform)) throw new Error('Use Linux/WSL or macOS ARM64 to run a fresh sandbox');
  if (process.platform === 'linux') {
    const limits = await readFile('/proc/self/limits', 'utf8');
    const match = limits.match(/^Max open files\s+(\S+)\s+(\S+)/m);
    if (match && match[2] !== 'unlimited' && Number(match[2]) < 65535) throw new Error('Official Sandbox requires hard NOFILE >=65535. This environment cannot start it.');
  }
  const started = now();
  const wat = await readFile(new URL('permission-probe.wat', import.meta.url), 'utf8');
  const wabt = await wabtFactory();
  const parsed = wabt.parseWat('permission-probe.wat', wat, { bulk_memory: false, simd: false });
  const wasm = parsed.toBinary({ canonicalize_lebs: true }).buffer;
  parsed.destroy();
  console.error('Starting NEAR Sandbox 2.14.0; first run may download its binary.');
  sandbox = await Sandbox.start({ version: VERSION, config: {
    additionalGenesis: { chain_id: CHAIN_ID },
    additionalAccounts: [new GenesisAccount(ownerId, ownerKey.getPublicKey().toString(), ownerKey.toString(), 100n * 10n ** 24n)],
    additionalConfig: { network: { boot_nodes: '' } },
  } });
  const runtime = await rpc('status', []);
  if (result(runtime).chain_id !== CHAIN_ID) throw new Error('Unexpected sandbox chain ID');
  const setup = [];
  for (const account of [target, other]) {
    const item = await submit(ownerKey, account, [actions.createAccount(), actions.transfer(10n * 10n ** 24n),
      actions.deployContract(wasm)], `deploy_${account}`);
    setupSucceeded(item); setup.push(item);
  }
  const initial_state = await view();
  const initial_other_state = await view(other);
  const checks = [];
  checks.push(await probe('owner_control', ownerKey, target, call('blocked')));
  const grant = await submit(ownerKey, ownerId,
    [actions.addFunctionCallAccessKey(limitedKey.getPublicKey(), target, ['allowed'], ALLOWANCE)], 'grant');
  setupSucceeded(grant); setup.push(grant);
  const key_before = await accessKey(limitedKey);
  checks.push(await probe('allowed_call', limitedKey, target, call('allowed')));
  const key_after_call = await accessKey(limitedKey);
  checks.push(await probe('denied_method', limitedKey, target, call('blocked')));
  checks.push(await probe('denied_receiver', limitedKey, other, call('allowed')));
  checks.push(await probe('denied_deposit', limitedKey, target, call('allowed', 1n)));
  checks.push(await probe('denied_transfer', limitedKey, other, actions.transfer(1n)));
  const revoke = await submit(ownerKey, ownerId, [actions.deleteKey(limitedKey.getPublicKey())], 'revoke');
  setupSucceeded(revoke); setup.push(revoke);
  const key_after_revoke = await accessKey(limitedKey);
  checks.push(await probe('revoked_call', limitedKey, target, call('allowed')));
  checks.push(await probe('owner_after_revoke', ownerKey, target, call('allowed')));
  const owner_key_after = await accessKey(ownerKey);
  return { schema: 1, environment: 'near-sandbox', started_at: started, finished_at: now(),
    runtime, configured_version: VERSION,
    binary_sha256: hash(await readFile(new URL('node_modules/near-sandbox/bin/near-sandbox-2.14.0/near-sandbox', import.meta.url))),
    owner_account: ownerId, target_account: target, other_account: other,
    owner_public_key: ownerKey.getPublicKey().toString(), limited_public_key: limitedKey.getPublicKey().toString(),
    permission: { receiver_id: target, method_names: ['allowed'], allowance_yocto: ALLOWANCE.toString() },
    contract: { wat_sha256: hash(wat), wasm_sha256: hash(wasm), wasm_base64: Buffer.from(wasm).toString('base64') },
    initial_state, initial_other_state, setup, key_before, key_after_call, key_after_revoke, owner_key_after, checks };
}

const watchdog = setTimeout(async () => {
  console.error('Sandbox experiment timed out. No successful result was substituted.');
  try { if (sandbox) await sandbox.tearDown(); } finally { process.exit(1); }
}, 240000);
try {
  const evidence = await main();
  await sandbox.tearDown(); sandbox = null;
  console.log(JSON.stringify(evidence));
} catch (error) {
  // Do not serialize SDK objects: a thrown object might carry in-memory test keys.
  console.error('Sandbox experiment failed:', error instanceof Error ? error.message.slice(0, 1800) : 'unknown error');
  if (sandbox) await sandbox.tearDown().catch(() => {});
  process.exitCode = 1;
} finally { clearTimeout(watchdog); }
