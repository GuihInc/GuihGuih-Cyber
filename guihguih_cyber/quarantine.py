"""Reversible, copy-based quarantine; the source is never removed automatically."""

import hashlib
import os
import shutil
import stat
import uuid
import errno
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from .storage import HistoryStore


class QuarantineError(RuntimeError):
    pass


class Quarantine:
    def __init__(self, store: HistoryStore, directory: Path | None = None):
        self.store = store
        self.directory = directory or store.path.parent / "quarantine"
        self.directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def items(self) -> list[dict]:
        db = self.store._connect()
        try:
            return [dict(row) for row in db.execute("SELECT * FROM quarantine ORDER BY created_at DESC")]
        finally:
            db.close()

    def quarantine_copy(self, source: Path | str, *, confirmed: bool) -> dict:
        if not confirmed:
            raise QuarantineError("Confirmação explícita necessária")
        source = Path(source).expanduser().absolute()
        try:
            source_info = source.lstat()
        except OSError as exc:
            raise QuarantineError(f"Origem indisponível: {exc}") from exc
        if not stat.S_ISREG(source_info.st_mode):
            raise QuarantineError("A origem precisa ser um arquivo regular, sem symlink")
        item_id = uuid.uuid4().hex
        destination = self.directory / f"{item_id}.quarantined"
        try:
            flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            source_fd = os.open(source, flags)
            source_digest = hashlib.sha256()
            with os.fdopen(source_fd, "rb") as src, destination.open("xb") as dst:
                before = os.fstat(src.fileno())
                if not stat.S_ISREG(before.st_mode):
                    raise QuarantineError("A origem deixou de ser arquivo regular")
                for block in iter(lambda: src.read(1024 * 1024), b""):
                    source_digest.update(block)
                    dst.write(block)
                after_fd = os.fstat(src.fileno())
                dst.flush(); os.fsync(dst.fileno())
            after_path = source.lstat()
            copied_hash = self._hash(destination)
            if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after_fd.st_dev, after_fd.st_ino, after_fd.st_size, after_fd.st_mtime_ns) or (before.st_dev, before.st_ino) != (after_path.st_dev, after_path.st_ino) or copied_hash != source_digest.hexdigest():
                destination.unlink(missing_ok=True)
                raise QuarantineError("O arquivo mudou durante a cópia; nenhuma ação aplicada")
            destination.chmod(stat.S_IRUSR | stat.S_IWUSR)
            row = {"id": item_id, "original_path": str(source), "stored_path": str(destination), "sha256": copied_hash, "created_at": datetime.now(timezone.utc).isoformat(), "state": "stored_copy"}
            db = self.store._connect()
            try:
                db.execute("INSERT INTO quarantine VALUES(?,?,?,?,?,?)", tuple(row.values())); db.commit()
            finally:
                db.close()
            return row
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    def restore_copy(self, item_id: str, destination: Path | str, *, confirmed: bool) -> Path:
        if not confirmed:
            raise QuarantineError("Confirmação explícita necessária")
        row = next((item for item in self.items() if item["id"] == item_id), None)
        if row is None or row["state"] != "stored_copy":
            raise QuarantineError("Item de quarentena não encontrado")
        source = Path(row["stored_path"])
        if self._hash(source) != row["sha256"]:
            raise QuarantineError("Hash da cópia não confere; restauração interrompida")
        target = Path(destination).expanduser().absolute()
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + f".{uuid.uuid4().hex}.tmp")
        try:
            shutil.copyfile(source, temporary)
            if self._hash(temporary) != row["sha256"]:
                raise QuarantineError("Hash da restauração não confere")
            # Hard-link publication is atomic and fails if another process created target.
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise QuarantineError("Destino já existe; escolha outro caminho para evitar sobrescrita") from exc
            except OSError as exc:
                if exc.errno == errno.EEXIST:
                    raise QuarantineError("Destino já existe; escolha outro caminho para evitar sobrescrita") from exc
                raise QuarantineError(f"O sistema de arquivos não permite restauração atômica segura: {exc}") from exc
            return target
        finally:
            temporary.unlink(missing_ok=True)

