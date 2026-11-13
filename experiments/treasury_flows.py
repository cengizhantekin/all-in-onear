"""Reconcile three native NEAR transfers to the labeled Intents buyback wallet."""
import base64
import json

from .common import ARCHIVE_RPC_URL, fetch_json, metric, now

INTENTS = "intents.near"
WRAP = "wrap.near"
WALLET = "buybacks.multisignature.near"
TRANSACTIONS = (
    "4sK4wJJrUQABRDnUXZKeYw6Le2NnP32UUxtAwjZ7tArB",
    "7J3qVuoMw22aTwpyqTdciSM5fCfWvXrjcMMNjV4LNCbZ",
    "7N6qqWNGLMD5opaprnJESuUehJq3PB5kqAEgnjw9fpkE",
)


def request(tx):
    return {"jsonrpc": "2.0", "id": "onear", "method": "EXPERIMENTAL_tx_status",
            "params": [tx, INTENTS]}


def collect():
    records = []
    for tx in TRANSACTIONS:
        payload = request(tx)
        response = fetch_json(ARCHIVE_RPC_URL, payload)
        records.append({"endpoint": ARCHIVE_RPC_URL, "request": payload,
                        "observed_at": now(), "response": response})
    return {"transactions": records}


def args(action, method):
    call = action["FunctionCall"]
    if call["method_name"] != method:
        raise ValueError(f"Expected {method}")
    return json.loads(base64.b64decode(call["args"], validate=True))


def linked_call(receipts, children, predecessor, receiver, method):
    matches = []
    for rid in children:
        receipt = receipts.get(rid)
        if receipt is None or receipt["predecessor_id"] != predecessor or receipt["receiver_id"] != receiver:
            continue
        actions = receipt["receipt"].get("Action", {}).get("actions", [])
        if len(actions) == 1 and actions[0].get("FunctionCall", {}).get("method_name") == method:
            matches.append((rid, args(actions[0], method)))
    if len(matches) != 1:
        raise ValueError(f"Expected one linked {method} receipt")
    return matches[0]


def transfer(receipts, outcomes, parent, predecessor, receiver, amount):
    parent_outcome = outcomes[parent]["outcome"]
    if parent_outcome["executor_id"] != predecessor:
        raise ValueError("Unexpected transfer parent executor")
    rid = parent_outcome["status"]["SuccessReceiptId"]
    if rid not in parent_outcome["receipt_ids"]:
        raise ValueError("Transfer receipt is not linked to its parent")
    receipt = receipts[rid]
    outcome = outcomes[rid]["outcome"]
    if (receipt["predecessor_id"] != predecessor or receipt["receiver_id"] != receiver
            or receipt["receipt"]["Action"]["actions"] != [{"Transfer": {"deposit": amount}}]
            or outcome["executor_id"] != receiver or "SuccessValue" not in outcome["status"]):
        raise ValueError("Transfer receipt does not reconcile")
    return rid


