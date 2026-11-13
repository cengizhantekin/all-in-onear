"""Read v1.signer state. Do not request a signature or contact MPC operators."""
import json
from .common import metric, rpc


def collect():
    return {"state": rpc("query", {
        "request_type": "call_function", "finality": "final",
        "account_id": "v1.signer", "method_name": "state", "args_base64": "e30=",
    })}


def analyze(evidence):
    result = evidence["state"]["response"]["result"]
    state = json.loads(bytes(result["result"]).decode())
    if "Running" not in state:
        raise ValueError("Signer is not in the expected Running state; review the new schema")
    running = state["Running"]
    parameters = running["parameters"]
    participants = parameters["participants"]["participants"]
    threshold = parameters["threshold"]
    if not isinstance(threshold, int) or not 1 <= threshold <= len(participants):
        raise ValueError("Unexpected threshold configuration")
    domains = running["domains"]["domains"]
    keys = running["keyset"]["domains"]
    schemes = sorted({name for item in keys for name in item["key"]})
    return {
        "headline": "A shared signing network, visible on NEAR.",
        "summary": f"The signer reports {len(participants)} participant entries and a governance parameter "
                   f"threshold of {threshold}. Key types in the current keyset: {', '.join(schemes)}.",
        "metrics": [metric("Participant entries", len(participants)), metric("Parameter threshold", threshold),
                    metric("Configured domains", len(domains)), metric("Key types", len(schemes))],
        "rows": [{"Domain": d["id"], "Protocol": d["protocol"], "Purpose": d.get("purpose", "unspecified"),
                  "Reconstruction threshold": d.get("reconstruction_threshold", "not returned")} for d in domains],
        "supports": "A deployed NEAR contract exposes the participant configuration and multiple cryptographic domains.",
        "investment_link": "Shared signing infrastructure can let applications coordinate assets across chains without "
                           "building their own signing network from scratch.",
        "limits": "Reading configuration does not prove signatures can currently be produced, operator independence, "
                  "threshold security or foreign-chain execution. No signature or transaction was submitted.",
        "block_height": result["block_height"], "block_hash": result["block_hash"],
    }
