import hashlib
import threading
import tempfile
import unittest
from pathlib import Path

from guihguih_cyber.scanner import scan_path
from guihguih_cyber.storage import HistoryStore


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_scans_fixture_and_reports_sha256(self):
        sample = self.tmp_path / "note.txt"
        sample.write_bytes(b"harmless fixture")
        report = scan_path(sample)
        self.assertEqual(report["files_scanned"], 1)
        self.assertEqual(report["files"][0]["sha256"], hashlib.sha256(b"harmless fixture").hexdigest())
        self.assertEqual(report["finding_count"], 0)

    def test_synthetic_marker_rule_and_sqlite_history(self):
        sample = self.tmp_path / "synthetic.txt"
        sample.write_bytes(b"prefix EICAR-STANDARD-ANTIVIRUS-TEST-FILE suffix")
        report = scan_path(sample)
        self.assertEqual(report["files"][0]["findings"][0]["rule_id"], "DEMO-EICAR")
        store = HistoryStore(self.tmp_path / "history.sqlite3")
        scan_id = store.save_scan(report)
        self.assertEqual(store.recent_scans()[0]["id"], scan_id)
        self.assertEqual(store.recent_scans()[0]["findings"], 1)

    def test_scans_directory_and_reports_missing_path(self):
        (self.tmp_path / "a.txt").write_text("hello")
        (self.tmp_path / "b.txt").write_text("world")
        report = scan_path(self.tmp_path)
        self.assertEqual(report["files_scanned"], 2)
        missing = scan_path(self.tmp_path / "not-here")
        self.assertEqual(missing["error_count"], 1)

    def test_cooperative_cancel(self):
        for i in range(4): (self.tmp_path / f"{i}.txt").write_text("fixture")
        cancel = threading.Event(); cancel.set()
        report = scan_path(self.tmp_path, cancel)
        self.assertTrue(report["cancelled"])
        self.assertEqual(report["files_scanned"], 0)


if __name__ == "__main__":
    unittest.main()

