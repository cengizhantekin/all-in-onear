"""Standard-library HTTP client. No signing, arbitrary URLs or shell execution."""
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

RPC_URL = "https://free.rpc.fastnear.com"
TOKENS_URL = "https://1click.chaindefuser.com/v0/tokens"
QUOTE_URL = "https://1click.chaindefuser.com/v0/quote"
ARCHIVE_RPC_URL = "https://archival-rpc.mainnet.near.org"
INTENTS_HISTORY_URLS = {
    "volume": "https://api.llama.fi/summary/dexs/near-intents?excludeTotalDataChartBreakdown=true",
    "fees": "https://api.llama.fi/summary/fees/near-intents?dataType=dailyFees&excludeTotalDataChartBreakdown=true",
    "revenue": "https://api.llama.fi/summary/fees/near-intents?dataType=dailyRevenue&excludeTotalDataChartBreakdown=true",
}
ALLOWED_URLS = {RPC_URL, TOKENS_URL, ARCHIVE_RPC_URL, *INTENTS_HISTORY_URLS.values()}
MAX_RESPONSE = 4_000_000


class NoQuoteRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Quote endpoint redirected; request was not forwarded")


def quote_preview(payload):
    """Fixed preview endpoint only. Keep HTTP errors as evidence, never retry a swap."""
    keys = {"dry", "swapType", "slippageTolerance", "originAsset", "destinationAsset",
            "amount", "depositType", "recipientType", "refundType", "quoteWaitingTimeMs",
            "recipient", "refundTo", "deadline"}
    if (not isinstance(payload, dict) or set(payload) != keys or payload.get("dry") is not True
            or payload.get("swapType") != "EXACT_INPUT"
            or payload.get("depositType") != "ORIGIN_CHAIN"
            or payload.get("recipientType") != "DESTINATION_CHAIN"
            or payload.get("refundType") != "ORIGIN_CHAIN"):
        raise ValueError("Only dry EXACT_INPUT previews are supported")
    request = urllib.request.Request(QUOTE_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "NEAR-Evidence-Lab/0.1"})
    record = {"endpoint": QUOTE_URL, "request": payload, "started_at": now()}
    started = time.perf_counter()
    try:
        opener = urllib.request.build_opener(NoQuoteRedirect())
        with opener.open(request, timeout=12) as response:
            raw = response.read(MAX_RESPONSE + 1)
            record["http_status"] = response.status
    except urllib.error.HTTPError as error:
        raw = error.read(MAX_RESPONSE + 1)
        record["http_status"] = error.code
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        record.update(http_status=None, transport_error=type(error).__name__)
        raw = b""
    record.update(finished_at=now(), response_ms=round((time.perf_counter() - started) * 1000))
    if len(raw) > MAX_RESPONSE:
        record["response_error"] = "Response exceeded the evidence size limit"
    elif raw:
        try:
            record["response"] = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            record["response_error"] = "Non-JSON response"
            record["body_excerpt"] = raw[:500].decode("utf-8", errors="replace")
    return record


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch_json(url, payload=None):
    if url not in ALLOWED_URLS:
        raise ValueError("Endpoint is not allowlisted")
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json", "User-Agent": "NEAR-Evidence-Lab/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            raw = response.read(MAX_RESPONSE + 1)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Public endpoint returned HTTP {error.code}; try recorded data.") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("Public endpoint could not be reached; try recorded data.") from None
    if len(raw) > MAX_RESPONSE:
        raise ValueError("Response exceeds the evidence size limit")
    return json.loads(raw)


def rpc(method, params):
    allowed = {"block", "EXPERIMENTAL_protocol_config", "query"}
    if method not in allowed:
        raise ValueError("Only read-only RPC methods are supported")
    if method == "query" and params.get("request_type") != "call_function":
        raise ValueError("Only view-function queries are supported")
    payload = {"jsonrpc": "2.0", "id": "near-evidence", "method": method, "params": params}
    response = fetch_json(RPC_URL, payload)
    if "error" in response:
        raise RuntimeError("RPC rejected the read-only request; inspect endpoint or retry later.")
    if "result" not in response:
        raise ValueError("RPC response has no result")
    return {"endpoint": RPC_URL, "request": payload, "response": response, "observed_at": now()}


def metric(label, value, unit=""):
    return {"label": label, "value": value, "unit": unit}
