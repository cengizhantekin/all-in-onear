"""Six fixed dry quotes. Compare preview availability, not realized swaps or fees."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from .common import QUOTE_URL, TOKENS_URL, fetch_json, quote_preview, metric, now

ASSETS = {
    "near": "nep141:17208628f84f5d6ad33f0da3bbbeb27ffcb398eac501a31bd6ad2011e36133a1",
    "base": "nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near",
    "sol": "nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near",
    "eth": "nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near",
}
# Public documentation example addresses and a public contract, only for dry validation.
# They are NOT user wallets or destinations for sending funds.
PLACEHOLDERS = {
    "near": "intents.near",
    "base": "0x2527D02599Ba641c19FEa793cD0F167589a0f10D",
    "eth": "0x2527D02599Ba641c19FEa793cD0F167589a0f10D",
    "sol": "13QkxhNMrTPxoCkRdYdJ65tFuwXPhL5gLS2Z5Nr6gjRK",
}
ROUTES = (("near", "base"), ("base", "sol"), ("sol", "eth"))
AMOUNTS = (25, 250)  # USDC tokens, NOT an assumption that 1 USDC equals 1 USD.
POLICY = {"matrix_version": 1, "routes": [list(r) for r in ROUTES],
          "amounts_usdc": list(AMOUNTS), "decimals": 6, "slippage_bps": 100,
          "quote_wait_ms": 3000, "authentication": "none", "retries": 0,
          "address_policy": "public preview placeholders; never fund these addresses"}


def request_for(origin, destination, amount, deadline):
    if (origin, destination) not in ROUTES or type(amount) is not int or amount not in AMOUNTS:
        raise ValueError("Route/amount is not in the fixed matrix")
    return {"dry": True, "swapType": "EXACT_INPUT", "slippageTolerance": 100,
            "originAsset": ASSETS[origin], "destinationAsset": ASSETS[destination],
            "amount": str(amount * 10 ** 6), "depositType": "ORIGIN_CHAIN",
            "recipientType": "DESTINATION_CHAIN", "refundType": "ORIGIN_CHAIN",
            "recipient": PLACEHOLDERS[destination], "refundTo": PLACEHOLDERS[origin],
            "deadline": deadline, "quoteWaitingTimeMs": 3000}


def collect():
    started = now()
    catalog = fetch_json(TOKENS_URL)
    if not isinstance(catalog, list) or not catalog:
        raise ValueError("Expected a non-empty token catalog")
    pinned = {}
    for chain, asset_id in ASSETS.items():
        matches = [t for t in catalog if t.get("assetId") == asset_id]
        if len(matches) > 1:
            raise ValueError("Duplicate pinned asset ID")
        pinned[chain] = matches[0] if matches else None
        if matches and (matches[0].get("blockchain") != chain or matches[0].get("symbol") != "USDC"
                        or type(matches[0].get("decimals")) is not int or matches[0]["decimals"] != 6):
            raise ValueError("Pinned USDC metadata changed; review the matrix before requesting quotes")
    deadline = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cells = []
    for origin, destination in ROUTES:
        for amount in AMOUNTS:
            cell = {"origin": origin, "destination": destination, "input_usdc": amount}
            if pinned[origin] is None or pinned[destination] is None:
                cell["not_requested"] = "Pinned asset missing from live catalog"
            else:
                cell["observation"] = quote_preview(request_for(origin, destination, amount, deadline))
            cells.append(cell)
    return {"policy": POLICY, "started_at": started, "finished_at": now(),
            "catalog": {"endpoint": TOKENS_URL, "observed_at": started, "response": catalog},
            "deadline": deadline, "cells": cells}


def uint(value):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal() or len(value) > 80:
        raise ValueError("Expected a base-unit integer string")
    return int(value)


def format_usdc(value):
    # Integer arithmetic preserves every micro-USDC, including amounts above Decimal's context precision.
    units = uint(value)
    return f"{units // 10**6}.{units % 10**6:06d}"


def classify(observation, expected):
    """HTTP success alone is not a usable quote. Verify echoed scope and dry response."""
    if observation.get("endpoint") != QUOTE_URL or observation.get("request") != expected:
        raise ValueError("Quote request differs from the declared dry matrix")
    status = observation.get("http_status")
    data = observation.get("response")
    if status is None:
        return "Transport error", observation.get("transport_error", "No HTTP response"), None
    if type(status) is not int or not 100 <= status <= 599:
        raise ValueError("Invalid HTTP status in evidence")
    if not 200 <= status < 300:
        message = data.get("message") if isinstance(data, dict) else observation.get("response_error", "HTTP error")
        return "API error", f"HTTP {status}: {str(message)[:200]}", None
    if not isinstance(data, dict) or not isinstance(data.get("quote"), dict):
        return "Invalid response", "HTTP success without a quote object", None
    quote = data["quote"]
    if any(quote.get(key) for key in ("depositAddress", "chainDepositAddresses", "depositMemo")):
        return "Invalid response", "Deposit routing returned for a dry request; do not use this response", None
    echo = data.get("quoteRequest")
    if not isinstance(echo, dict) or any(echo.get(key) != expected[key] for key in
            ("dry", "swapType", "originAsset", "destinationAsset", "amount", "depositType", "recipientType", "refundType", "slippageTolerance")) or echo.get("dry") is not True:
        return "Invalid response", "Response does not match the requested preview", None
    try:
        if uint(quote.get("amountIn")) != int(expected["amount"]) or uint(quote.get("amountOut")) <= 0:
            raise ValueError("Quote amount mismatch")
        minimum = uint(quote.get("minAmountOut"))
        if minimum > uint(quote["amountOut"]):
            raise ValueError("Minimum exceeds quoted output")
        eta = quote.get("timeEstimate")
        if eta is not None and (type(eta) not in (float, int) or not Decimal(str(eta)).is_finite() or eta < 0):
            raise ValueError("Invalid time estimate")
    except (ValueError, TypeError):
        return "Invalid response", "Invalid or mismatched base-unit amounts / estimate", None
    return "Quoted", "Preview only; signature not verified", quote


def analyze(evidence):
    if evidence.get("policy") != POLICY:
        raise ValueError("Unsupported quote matrix policy")
    expected_cells = [(a, b, n) for a, b in ROUTES for n in AMOUNTS]
    cells = evidence["cells"]
    if not isinstance(cells, list) or [(c.get("origin"), c.get("destination"), c.get("input_usdc")) for c in cells] != expected_cells:
        raise ValueError("Incomplete, duplicated or reordered quote matrix")
    rows = []
    quoted = attempted = 0
    covered_routes = set()
    for cell in cells:
        origin, destination, amount = cell["origin"], cell["destination"], cell["input_usdc"]
        row = {"Route": f"{origin} → {destination}", "Input · USDC": amount,
               "Quoted output · USDC": "—", "Min output · USDC": "—",
               "API response · ms": "—", "Service ETA · s": "—"}
        if cell.get("not_requested"):
            status, detail, quote = "Not requested", cell["not_requested"], None
        else:
            attempted += 1
            observation = cell["observation"]
            status, detail, quote = classify(observation,
                request_for(origin, destination, amount, evidence["deadline"]))
            latency = observation["response_ms"]
            if type(latency) is not int or latency < 0:
                raise ValueError("Invalid response duration")
            row["API response · ms"] = latency
        if quote:
            quoted += 1
            covered_routes.add((origin, destination))
            row["Quoted output · USDC"] = format_usdc(quote["amountOut"])
            row["Min output · USDC"] = format_usdc(quote["minAmountOut"])
            row["Service ETA · s"] = quote.get("timeEstimate", "—")
        row.update(Status=status, Note=detail)
        rows.append(row)
    support = (f"One fixed integration returned usable preview structures for {len(covered_routes)} of the 3 selected routes."
               if quoted else "This capture returned no usable quotes. Its errors document availability for this matrix at the recorded time.")
    return {
        "headline": "One integration, measured route previews.",
        "summary": f"{quoted} of {len(cells)} planned cells returned matching dry quotes ({attempted} HTTP attempts). "
                   "Each route uses 25 and 250 USDC; every planned cell remains visible, including errors. "
                   "These are preview observations, not executed swaps.",
        "metrics": [metric("Planned cells", len(cells)), metric("Usable previews", quoted),
                    metric("Routes with a preview", len(covered_routes)), metric("Other cells", len(cells) - quoted)],
        "rows": rows, "supports": support,
        "investment_link": "Quotable routes add a concrete integration signal beyond asset listings: applications can request cross-chain outcomes through a shared interface. Sustained usage and token value capture still need separate evidence.",
        "limits": "One unauthenticated snapshot with one attempt per cell; not a reliability statistic or a market-wide liquidity survey. "
                  "API response time is measured; transfer time is the service's estimate, not measured settlement. "
                  "Output differences are not an isolated fee or slippage measurement. No deposit or swap was executed. "
                  "Quote signatures and provider authenticity are not independently verified; complete-stack superiority is not tested.",
        "matrix_version": 1, "dry_run": True, "attempted": attempted, "quoted": quoted,
    }
