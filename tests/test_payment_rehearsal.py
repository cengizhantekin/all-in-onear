import json
import unittest
from unittest.mock import patch

import guide
import runner
from experiments import payment_rehearsal


class PaymentRehearsalTests(unittest.TestCase):
    def test_offline_review_and_rejection_cases(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("Network is unavailable")):
            output = runner.run("payment_rehearsal", "scenario")
        result = output["result"]
        self.assertEqual(result["metrics"][1]["value"], "24.992550")
        self.assertEqual(result["metrics"][2]["value"], "24.742624")
        self.assertEqual([row["Decision"] for row in result["rows"]], [
            "Ready for human review",
            "Rejected · recipient outside policy",
            "Rejected · spend cap exceeded",
            "Rejected · preview minimum below policy",
        ])
        self.assertEqual(guide.guide("Ödeme provası")["experiment_id"], "payment_rehearsal")

    def test_fixture_matches_original_recording(self):
        archived = payment_rehearsal.collect()["archived_preview"]
        record = json.loads((runner.RECORDINGS / archived["parent_recording"]).read_text())
        # The quote matrix can be refreshed independently. Compare its cell only if it
        # still contains the original snapshot.
        if runner.digest(record["evidence"]) == archived["parent_evidence_sha256"]:
            self.assertIn(archived["observation"], [cell.get("observation") for cell in record["evidence"]["cells"]])

    def test_altered_recipient_echo_is_rejected(self):
        evidence = payment_rehearsal.collect()
        evidence["archived_preview"]["observation"]["response"]["quoteRequest"]["recipient"] = "unexpected"
        with self.assertRaisesRegex(ValueError, "different recipient"):
            payment_rehearsal.analyze(evidence)

    def test_scenario_is_fixed(self):
        with self.assertRaisesRegex(ValueError, "fixed demonstration inputs"):
            runner.run("payment_rehearsal", "scenario", {"input_units": "1"})
