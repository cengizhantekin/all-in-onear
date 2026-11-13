/** Offline preparation checks only: this is NOT a NEAR runtime test. */
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import wabtFactory from 'wabt';
import { KeyPair, KeyPairSigner, createTransaction, actions, decodeSignedTransaction } from 'near-api-js';
const wabt = await wabtFactory();
const wat = wabt.parseWat('permission-probe.wat', await readFile(new URL('permission-probe.wat', import.meta.url), 'utf8'));
const wasm = wat.toBinary({ canonicalize_lebs:true }).buffer;
wat.destroy();
assert(WebAssembly.validate(wasm));
const compiled = await WebAssembly.compile(wasm);
assert.deepEqual(WebAssembly.Module.exports(compiled).map(x=>x.name), ['memory','allowed','blocked','get_last']);
const key = KeyPair.fromRandom('ed25519');
const tx = createTransaction('owner',key.getPublicKey(),'probe.owner',1n,
  [actions.functionCall('blocked',{},30n*10n**12n,0n)],new Uint8Array(32));
const {signedTransaction} = await new KeyPairSigner(key).signTransaction(tx);
const decoded=decodeSignedTransaction(signedTransaction.encode());
assert.equal(decoded.transaction.receiverId,'probe.owner');
assert.equal(decoded.transaction.actions[0].functionCall.methodName,'blocked');
// No account/permission lookup or local filter is needed to encode this disallowed-method probe.
console.log('Offline WAT compilation and signed transaction encoding passed. No NEAR runtime was started.');
