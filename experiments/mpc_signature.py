"""Verify one historical secp256k1 Chain Signatures receipt using public data."""
import base64
import hashlib
import json

from .common import ARCHIVE_RPC_URL, fetch_json, metric, now

TX = "A9bXyEZLSxUeL7jEZmwsXks3a1RCYjYTnct9msnpNBCN"
TX_SENDER = "omni-relayer.bridge.near"
SIGN_RECEIPT = "HhU4ktsFCcWPsWyJTwwMMToxjVypWMGrdLoqXCeYnoEo"
SIGNER = "v1.signer"
EXPLORER = f"https://nearblocks.io/txns/{TX}/execution"
TWEAK_PREFIX = "near-mpc-recovery v0.1.0 epsilon derivation:"

# SEC 2 secp256k1 parameters. These routines operate only on public data.
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def add(a, b):
    if a is None or b is None:
        return b if a is None else a
    x1, y1 = a
    x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if a == b:
        slope = 3 * x1 * x1 * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P
    x = (slope * slope - x1 - x2) % P
    return x, (slope * (x1 - x) - y1) % P


def multiply(scalar, point):
    result = None
    for bit in bin(scalar % N)[2:]:
        result = add(result, result)
        if bit == "1":
            result = add(result, point)
    return result


def valid_point(point):
    x, y = point
    return 0 <= x < P and 0 <= y < P and (y * y - x * x * x - 7) % P == 0