def reconcile(tx, record):
    if record["endpoint"] != ARCHIVE_RPC_URL or record["request"] != request(tx):
        raise ValueError("Unexpected archive request")
    response = record["response"]
    if "error" in response:
        raise ValueError("Archival RPC rejected the transaction lookup")
    execution = response["result"]
    transaction = execution["transaction"]
    if (execution["final_execution_status"] != "FINAL" or "SuccessValue" not in execution["status"]
            or transaction["hash"] != tx or transaction["signer_id"] != INTENTS
            or transaction["receiver_id"] != INTENTS or len(transaction["actions"]) != 1):
        raise ValueError("Expected the pinned finalized Intents transaction")
    args(transaction["actions"][0], "execute_intents")
    receipt_list = execution["receipts"]
    outcome_list = execution["receipts_outcome"]
    receipts = {entry["receipt_id"]: entry for entry in receipt_list}
    outcomes = {entry["id"]: entry for entry in outcome_list}
    if len(receipts) != len(receipt_list) or len(outcomes) != len(outcome_list):
        raise ValueError("Duplicate receipt or receipt outcome")
    root = execution["transaction_outcome"]["outcome"]["status"]["SuccessReceiptId"]
    root_outcome = outcomes[root]["outcome"]
    if root_outcome["executor_id"] != INTENTS or "SuccessValue" not in root_outcome["status"]:
        raise ValueError("Expected successful execution on the Intents verifier")
    withdrawals = []
    for log in root_outcome["logs"]:
        if log.startswith("EVENT_JSON:"):
            event = json.loads(log.removeprefix("EVENT_JSON:"))
            if event["standard"] == "dip4" and event["event"] == "native_withdraw":
                withdrawals.extend(x for x in event["data"] if x["receiver_id"] == WALLET)
    if len(withdrawals) != 1:
        raise ValueError("Expected one withdrawal event to the labeled wallet")
    amount = withdrawals[0]["amount"]
    if not isinstance(amount, str) or not amount.isascii() or not amount.isdecimal() or not 1 <= len(amount) <= 39 or int(amount) <= 0:
        raise ValueError("Invalid withdrawal amount")
    children = root_outcome["receipt_ids"]
    unwrap, unwrap_args = linked_call(receipts, children, INTENTS, WRAP, "near_withdraw")
    callback, callback_args = linked_call(receipts, children, INTENTS, INTENTS, "do_native_withdraw")
    if unwrap_args != {"amount": amount} or callback_args != {"withdraw": {"receiver_id": WALLET, "amount": amount}}:
        raise ValueError("The withdrawal event, unwrap call and payout callback disagree")
    unwrap_action = receipts[unwrap]["receipt"]["Action"]["actions"][0]["FunctionCall"]
    if unwrap_action["deposit"] != "1":
        raise ValueError("Expected the one-yocto unwrap deposit")
    # wrap.near returns the unwrapped amount plus the attached yoctoNEAR.
    returned = transfer(receipts, outcomes, unwrap, WRAP, INTENTS, str(int(amount) + 1))
    data_receivers = receipts[returned]["receipt"]["Action"]["output_data_receivers"]
    callback_inputs = receipts[callback]["receipt"]["Action"]["input_data_ids"]
    if len(callback_inputs) != 1 or data_receivers != [{"data_id": callback_inputs[0], "receiver_id": INTENTS}]:
        raise ValueError("The payout callback does not wait for the unwrap transfer")
    delivered = transfer(receipts, outcomes, callback, INTENTS, WALLET, amount)
    return int(amount), delivered


def near(yocto):
    micros = (yocto + 5 * 10**17) // 10**18
    return f"{micros // 10**6:,}.{micros % 10**6:06d}"


def analyze(evidence):
    records = evidence["transactions"]
    if not isinstance(records, list) or len(records) != len(TRANSACTIONS):
        raise ValueError("Expected all three pinned transaction records")
    rows = []
    receipt_ids = set()
    total = 0
    for tx, record in zip(TRANSACTIONS, records):
        amount, receipt = reconcile(tx, record)
        if receipt in receipt_ids:
            raise ValueError("A wallet credit was counted twice")
        receipt_ids.add(receipt)
        total += amount
        rows.append({"Transaction hash": tx, "Wallet transfer receipt": receipt,
                     "Amount received (NEAR)": near(amount), "Status": "Finalized and reconciled"})
    return {
        "headline": "Follow wrapped NEAR into the labeled buyback wallet.",
        "summary": f"Three finalized Intents transactions delivered {near(total)} NEAR to {WALLET}. "
                   "Each withdrawal event reconciles with a wrap.near unwrap and the final native transfer.",
        "metrics": [metric("Finalized wallet transfers", len(rows)),
                    metric("Native NEAR received", near(total), "NEAR"),
                    metric("Matching withdrawal paths", len(rows))],
        "rows": rows,
        "supports": "The amount can be traced from the Intents withdrawal event through unwrapping to the destination wallet.",
        "investment_link": "The transfers make one downstream token flow from the Intents system auditable alongside reported historical wallet revenue.",
        "limits": "Three selected transactions discovered through NearBlocks. The archive replies are public RPC evidence. "
                  "This sample traces withdrawals of existing wNEAR and incoming native NEAR. "
                  "It does not identify a preceding market purchase, the source of every token, subsequent use, or total buyback or burn activity.",
        "destination": WALLET, "total_yocto": str(total),
    }
