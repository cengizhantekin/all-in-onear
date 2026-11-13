"""Inspect one keyless direct-model TDX report and optionally verify its Intel chain."""
import asyncio
import hashlib
import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from .common import MAX_RESPONSE, metric, now

ENDPOINT = "https://glm-5-3-flash.completions.near.ai/v1/attestation/report"
MODEL = "z-ai/glm-5.3-flash"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Direct attestation report redirected")


def report_url(nonce):
    return ENDPOINT + "?" + urllib.parse.urlencode({
        "signing_algo": "ecdsa", "nonce": nonce, "include_tls_fingerprint": "true",
    })


def verifier():
    try:
        import dcap_qvl
    except ImportError:
        return None
    return dcap_qvl


async def collateral_for(qvl, quote):
    return await asyncio.wait_for(qvl.get_collateral(qvl.PHALA_PCCS_URL, quote), timeout=25)


def collect():
    endpoint = report_url(secrets.token_hex(32))
    request = urllib.request.Request(endpoint, headers={"Accept": "application/json",
                                                        "User-Agent": "NEAR-Evidence-Lab/0.13"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=18) as response:
            raw = response.read(MAX_RESPONSE + 1)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Direct attestation endpoint returned HTTP {error.code}") from None
    except OSError:
        raise RuntimeError("Direct attestation endpoint could not be reached") from None
    if len(raw) > MAX_RESPONSE:
        raise ValueError("Attestation exceeds the evidence size limit")
    report = json.loads(raw)
    evidence = {"report": {"endpoint": endpoint, "observed_at": now(), "response": report}}
    qvl = verifier()
    if qvl is not None:
        try:
            collateral = asyncio.run(collateral_for(qvl, bytes.fromhex(report["intel_quote"])))
        except (RuntimeError, TimeoutError, ValueError) as error:
            raise RuntimeError("Could not obtain Intel verification collateral; try recorded data") from error
        evidence["intel_collateral"] = json.loads(collateral.to_json())
    return evidence


def hex_bytes(value, length, label):
    if not isinstance(value, str) or len(value) != length * 2:
        raise ValueError(f"Invalid {label} length")
    data = bytes.fromhex(value)
    if len(data) != length:
        raise ValueError(f"Invalid {label} encoding")
    return data


def report_body(quote):
    # TDX 1.0 Quote v4 has a 48-byte header followed by a 584-byte TD report.
    if (len(quote) < 636 or quote[:2] != b"\x04\x00"
            or quote[2:4] != b"\x02\x00" or quote[4:8] != b"\x81\x00\x00\x00"):
        raise ValueError("Unsupported Intel TDX quote format")
    signed_size = int.from_bytes(quote[632:636], "little")
    if signed_size == 0 or 636 + signed_size > len(quote):
        raise ValueError("Truncated Intel quote signature")
    return quote[48:632]


def decoded_json(value):
    return json.loads(value) if isinstance(value, str) else value


def replay_rtmr3(log):
    rtmr = bytes(48)
    count = 0
    for entry in decoded_json(log):
        if entry["imr"] != 3:
            continue
        prefix = entry["event_type"].to_bytes(4, "little")
        material = prefix + b":" + entry["event"].encode("utf-8") + b":" + bytes.fromhex(entry.get("event_payload") or "")
        digest = hashlib.sha384(material).digest()
        if entry.get("digest") and hex_bytes(entry["digest"], 48, "event digest") != digest:
            raise ValueError("RTMR3 event digest mismatch")
        rtmr = hashlib.sha384(rtmr + digest).digest()
        count += 1
    if not count:
        raise ValueError("No RTMR3 events to replay")
    return rtmr, count


def verify_chain(quote, body, evidence, captured):
    if "intel_collateral" not in evidence:
        return "Not checked · no collateral", []
    qvl = verifier()
    if qvl is None:
        return "Not checked · optional verifier missing", []
    collateral = qvl.QuoteCollateralV3.from_json(json.dumps(evidence["intel_collateral"]))
    # In replay, appraise at the stored capture time. This is not a current status check.
    verdict = qvl.verify(quote, collateral, int(captured.timestamp()))
    report = json.loads(verdict.to_json())["report"]["TD10"]
    for field, expected in (("report_data", body[520:584]), ("mr_config_id", body[184:232]),
                            ("rt_mr3", body[472:520])):
        if hex_bytes(report[field], len(expected), field) != expected:
            raise ValueError("Verified quote fields differ from the local parse")
    return "Verified · " + verdict.status, list(verdict.advisory_ids)


def analyze(evidence):
    record = evidence["report"]
    captured = datetime.fromisoformat(record["observed_at"])
    if captured.utcoffset() is None:
        raise ValueError("Attestation capture time must include a timezone")
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(record["endpoint"]).query)
    nonce_hex, = params["nonce"]
    nonce = hex_bytes(nonce_hex, 32, "client nonce")
    if record["endpoint"] != report_url(nonce_hex):
        raise ValueError("Attestation request differs from the fixed direct-model request")
    report = record["response"]
    if report["model_name"] != MODEL or report["signing_algo"] != "ecdsa":
        raise ValueError("Unexpected model or signer scheme")
    quote = bytes.fromhex(report["intel_quote"])
    body = report_body(quote)
    reported_nonce = hex_bytes(report["request_nonce"], 32, "echoed nonce")
    binding = body[520:584]
    signer = hex_bytes(report["signing_address"].removeprefix("0x"), 20, "ECDSA signer")
    fingerprint = hex_bytes(report["tls_cert_fingerprint"], 32, "declared TLS fingerprint")
    expected_signer_binding = hashlib.sha256(signer + fingerprint).digest()
    if binding != expected_signer_binding + nonce or reported_nonce != nonce:
        raise ValueError("Nonce or signer/fingerprint binding does not match the quote")
    changed_nonce = bytes([nonce[0] ^ 1]) + nonce[1:]
    if binding == expected_signer_binding + changed_nonce:
        raise ValueError("Changed nonce was accepted")

    compose = decoded_json(report["info"]["tcb_info"])["app_compose"]
    config_id = b"\x01" + hashlib.sha256(compose.encode("utf-8")).digest() + bytes(15)
    rtmr, event_count = replay_rtmr3(report["event_log"])
    if body[184:232] != config_id or body[472:520] != rtmr:
        raise ValueError("Configuration or event log measurement differs from the quote")
    if int.from_bytes(body[120:128], "little") & 1:
        raise ValueError("The TDX debug flag is enabled")

    chain, advisories = verify_chain(quote, body, evidence, captured)
    return {
        "headline": "Inspect a direct model’s TDX attestation.",
        "summary": f"The {MODEL} report matches the client nonce, declared signer and certificate fingerprint, "
                   f"configuration hash, and {event_count} replayed runtime events. A changed nonce was rejected.",
        "metrics": [metric("Client nonce", "Matched"), metric("Changed nonce", "Rejected"),
                    metric("RTMR3 events replayed", event_count)],
        "rows": [
            {"Check": "Intel DCAP signature chain", "Result": chain},
            {"Check": "Client nonce in quote", "Result": "Matched"},
            {"Check": "Changed client nonce", "Result": "Rejected"},
            {"Check": "Signer and declared TLS fingerprint in quote", "Result": "Matched"},
            {"Check": "Configuration measurement (MRCONFIGID)", "Result": "Matched"},
            {"Check": "Runtime measurement (RTMR3)", "Result": "Matched"},
            {"Check": "TDX debug flag", "Result": "Disabled"},
        ],
        "supports": "A public direct-model report exposes measurements that an application can inspect and compare with a fresh challenge.",
        "investment_link": "Inspectable deployment evidence can help applications set explicit requirements for confidential compute.",
        "limits": "The structural checks compare fields in one saved report. Intel signature-chain verification requires "
                  "the optional dcap-qvl dependency and replays with the stored capture time. "
                  "The declared certificate fingerprint was checked inside the quote. "
                  "Peer certificate binding, GPU attestation, deployment policy, and any separate inference request are outside this experiment.",
        "model": MODEL, "intel_chain": chain, "intel_advisories": advisories,
    }
