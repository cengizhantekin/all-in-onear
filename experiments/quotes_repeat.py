"""Compare two captures of the same fixed, dry 1Click quote matrix."""
from datetime import datetime, timezone

from .common import metric
from .quotes import analyze as analyze_matrix, format_usdc


def capture(output):
    """Keep the original capture metadata and raw evidence from each round."""
    return {
        "captured_at": output["captured_at"],
        "source_sha256": output["captured_source_sha256"],
        "evidence_sha256": output["evidence_sha256"],
        "evidence": output["evidence"],
    }


def collect():
    from runner import run

    earlier = run("quotes", "replay")
    later = run("quotes", "live")
    return {"earlier": capture(earlier), "later": capture(later)}


def checked_matrix(snapshot):
    from runner import digest

    evidence = snapshot["evidence"]
    if digest(evidence) != snapshot["evidence_sha256"]:
        raise ValueError("Quote capture checksum mismatch")
    started = datetime.fromisoformat(evidence["started_at"])
    finished = datetime.fromisoformat(evidence["finished_at"])
    captured = datetime.fromisoformat(snapshot["captured_at"])
    if (any(value.utcoffset() is None for value in (started, finished, captured))
            or not started <= finished <= captured):
        raise ValueError("Quote capture timing is invalid")
    return started, finished, analyze_matrix(evidence)


def change(first, second):
    # The fixed matrix formats valid amounts as exact six-decimal USDC strings.
    delta = int(second.replace(".", "")) - int(first.replace(".", ""))
    sign = "+" if delta > 0 else "-" if delta < 0 else ""
    return sign + format_usdc(str(abs(delta)))


def analyze(evidence):
    first_time, first_end, first = checked_matrix(evidence["earlier"])
    second_time, _, second = checked_matrix(evidence["later"])
    if second_time <= first_end:
        raise ValueError("Compare two distinct, chronological quote captures")

    rows = []
    paired = 0
    for earlier, later in zip(first["rows"], second["rows"]):
        before = earlier["Quoted output · USDC"]
        after = later["Quoted output · USDC"]
        matched = earlier["Status"] == later["Status"] == "Quoted"
        paired += matched
        rows.append({
            "Route": earlier["Route"],
            "Input · USDC": earlier["Input · USDC"],
            "Earlier status": earlier["Status"],
            "Earlier output · USDC": before,
            "Later status": later["Status"],
            "Later output · USDC": after,
            "Change · USDC": change(before, after) if matched else "—",
            "Later error": "—" if later["Status"] == "Quoted" else later["Note"],
        })

    dates = [value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
             for value in (first_time, second_time)]
    return {
        "headline": "Repeat the same quotes at two different times.",
        "summary": f"{paired} of {len(rows)} route and amount pairs returned usable dry quotes in both rounds. "
                   f"The matrices started at {dates[0]} and {dates[1]}.",
        "metrics": [metric("Earlier usable previews", first["quoted"]),
                    metric("Later usable previews", second["quoted"]),
                    metric("Usable in both rounds", paired),
                    metric("Route and amount pairs", len(rows))],
        "rows": rows,
        "supports": "The paired rows show whether the same requests returned usable previews at two recorded times. "
                    "The output change is calculated only where both responses qualify.",
        "investment_link": "Repeated quotes help assess whether one interface can continue to surface cross-chain routes for a fixed workload.",
        "limits": "Two snapshots with one unauthenticated dry request per cell in each round. "
                  "The quote difference reflects the returned amounts at those times. "
                  "It does not isolate fees, measure executed swaps, or estimate uptime or repeat user demand. "
                  "Both raw captures and their response errors are included.",
        "earlier_started_at": first_time.isoformat(), "later_started_at": second_time.isoformat(),
        "dry_run": True,
    }
