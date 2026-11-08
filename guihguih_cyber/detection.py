"""Small, transparent local rules. These are demonstrations, not AV signatures."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    rule_id: str
    label: str
    explanation: str
    marker: bytes


RULES = (
    Rule("DEMO-EICAR", "Marcador de teste", "O arquivo contém o marcador EICAR de teste; isso não é malware.", b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"),
    Rule("SUSPICIOUS-PS-ENCODED", "Script potencialmente ofuscado", "Script PowerShell contém o parâmetro de codificação -EncodedCommand.", b"-encodedcommand"),
)


def evaluate(data: bytes, filename: str) -> list[dict[str, str]]:
    lowered = data.lower()
    findings = []
    for rule in RULES:
        if rule.marker.lower() in lowered:
            findings.append({"rule_id": rule.rule_id, "label": rule.label, "explanation": rule.explanation})
    if filename.lower().endswith((".ps1", ".psm1")) and b"-encodedcommand" in lowered:
        return findings
    return findings

