# Arquitetura-alvo — GuihGuih Cyber

```
                     GUI Tauri (Windows / Linux / macOS)
                                    |
                  IPC local autenticado, contratos tipados
                                    |
           +---------------- Motor Rust de segurança ----------------+
           |    Scanner     Regras/YARA-X     Quarentena             |
           |    SQLite      Vault AEAD        Eventos/auditoria      |
           |    ML ONNX*    Política          Fila/limites           |
           +------------------+------------------------------------+
                              |
                 Adaptadores específicos do sistema
                  Windows     Linux       macOS
                              |
            Logs, arquivos e conexões de sistemas próprios

      PWA celular opcional (TLS + pareamento + sem exposição pública)

* ML só depois de modelo treinado/validado; regras funcionam sem ele.
```

## Módulos sugeridos
- `crates/engine`: varredura streaming, SHA-256, resultados e orçamento de memória.
- `crates/detection`: assinaturas, regras e heurísticas com motivos.
- `crates/storage`: DB SQLite com migrações e proteção de dados sensíveis.
- `crates/quarantine`: movimentação segura, hash pós-ação, manifesto, restauração revisada.
- `crates/vault`: criptografia autenticada, derivação de chave e restauração.
- `crates/network`: eventos normalizados dos próprios serviços e equipamentos autorizados.
- Não há módulo de inteligência externa nesta versão; as detecções permanecem locais.
- `crates/platform`: interfaces com cada SO, capacidades declaradas em runtime.
- `apps/desktop`: Tauri/React/Ts, comunicação tipada e UI com estados verdadeiros.
- `apps/mobile-dashboard`: PWA pareado, futuro.
- `models/`: treinamento e avaliações da IA, futuro.

## Interfaces conceituais
- `ScanRequest(path, profile, time_budget)` → `ScanReport(files_count, findings, errors, duration)`
- `Finding(id, sha256, rule_id, severity, explanation, evidence, confidence)`
- `NetworkEvent(timestamp_utc, asset_id, source_ip, destination_service, type, evidence)`
- `QuarantineAction(id, finding_id, original_path, quarantine_path, state, rollback_id)`

Crie contratos reais e serialização tipada durante o desenvolvimento. Modelo de dados acima é ilustrativo.

