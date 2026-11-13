import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import runner
from experiments import assets, economics, network
from experiments.common import fetch_json, rpc


class EvidenceTests(unittest.TestCase):
    def test_recorded_observations_recompute(self):
        for name in ("network", "mpc", "assets", "quotes"):
            with self.subTest(name=name):
                output = runner.run(name, "replay")
                self.assertEqual(output["mode"], "replay")
                self.assertTrue(output["captured_at"])
                self.assertEqual(output["evidence_sha256"], runner.digest(output["evidence"]))
                self.assertGreater(len(output["result"]["metrics"]), 0)

    def test_replay_never_calls_live_network(self):
        with patch("experiments.common.fetch_json", side_effect=AssertionError("network should not be used")):
            for name in ("network", "mpc", "assets", "quotes"):
                runner.run(name, "replay")

    def test_corrupted_capture_is_rejected(self):
        source = runner.RECORDINGS / "network.json"
        capture = json.loads(source.read_text())
        capture["evidence"]["block"]["response"]["result"]["header"]["height"] += 1
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, "network.json").write_text(json.dumps(capture))
            with patch.object(runner, "RECORDINGS", Path(temp)):
                with self.assertRaisesRegex(ValueError, "checksum"):
                    runner.run("network", "replay")

    def test_buybacks_without_burn_do_not_reduce_supply(self):
        output = runner.run("economics", "scenario", {"burn_share": 0})["result"]
        metrics = {m["label"]: m["value"] for m in output["metrics"]}
        self.assertGreater(metrics["Tokens purchased"], 0)
        self.assertEqual(metrics["Tokens burned"], 0)
        self.assertEqual(metrics["Net modeled supply change"], economics.DEFAULTS["annual_issuance_near"])
        self.assertIsNone(output["break_even_annual_volume_usd"])

    def test_economic_break_even_matches_formula(self):
        parameters = {"annual_volume_usd": 1_000_000, "net_revenue_bps": 100,
                      "allocation": 1, "near_price_usd": 2,
                      "annual_issuance_near": 5000, "burn_share": 1}
        result = runner.run("economics", "scenario", parameters)["result"]
        self.assertEqual(result["break_even_annual_volume_usd"], 1_000_000)
        self.assertEqual(result["metrics"][-1]["value"], 0)

    def test_invalid_economic_inputs_rejected(self):
        for bad in ({"allocation": 2}, {"near_price_usd": 0}, {"annual_volume_usd": float("nan")},
                    {"burn_share": True}, {"unrecognized": 10}, {"annual_volume_usd": "123"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                runner.run("economics", "scenario", bad)

    def test_modes_and_module_paths_are_allowlisted(self):
        for name, mode in (("../server", "live"), ("economics", "live"), ("network", "scenario")):
            with self.subTest(name=name), self.assertRaises(ValueError):
                runner.run(name, mode)
        with self.assertRaises(ValueError):
            runner.source_files("../agent")

    def test_endpoints_and_rpc_methods_are_allowlisted(self):
        with self.assertRaises(ValueError):
            fetch_json("http://127.0.0.1:1/internal")
        with self.assertRaises(ValueError):
            rpc("broadcast_tx_commit", {})

    def test_duplicate_catalog_assets_rejected(self):
        token = {"assetId": "asset-a", "blockchain": "chain-a", "symbol": "A"}
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            assets.analyze({"catalog": {"response": [token, token]}})

    def test_mismatched_block_pin_rejected(self):
        evidence = json.loads((runner.RECORDINGS / "network.json").read_text())["evidence"]
        bad = copy.deepcopy(evidence)
        bad["config"]["request"]["params"]["block_id"] = "different-block"
        with self.assertRaisesRegex(ValueError, "pinned"):
            network.analyze(bad)


if __name__ == "__main__":
    unittest.main()
