import hashlib
import threading
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from guihguih_cyber.monitor import FolderMonitor
from guihguih_cyber.quarantine import Quarantine, QuarantineError
from guihguih_cyber.scanner import scan_path
from guihguih_cyber.storage import HistoryStore


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = HistoryStore(self.root / "history.sqlite3")

    def tearDown(self):
        self.tmp.cleanup()

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
        self.assertIn(file, events)

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

