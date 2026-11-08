"""Watch only user-selected directories. watchdog is optional; polling fallback is available."""

import threading
import time
from pathlib import Path


class FolderMonitor:
    def __init__(self, callback, interval: float = 2.0):
        self.callback = callback
        self.interval = interval
        self._roots: set[Path] = set()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def active(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def add_folder(self, path: Path | str) -> Path:
        root = Path(path).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Monitoramento aceita apenas pastas")
        self._roots.add(root)
        return root

    def start(self):
        if not self._roots:
            raise ValueError("Adicione ao menos uma pasta explicitamente")
        if self.active:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._poll, daemon=True, name="guih-folder-monitor")
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 1)

    def _poll(self):
        known: dict[Path, tuple[int, int]] = {}
        while not self._stop.is_set():
            for root in tuple(self._roots):
                try:
                    for path in root.rglob("*"):
                        if path.is_symlink() or not path.is_file():
                            continue
                        try:
                            st = path.stat(follow_symlinks=False)
                            stamp = (st.st_size, st.st_mtime_ns)
                        except OSError:
                            continue
                        if path not in known:
                            known[path] = stamp
                        elif known[path] != stamp:
                            known[path] = stamp
                            self.callback(path)
                except OSError:
                    continue
            self._stop.wait(self.interval)

