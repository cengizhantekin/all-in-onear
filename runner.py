"""Run allowlisted experiments, record public evidence, replay identical inputs."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from catalog import TESTS
from experiments.common import now

ROOT = Path(__file__).resolve().parent
RECORDINGS = ROOT / "data" / "recordings"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_files(test_id):
    if test_id not in TESTS:
        raise ValueError("Unknown experiment")
    files = [f"experiments/{test_id}.py", "experiments/common.py", "runner.py", "catalog.py"]
    if TESTS[test_id]["mode"] == "sandbox":
        script = "access-keys.mjs" if test_id == "access" else "global-contracts.mjs"
        files[1:1] = [f"sandbox/{script}", "sandbox/permission-probe.wat",
                      "sandbox/download_binary.py", "sandbox/package.json", "sandbox/package-lock.json"]
    if test_id in ("quotes_repeat", "payment_rehearsal"):
        files.insert(1, "experiments/quotes.py")
    if test_id == "payment_rehearsal":
        files.insert(2, "data/fixtures/payment_quote.json")
    if test_id == "global_contracts":
        files.insert(1, "experiments/access.py")
    return files


def source_digest(test_id):
    return digest({name: (ROOT / name).read_text(encoding="utf-8") for name in source_files(test_id)})


IMPORTED_SOURCE_DIGESTS = {name: source_digest(name) for name in TESTS}


def run(test_id, mode="live", parameters=None, record=False):
    if test_id not in TESTS:
        raise ValueError("Unknown experiment")
    if source_digest(test_id) != IMPORTED_SOURCE_DIGESTS[test_id]:
        raise RuntimeError("Source changed since process startup. Restart the server before running changed code.")
    item = TESTS[test_id]
    module = item["module"]
    started = now()
    clock = time.perf_counter()
    if item["mode"] == "scenario":
        if mode != "scenario":
            raise ValueError("Scenarios must be explicitly run in scenario mode")
        evidence = module.collect(parameters)
        captured_at = None
        captured_source = None
    elif mode == "sandbox":
        if item["mode"] != "sandbox" or parameters:
            raise ValueError("Sandbox mode requires a local sandbox experiment with fixed inputs")
        evidence = module.collect()
        captured_at = now()
        captured_source = source_digest(test_id)
    elif mode == "live":
        if item["mode"] == "sandbox":
            raise ValueError("Choose sandbox or recorded sandbox explicitly for this local experiment")
        if parameters:
            raise ValueError("This observation accepts no user parameters")
        evidence = module.collect()
        captured_at = now()
        captured_source = source_digest(test_id)
    elif mode == "replay":
        if parameters:
            raise ValueError("Recorded observations accept no user parameters")
        path = RECORDINGS / f"{test_id}.json"
        if not path.exists():
            raise ValueError("No recorded observation available. Run a live capture first.")
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("experiment_id") != test_id or saved.get("schema_version") != 1:
            raise ValueError("Recording does not match this experiment/schema")
        expected_capture = "sandbox" if item["mode"] == "sandbox" else "live"
        if saved.get("capture_mode", "live") != expected_capture:
            raise ValueError("Recording environment does not match this experiment")
        evidence = saved["evidence"]
        if digest(evidence) != saved["evidence_sha256"]:
            raise ValueError("Recording checksum mismatch; do not use this evidence")
        captured_at = saved["captured_at"]
        captured_source = saved["source_sha256"]
    else:
        raise ValueError("Unsupported mode")
    result = module.analyze(evidence)
    output = {"schema_version": 1, "experiment_id": test_id, "mode": mode,
              "executed_at": started, "captured_at": captured_at,
              "duration_ms": round((time.perf_counter() - clock) * 1000),
              "source_sha256": source_digest(test_id), "captured_source_sha256": captured_source,
              "evidence_sha256": digest(evidence), "result": result, "evidence": evidence}
    if record:
        if mode not in ("live", "sandbox"):
            raise ValueError("Only fresh live observations or sandbox runs can be recorded")
        RECORDINGS.mkdir(parents=True, exist_ok=True)
        saved = {"schema_version": 1, "experiment_id": test_id, "capture_mode": mode, "captured_at": captured_at,
                 "source_sha256": output["source_sha256"], "evidence_sha256": output["evidence_sha256"],
                 "evidence": evidence}
        (RECORDINGS / f"{test_id}.json").write_text(json.dumps(saved, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=TESTS)
    parser.add_argument("--mode", choices=["live", "replay", "scenario", "sandbox"], required=True)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--parameters", default="{}", help="JSON object, scenario mode only")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.experiment, args.mode, json.loads(args.parameters), args.record), indent=2, ensure_ascii=False))
    except (ValueError, RuntimeError, KeyError, TypeError) as error:
        parser.exit(1, f"Experiment failed: {error}\n")
