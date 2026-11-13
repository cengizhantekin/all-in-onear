"""Build a review brief from a sample payment and a recorded Intents preview."""
import json
from pathlib import Path

from . import quotes
from .common import metric

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "payment_quote.json"
REQUEST = {
    "origin_asset": quotes.ASSETS["near"],
    "destination_asset": quotes.ASSETS["base"],
    "recipient": quotes.PLACEHOLDERS["base"],
    "input_units": "25000000",
}
POLICY = {
    "origin_asset": quotes.ASSETS["near"],
    "destination_asset": quotes.ASSETS["base"],
    "recipient": quotes.PLACEHOLDERS["base"],
    "maximum_input_units": "25000000",
    "minimum_output_units": "24700000",
}


def collect(parameters=None):
    if parameters:
        raise ValueError("The payment rehearsal uses fixed demonstration inputs")
    return {"request": REQUEST.copy(), "policy": POLICY.copy(),
            "archived_preview": json.loads(FIXTURE.read_text(encoding="utf-8"))}


def review(request, policy, preview_request, quote):
    if any(request[field] != policy[field] for field in ("origin_asset", "destination_asset")):
        return "Rejected · route outside policy"
    if request["recipient"] != policy["recipient"]:
        return "Rejected · recipient outside policy"
    if (request["origin_asset"], request["destination_asset"], request["recipient"]) != (
            preview_request["originAsset"], preview_request["destinationAsset"], preview_request["recipient"]):
        return "Rejected · route or recipient differs from recorded preview"
    if quotes.uint(request["input_units"]) > quotes.uint(policy["maximum_input_units"]):
        return "Rejected · spend cap exceeded"
    if request["input_units"] != preview_request["amount"]:
        return "Rejected · amount differs from recorded preview"
    if quotes.uint(quote["minAmountOut"]) < quotes.uint(policy["minimum_output_units"]):
        return "Rejected · preview minimum below policy"
    return "Ready for human review"


def analyze(evidence):
    request, policy = evidence["request"], evidence["policy"]
    archived = evidence["archived_preview"]
    observation = archived["observation"]
    expected = quotes.request_for("near", "base", 25, archived["deadline"])
    status, detail, quote = quotes.classify(observation, expected)
    if status != "Quoted":
        raise ValueError(f"Recorded preview is unusable: {detail}")
    if observation["response"]["quoteRequest"].get("recipient") != expected["recipient"]:
        raise ValueError("Recorded preview echoes a different recipient")

    changed_recipient = {**request, "recipient": "0x" + "1" * 40}
    over_cap = {**request, "input_units": "26000000"}
    weak_quote = {**quote, "minAmountOut": "24699999"}
    examples = [
        ("Sample supplier request", request, quote, "Ready for human review"),
        ("Change the recipient", changed_recipient, quote, "Rejected · recipient outside policy"),
        ("Spend 26 USDC", over_cap, quote, "Rejected · spend cap exceeded"),
        ("Lower the preview minimum below 24.70 USDC", request, weak_quote, "Rejected · preview minimum below policy"),
    ]
    rows = [
        {"Case": label, "Expected": expected_result, "Decision": review(sample, policy, expected, preview)}
        for label, sample, preview, expected_result in examples
    ]
    matched = sum(row["Decision"] == row["Expected"] for row in rows)
    output = quotes.format_usdc(quote["amountOut"])
    minimum = quotes.format_usdc(quote["minAmountOut"])
    return {
        "headline": "A cross-chain payment brief for human review.",
        "summary": f"The sample supplier request spends 25 USDC on NEAR. The recorded Base preview shows "
                   f"{output} USDC, with a preview minimum of {minimum} USDC. "
                   f"The local policy returned “{rows[0]['Decision']}”.",
        "metrics": [metric("Requested spend", "25", "USDC on NEAR"),
                    metric("Recorded preview", output, "USDC on Base"),
                    metric("Preview minimum", minimum, "USDC on Base"),
                    metric("Policy checks matched", f"{matched}/{len(rows)}")],
        "rows": rows,
        "quote_recorded_at": observation["finished_at"],
        "supports": "A single review brief can pair a recorded cross-chain quote with explicit rules for the destination asset, recipient, spending cap and minimum output.",
        "investment_link": "A common quoting interface gives payment applications a concrete place to add review rules. The related NEAR account, signing and confidential computing experiments cover other steps a product could integrate.",
        "limits": "This offline rehearsal uses a sample request, a public example address and an expired dry quote. It ends at human review and performs zero signatures or transfers. The TDX, Sandbox and Chain Signatures results come from separate experiments.",
    }
