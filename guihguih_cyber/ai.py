"""GuihGuih AI scaffold: explicit feature extraction only, no trained model."""

from pathlib import Path


MODEL_STATUS = "experimental_unavailable"


def extract_static_features(path: Path | str) -> dict:
    path = Path(path)
    stat = path.stat()
    suffix = path.suffix.lower()
    return {"size_bytes": stat.st_size, "extension": suffix, "is_script": suffix in {".ps1", ".vbs", ".js", ".sh", ".bat"}, "model_status": MODEL_STATUS, "classification": None, "explanation": "Sem modelo treinado e validado; nenhuma classificação por IA foi realizada."}

