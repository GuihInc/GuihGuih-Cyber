import unittest

from guihguih_cyber.ai import ENGINE_STATUS, MODEL_STATUS, analyze_scan_report, extract_static_features


class ExplainableTriageTests(unittest.TestCase):
    def test_scan_findings_are_explained_without_ml_verdict(self):
        result = analyze_scan_report({
            "files_scanned": 1,
            "finding_count": 1,
            "error_count": 0,
            "files": [{
                "status": "finding",
                "findings": [{"rule_id": "SUSPICIOUS-PS-ENCODED"}],
            }],
        })
        self.assertEqual(result["engine_status"], ENGINE_STATUS)
        self.assertEqual(result["model_status"], MODEL_STATUS)
        self.assertIsNone(result["classification"])
        self.assertEqual(result["observations"][0]["level"], "review")
        self.assertIn("Não execute", result["observations"][0]["action"])

    def test_eicar_test_marker_is_not_described_as_real_malware(self):
        result = analyze_scan_report({
            "files": [{"status": "finding", "findings": [{"rule_id": "DEMO-EICAR"}]}]
        })
        self.assertIn("inofensivo", result["observations"][0]["reason"])

    def test_no_findings_does_not_claim_file_is_safe(self):
        result = analyze_scan_report({"files_scanned": 1, "files": []})
        self.assertEqual(result["observations"], [])
        self.assertIn("não comprova", result["summary"])

    def test_scan_error_is_shown_as_incomplete(self):
        result = analyze_scan_report({
            "files": [{"status": "error", "error": "fixture error", "findings": []}]
        })
        self.assertEqual(result["observations"][0]["level"], "incomplete")
        self.assertEqual(result["observations"][0]["reason"], "fixture error")

    def test_metadata_feature_extraction_is_labeled_not_a_classification(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp:
            script = Path(temp) / "sample.ps1"
            script.write_text("Write-Output 'synthetic fixture'", encoding="utf-8")
            features = extract_static_features(script)
        self.assertTrue(features["is_script"])
        self.assertIsNone(features["classification"])
        self.assertEqual(features["model_status"], MODEL_STATUS)


if __name__ == "__main__":
    unittest.main()
