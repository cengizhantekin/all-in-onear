"""Recompute a paired global-contract deployment comparison from local RPC evidence."""
import base64
import hashlib
import json
from decimal import Decimal

from .access import availability, collect_script
from .common import metric

PAIRS = tuple((f"local{i:02d}", f"reuse{i:02d}") for i in range(1, 4))
PUBLISHER = "publish"


def collect():
    return collect_script("global-contracts.mjs")


def result(record):
    response = record["response"]
    value = response.get("result")
    if "error" in response or not isinstance(value, dict) or "error" in value:
        raise ValueError("Incomplete local RPC evidence")
    return value


def query(record, account, request_type):
    request = record["request"]
    params = request["params"]
    if (request["method"] != "query" or params.get("request_type") != request_type
            or params.get("account_id") != account or params.get("finality") != "final"):
        raise ValueError(f"Unexpected account query for {account}")
    return result(record)


def transaction(record, account, action):
    request = record["request"]
    outcome = result(record)
    tx = outcome["transaction"]
    actions = tx["actions"]
    if (request["method"] != "send_tx" or request["params"].get("wait_until") != "FINAL"
            or outcome.get("final_execution_status") != "FINAL"
            or "SuccessValue" not in outcome.get("status", {})
            or tx["signer_id"] != account or tx["receiver_id"] != account
            or len(actions) != 1 or action not in actions[0]):
        raise ValueError(f"Expected finalized {action} for {account}")
    outcomes = [outcome["transaction_outcome"], *outcome["receipts_outcome"]]
    if len({item["id"] for item in outcomes}) != len(outcomes):
        raise ValueError("Duplicate execution outcome")
    return outcome["status"]["SuccessValue"], sum(
        int(item["outcome"]["gas_burnt"]) for item in outcomes
    )


def measure(record, account, action):
    before = query(record["before"], account, "view_account")
    after = query(record["after"], account, "view_account")
    _, gas = transaction(record["transaction"], account, action)
    storage = int(after["storage_usage"]) - int(before["storage_usage"])
    spent = int(before["amount"]) - int(after["amount"])
    if (min(storage, spent, gas) < 0 or before["locked"] != after["locked"]
            or int(after["block_height"]) <= int(before["block_height"])):
        raise ValueError(f"Unreconciled account measurements for {account}")
    return storage, spent, gas


def read_state(record, account):
    value = query(record, account, "call_function")
    if record["request"]["params"].get("method_name") != "get_last":
        raise ValueError("Wrong contract method for state check")
    return json.loads(bytes(value["result"]))


def near(yocto):
    return format(Decimal(yocto).scaleb(-24), "f").rstrip("0").rstrip(".") or "0"


def row(label, measurement, rate):
    size, cost, gas = measurement
    return {
        "Step": label,
        "Storage added (bytes)": size,
        "Storage reserve (NEAR)": near(size * rate),
        "Balance spent (NEAR)": near(cost),
        "Gas burnt (Tgas)": format(Decimal(gas).scaleb(-12), "f"),
    }


def analyze(evidence):
    runtime = result(evidence["runtime"])
    if (evidence.get("schema") != 1 or evidence.get("environment") != "near-sandbox"
            or runtime.get("chain_id") != "onear-global-contracts-sandbox"
            or runtime.get("version", {}).get("version") != "2.14.0"):
        raise ValueError("Expected the pinned local Sandbox experiment")
    wasm = base64.b64decode(evidence["contract"]["wasm_base64"], validate=True)
    if (not wasm.startswith(b"\0asm")
            or hashlib.sha256(wasm).hexdigest() != evidence["contract"]["wasm_sha256"]):
        raise ValueError("WASM evidence digest mismatch")
    rate = int(result(evidence["config"])["runtime_config"]["storage_amount_per_byte"])
    if rate <= 0 or len(evidence["pairs"]) != len(PAIRS) or len(evidence["writes"]) != 2:
        raise ValueError("Incomplete paired deployment evidence")

    publication = measure(evidence["publication"], PUBLISHER, "DeployGlobalContract")
    rows = [row("Publish shared code once", publication, rate)]
    regular, attached = [], []
    for (local, shared), pair in zip(PAIRS, evidence["pairs"]):
        local_before = query(pair["local"]["before"], local, "view_account")
        shared_before = query(pair["global"]["before"], shared, "view_account")
        if any(local_before[k] != shared_before[k] for k in ("amount", "locked", "storage_usage", "code_hash")):
            raise ValueError("Paired accounts started in different states")
        regular.append(measure(pair["local"], local, "DeployContract"))
        attached.append(measure(pair["global"], shared, "UseGlobalContract"))
        rows.append(row(f"{local}: deploy a copy", regular[-1], rate))
        rows.append(row(f"{shared}: attach by hash", attached[-1], rate))

    for account, record in zip(PAIRS[0], evidence["writes"]):
        value, _ = transaction(record, account, "FunctionCall")
        action = result(record)["transaction"]["actions"][0]["FunctionCall"]
        if action["method_name"] != "allowed" or json.loads(base64.b64decode(value)) != "allowed":
            raise ValueError("State-write control did not execute the expected method")
    for pair in PAIRS:
        for account in pair:
            initial = read_state(evidence["initial"][account], account)
            final = read_state(evidence["final"][account], account)
            if initial != "none" or final != ("allowed" if pair == PAIRS[0] else "none"):
                raise ValueError("The two deployment paths failed the independent-state check")

    regular_total = tuple(map(sum, zip(*regular)))
    shared_total = tuple(map(sum, zip(publication, *attached)))
    rows.extend((row("Total: three separate deployments", regular_total, rate),
                 row("Total: one publication and three attachments", shared_total, rate)))
    regular_bytes = regular_total[0]
    shared_bytes = sum(item[0] for item in attached)
    return {
        "headline": "One publication, three accounts with independent state.",
        "summary": f"A {len(wasm)}-byte contract added {regular_bytes} bytes across three regular accounts "
                   f"and {shared_bytes} bytes across three accounts referencing the shared code. "
                   "Both paths passed the state-write and isolation checks.",
        "metrics": [metric("WASM size", len(wasm), "bytes"), metric("Accounts per path", len(PAIRS)),
                    metric("Regular account storage added", regular_bytes, "bytes"),
                    metric("Shared account storage added", shared_bytes, "bytes")],
        "rows": rows,
        "supports": "The comparison measures per-account reuse and includes the separate upfront publication in the shared total. "
                    "Balance spent is measured after finalized refunds. The storage reserve uses the protocol rate and remains part of the account balance.",
        "investment_link": "Shared contract code gives applications that repeat the same deployment a way to reduce per-account storage. "
                           "The number of reuses and publication cost determine the economics of a given deployment.",
        "limits": "A fixed local Sandbox with three accounts per path and a small probe contract. "
                  "The account storage totals cover the measured accounts and exclude the protocol-wide shared code copies. "
                  "The publication balance change includes execution fees and the protocol's publication charge. "
                  "The state writes occur after the cost measurements. Mainnet fees and workloads vary.",
        "environment": "near-sandbox",
    }