def root_point(key):
    scheme, encoded = key.split(":", 1)
    if scheme != "secp256k1" or not 1 <= len(encoded) <= 89:
        raise ValueError("Unexpected root key encoding")
    number = 0
    for char in encoded:
        number = number * 58 + BASE58.index(char)
    leading = len(encoded) - len(encoded.lstrip("1"))
    raw = bytes(leading) + number.to_bytes((number.bit_length() + 7) // 8, "big")
    point = (int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big"))
    if len(raw) != 64 or not valid_point(point):
        raise ValueError("Invalid historical root point")
    return point


def verify(digest, point, r, s):
    if len(digest) != 32 or point is None or not (1 <= r < N and 1 <= s < N):
        return False
    inverse = pow(s, -1, N)
    check = add(multiply(int.from_bytes(digest, "big") * inverse, G),
                multiply(r * inverse, point))
    return check is not None and check[0] % N == r


def decoded(value):
    return json.loads(base64.b64decode(value, validate=True))


def transaction_request():
    return {"jsonrpc": "2.0", "id": "onear", "method": "EXPERIMENTAL_tx_status",
            "params": [TX, TX_SENDER]}


def key_request(block, domain):
    return {"jsonrpc": "2.0", "id": "onear", "method": "query", "params": {
        "request_type": "call_function", "block_id": block, "account_id": SIGNER,
        "method_name": "public_key",
        "args_base64": base64.b64encode(json.dumps({"domain_id": domain}, separators=(",", ":")).encode()).decode(),
    }}


def rpc_result(record, request):
    response = record["response"]
    if record["request"] != request or record["endpoint"] != ARCHIVE_RPC_URL:
        raise ValueError("Historical RPC request does not match the experiment")
    if "error" in response or not isinstance(response.get("result"), dict):
        raise ValueError("Historical RPC did not return a result")
    return response["result"]


def function_args(receipt, method):
    actions = receipt["receipt"]["Action"]["actions"]
    if len(actions) != 1 or actions[0].get("FunctionCall", {}).get("method_name") != method:
        raise ValueError(f"Expected the {method} receipt")
    return decoded(actions[0]["FunctionCall"]["args"])


def trace(record):
    outcome = rpc_result(record, transaction_request())
    transaction = outcome["transaction"]
    if (outcome["final_execution_status"] != "FINAL" or transaction["hash"] != TX
            or transaction["signer_id"] != TX_SENDER or "SuccessValue" not in outcome["status"]):
        raise ValueError("Expected the pinned finalized transaction")
    receipts = {item["receipt_id"]: item for item in outcome["receipts"]}
    outcomes = {item["id"]: item for item in outcome["receipts_outcome"]}
    sign = receipts[SIGN_RECEIPT]
    signer_outcome = outcomes[SIGN_RECEIPT]
    if sign["receiver_id"] != SIGNER or signer_outcome["outcome"]["executor_id"] != SIGNER:
        raise ValueError("Sign request did not execute on the expected contract")
    request = function_args(sign, "sign")["request"]
    domain = request["key_version"]
    digest = bytes(request["payload"])
    if domain != 0 or len(digest) != 32 or not isinstance(request["path"], str):
        raise ValueError("Unexpected signing request")
    callback_id = signer_outcome["outcome"]["status"]["SuccessReceiptId"]
    callback = receipts[callback_id]
    response = outcomes[callback_id]["outcome"]
    if callback["predecessor_id"] != SIGNER or callback["receiver_id"] != SIGNER or response["executor_id"] != SIGNER:
        raise ValueError("Unexpected signature callback")
    callback_args, = function_args(callback, "return_signature_and_clean_state_on_success")
    tweak = hashlib.sha3_256((TWEAK_PREFIX + sign["predecessor_id"] + "," + request["path"]).encode()).digest()
    if (callback_args["domain_id"] != domain or bytes(callback_args["tweak"]) != tweak
            or bytes.fromhex(callback_args["payload"]["Ecdsa"]) != digest):
        raise ValueError("Callback digest, domain or derivation does not match the request")
    return (signer_outcome["block_hash"], sign["predecessor_id"], request["path"],
            domain, digest, tweak, callback_id, decoded(response["status"]["SuccessValue"]))


def archive(request):
    return {"endpoint": ARCHIVE_RPC_URL, "request": request,
            "response": fetch_json(ARCHIVE_RPC_URL, request), "observed_at": now()}


def collect():
    transaction = archive(transaction_request())
    block, _, _, domain, *_ = trace(transaction)
    return {"transaction": transaction, "historical_key": archive(key_request(block, domain))}


def analyze(evidence):
    block, caller, path, domain, digest, tweak, callback_id, signature = trace(evidence["transaction"])
    historical = rpc_result(evidence["historical_key"], key_request(block, domain))
    if historical["block_hash"] != block:
        raise ValueError("Root key was not read at the sign receipt block")
    root = root_point(json.loads(bytes(historical["result"])))
    derived = add(root, multiply(int.from_bytes(tweak, "big"), G))
    if derived is None or not valid_point(derived):
        raise ValueError("Derived point is invalid")

    r_point = bytes.fromhex(signature["big_r"]["affine_point"])
    scalar = bytes.fromhex(signature["s"]["scalar"])
    if (signature["scheme"] != "Secp256k1" or len(r_point) != 33 or r_point[0] not in (2, 3)
            or len(scalar) != 32):
        raise ValueError("Unexpected secp256k1 signature encoding")
    x = int.from_bytes(r_point[1:], "big")
    y = pow((x * x * x + 7) % P, (P + 1) // 4, P)
    y = y if y % 2 == r_point[0] % 2 else (-y) % P
    if not valid_point((x, y)):
        raise ValueError("Invalid signature point")
    r, s = x % N, int.from_bytes(scalar, "big")
    changed = bytes([digest[0] ^ 1]) + digest[1:]
    original_ok = verify(digest, derived, r, s)
    changed_ok = verify(changed, derived, r, s)
    if not original_ok or changed_ok:
        raise ValueError("The original signature or one-byte control did not match expectations")
    compressed = bytes([2 + derived[1] % 2]) + derived[0].to_bytes(32, "big")
    return {
        "headline": "A public Chain Signatures response verifies offline.",
        "summary": "The ECDSA signature matched the original 32-byte digest and the independently derived public key. "
                   "Flipping one bit in the first digest byte made the same signature fail verification.",
        "metrics": [metric("Original digest", "Valid"), metric("Changed digest", "Rejected"),
                    metric("Digest length", len(digest), "bytes"), metric("Signing domain", domain)],
        "rows": [{"Check": "Original digest", "Digest (hex)": digest.hex(), "Expected": "Valid", "Observed": "Valid"},
                 {"Check": "First byte changed", "Digest (hex)": changed.hex(), "Expected": "Rejected", "Observed": "Rejected"}],
        "supports": "One finalized mainnet request produced a signature that verifies against a public key derived from "
                    "its calling account, derivation path and historical root key.",
        "investment_link": "Applications can use shared signing infrastructure and independently verify returned signatures for their derived keys.",
        "limits": "One archived ECDSA request. The evidence uses archival RPC transaction and state data, "
                  "and the offline check verifies the signed digest and signature scalars. "
                  "The originating Bitcoin payload, foreign-chain settlement and signer independence are outside the measurement.",
        "block_height": historical["block_height"], "block_hash": block,
        "transaction_hash": TX, "sign_receipt_id": SIGN_RECEIPT, "callback_receipt_id": callback_id,
        "calling_account": caller, "derivation_path": path, "derived_public_key": compressed.hex(),
    }
