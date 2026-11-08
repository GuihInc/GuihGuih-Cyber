import hashlib
import threading
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from guihguih_cyber.monitor import FolderMonitor
from guihguih_cyber.quarantine import Quarantine, QuarantineError
from guihguih_cyber.ransomware import ChangeBurstDetector
from guihguih_cyber.scanner import scan_path
from guihguih_cyber.storage import HistoryStore


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = HistoryStore(self.root / "history.sqlite3")

    def tearDown(self):
        self.tmp.cleanup()

    def test_preferences_use_default_and_persist_locally(self):
        self.assertEqual(self.store.get_preference("monitor_poll_interval", "2.0"), "2.0")
        self.store.set_preference("monitor_poll_interval", "5.0")
        self.assertEqual(self.store.get_preference("monitor_poll_interval", "2.0"), "5.0")

    def test_ransomware_heuristic_alerts_once_per_burst_and_resets(self):
        detector = ChangeBurstDetector(threshold=3, window_seconds=10)
        self.assertIsNone(detector.record_change("a", now=1))
        self.assertIsNone(detector.record_change("b", now=2))
        alert = detector.record_change("c", now=3)
        self.assertEqual(alert["event_count"], 3)
        self.assertIsNone(detector.record_change("d", now=4))
        self.assertIsNone(detector.record_change("e", now=20))
        self.assertIsNone(detector.record_change("f", now=21))
        next_alert = detector.record_change("g", now=22)
        self.assertEqual(next_alert["event_count"], 3)

    def test_ransomware_heuristic_counts_distinct_files_not_repeated_writes(self):
        detector = ChangeBurstDetector(threshold=2, window_seconds=10)
        self.assertIsNone(detector.record_change("same-file", now=1))
        self.assertIsNone(detector.record_change("same-file", now=2))
        alert = detector.record_change("another-file", now=3)
        self.assertEqual(alert["event_count"], 2)

    def test_ransomware_alert_is_persisted_without_file_paths(self):
        alert = {
            "created_at": "2026-11-08T12:00:00+00:00",
            "rule_id": "LOCAL-CHANGE-BURST",
            "event_count": 10,
            "window_seconds": 10.0,
        }
        self.store.save_security_alert(alert)
        rows = self.store.recent_security_alerts()
        self.assertEqual(rows[0]["rule_id"], "LOCAL-CHANGE-BURST")
        self.assertNotIn("path", rows[0])

    def test_quarantine_copy_and_restore_verified(self):
        source = self.root / "sample.txt"
        source.write_bytes(b"safe synthetic fixture")
        quarantine = Quarantine(self.store, self.root / "q")
        with self.assertRaises(QuarantineError):
            quarantine.quarantine_copy(source, confirmed=False)
        item = quarantine.quarantine_copy(source, confirmed=True)
        self.assertTrue(source.exists())
        restored = quarantine.restore_copy(item["id"], self.root / "restored.txt", confirmed=True)
        self.assertEqual(restored.read_bytes(), source.read_bytes())
        self.assertEqual(hashlib.sha256(restored.read_bytes()).hexdigest(), item["sha256"])

    def test_quarantine_refuses_overwrite(self):
        source = self.root / "sample.txt"
        source.write_bytes(b"x")
        quarantine = Quarantine(self.store, self.root / "q")
        item = quarantine.quarantine_copy(source, confirmed=True)
        destination = self.root / "existing.txt"
        destination.write_text("keep")
        with self.assertRaises(QuarantineError):
            quarantine.restore_copy(item["id"], destination, confirmed=True)
        self.assertEqual(destination.read_text(), "keep")

    def test_monitor_requires_explicit_folder_and_emits_change(self):
        events = []
        root = self.root / "watch"
        root.mkdir()
        monitor = FolderMonitor(lambda path: events.append(path), interval=.03)
        with self.assertRaises(ValueError):
            monitor.start()
        monitor.add_folder(root)
        monitor.start()
        try:
            time.sleep(.06)
            file = root / "changed.txt"
            file.write_text("first")
            time.sleep(.06)
            file.write_text("second")
            time.sleep(.12)
        finally:
            monitor.stop()
        self.assertTrue(any(event.resolve() == file.resolve() for event in events))

    def test_quarantine_refuses_symlink(self):
        source = self.root / "sample.txt"
        source.write_bytes(b"fixture")
        alias = self.root / "alias.txt"
        try:
            alias.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("symlink privilege unavailable")
        with self.assertRaises(QuarantineError):
            Quarantine(self.store, self.root / "q").quarantine_copy(alias, confirmed=True)

    def test_scanner_refuses_symlink_target(self):
        source = self.root / "source.txt"
        source.write_bytes(b"harmless")
        alias = self.root / "alias.txt"
        try:
            alias.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("symlink privilege unavailable")
        report = scan_path(alias)
        self.assertEqual(report["error_count"], 1)
        self.assertIsNone(report["files"][0]["sha256"])


if __name__ == "__main__":
    unittest.main()
