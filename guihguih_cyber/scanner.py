"""Streaming local scanner with SHA-256, bounded memory and cooperative cancellation."""

import hashlib
import os
import stat
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Event

from .detection import evaluate

CHUNK_SIZE = 1024 * 1024


def _scan_file(path: Path, cancel: Event | None = None) -> dict:
    digest = hashlib.sha256()
    matches: list[dict[str, str]] = []
    overlap = b""
    size = 0
    try:
        # Open without following a final symlink where the platform supports it.
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise OSError("O caminho não aponta para arquivo regular")
            while chunk := handle.read(CHUNK_SIZE):
                if cancel and cancel.is_set():
                    return {"path": str(path), "sha256": None, "size": size, "status": "cancelled", "findings": [], "error": None}
                size += len(chunk)
                digest.update(chunk)
                # Keep a small overlap so rules crossing chunk boundaries are detected.
                findings = evaluate(overlap + chunk, path.name)
                for finding in findings:
                    if finding not in matches:
                        matches.append(finding)
                overlap = (overlap + chunk)[-256:]
            after = os.fstat(handle.fileno())
            if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
                raise OSError("Arquivo alterado durante a leitura; hash descartado")
        return {"path": str(path), "sha256": digest.hexdigest(), "size": size, "status": "finding" if matches else "clean_by_rules", "findings": matches, "error": None}
    except OSError as exc:
        return {"path": str(path), "sha256": None, "size": size, "status": "error", "findings": [], "error": f"{type(exc).__name__}: {exc}"}


def scan_path(root: Path | str, cancel: Event | None = None, progress=None) -> dict:
    root = Path(root).expanduser().absolute()
    started = datetime.now(timezone.utc).isoformat()
    started_clock = time.monotonic()
    report = {"started_at": started, "root_path": str(root), "files": [], "files_scanned": 0, "finding_count": 0, "error_count": 0, "cancelled": False, "duration_seconds": 0.0}
    if not root.exists():
        report["error_count"] = 1
        report["files"].append({"path": str(root), "sha256": None, "size": 0, "status": "error", "findings": [], "error": "Caminho não encontrado"})
    else:
        candidates = [root] if root.is_file() or root.is_symlink() else None
        if root.is_symlink():
            report["error_count"] = 1
            report["files"].append({"path": str(root), "sha256": None, "size": 0, "status": "error", "findings": [], "error": "Symlink ignorado por segurança"})
            candidates = []
        iterator = iter(candidates) if candidates is not None else (p for base, _, names in os.walk(root, followlinks=False) for name in names if (p := Path(base) / name).is_file() and not p.is_symlink())
        for path in iterator:
            if cancel and cancel.is_set():
                report["cancelled"] = True
                break
            item = _scan_file(path, cancel)
            report["files"].append(item)
            if item["status"] == "cancelled":
                report["cancelled"] = True
                break
            report["files_scanned"] += item["status"] != "error"
            report["finding_count"] += len(item["findings"])
            report["error_count"] += item["status"] == "error"
            if progress:
                progress(report["files_scanned"], item)
    report["duration_seconds"] = time.monotonic() - started_clock
    return report

