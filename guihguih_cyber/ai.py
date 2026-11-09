"""Local, explainable scan triage; not a trained or generative AI model."""

from pathlib import Path
from typing import Any


MODEL_STATUS = "experimental_unavailable"
ENGINE_STATUS = "local_rules_only"
SCRIPT_EXTENSIONS = {".ps1", ".psm1", ".vbs", ".js", ".sh", ".bat", ".cmd"}


def extract_static_features(path: Path | str) -> dict[str, Any]:
    """Return basic metadata only; this function does not execute or classify files."""
    file_path = Path(path)
    stat = file_path.stat()
    suffix = file_path.suffix.lower()
    return {
        "size_bytes": stat.st_size,
        "extension": suffix,
        "is_script": suffix in SCRIPT_EXTENSIONS,
        "model_status": MODEL_STATUS,
        "classification": None,
        "explanation": "Metadados estáticos coletados; nenhum modelo treinado e validado realizou classificação.",
    }


def analyze_scan_report(report: dict[str, Any]) -> dict[str, Any]:
    """Build a privacy-preserving, explainable summary from an existing local scan report.

    This is deterministic triage over scanner findings, not ML or threat verdicts.
    It never opens files, contacts a service, or recommends automatic deletion.
    """
    files = report.get("files", [])
    if not isinstance(files, list):
        raise ValueError("Relatório de verificação inválido: 'files' deve ser uma lista")

    observations: list[dict[str, str]] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        status = item.get("status")
        findings = item.get("findings", [])
        if not isinstance(findings, list):
            findings = []
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            rule_id = str(finding.get("rule_id", "REGRA-LOCAL"))
            if rule_id == "DEMO-EICAR":
                observations.append({
                    "level": "info",
                    "title": "Marcador de teste EICAR",
                    "reason": "A regra encontrou um marcador de teste inofensivo; isso não indica malware real.",
                    "action": "Se foi criado para teste, remova-o manualmente quando não precisar mais.",
                })
            elif rule_id == "SUSPICIOUS-PS-ENCODED":
                observations.append({
                    "level": "review",
                    "title": "Comando PowerShell codificado",
                    "reason": "A regra local encontrou -EncodedCommand, que pode ocultar o conteúdo de um script.",
                    "action": "Não execute até revisar a origem e o conteúdo com uma ferramenta confiável.",
                })
            else:
                observations.append({
                    "level": "review",
                    "title": f"Regra local acionada: {rule_id}",
                    "reason": str(finding.get("explanation", "O scanner sinalizou este item.")),
                    "action": "Revise o resultado antes de abrir ou mover o arquivo.",
                })
        if status == "error":
            observations.append({
                "level": "incomplete",
                "title": "Arquivo não analisado completamente",
                "reason": str(item.get("error") or "O scanner encontrou um erro."),
                "action": "Feche o aplicativo que está usando o arquivo e tente verificá-lo novamente.",
            })

    return {
        "engine_status": ENGINE_STATUS,
        "model_status": MODEL_STATUS,
        "classification": None,
        "files_scanned": int(report.get("files_scanned", 0)),
        "finding_count": int(report.get("finding_count", 0)),
        "error_count": int(report.get("error_count", 0)),
        "cancelled": bool(report.get("cancelled", False)),
        "observations": observations,
        "summary": (
            "Triagem local explicável concluída. Nenhum modelo de IA classificou os arquivos. "
            "Ausência de regras acionadas não comprova que os arquivos são seguros."
        ),
    }
