# Instruções do agente Codex — GuihGuih Cyber

## Missão
Desenvolva, teste e documente o **GuihGuih Cyber**, um produto defensivo de cibersegurança. Avance por marcos pequenos, funcionais e verificáveis. Nunca apresente como pronto algo que seja só interface, mock, TODO ou lógica experimental.

## Regras obrigatórias
1. Escopo: somente sistemas e redes próprios/autorizados. Nunca implementar rastreamento clandestino, exfiltração, phishing, execução remota arbitrária, exploração ofensiva ou interceptação de dados de terceiros.
2. Nenhuma ação destrutiva automática: quarentena reversível e bloqueio de rede somente por opt-in, com lista de permissões, confirmação, auditoria e opção de desfazer.
3. Preserve o antivírus nativo do sistema, especialmente Microsoft Defender; não tente desativá-lo ou criar exclusões automaticamente.
4. Sem integração de inteligência externa neste produto. Nunca transmitir hashes, arquivos, PII, documentos pessoais ou segredos a terceiros.
5. Não invente uma 'IA própria' funcional. Comece com regras explicáveis; desenvolva depois pipeline de dados licenciados, treinamento reprodutível, validação e assinaturas de modelos. A ausência do modelo deve falhar em modo seguro.
6. Nunca execute amostras de malware para escaneá-las; análise estática e parsing robusto primeiro. Testes apenas com fixtures sintéticas e inofensivas.
7. API local vinculada a loopback por padrão; painel no celular somente com pareamento explícito, autenticação forte, TLS e permissões mínimas.
8. Credenciais no cofre do SO; logs com minimização e retenção configurável; sem telemetria externa por padrão.
9. Qualquer funcionalidade específica de SO deve expor disponibilidade e requisitos. Não alegue bloqueio pré-execução quando só houver monitoramento reativo.
10. Execute testes e linters onde suportados. Documente comandos e limitações, e não alegue teste em SO que não está disponível.

## Tecnologias preferidas
- `core/`: Rust estável para motor, hash, varredura, quarentena e armazenamento seguro.
- `desktop/`: Tauri + React + TypeScript para interface Windows/Linux/macOS.
- `models/`: treinamento offline em Python, com inferência local ONNX quando modelo validado.
- `connectors/`: módulos opcionais de regras YARA-X, ClamAV e integrações com os SOs.
- `mobile/`: painel web responsivo/PWA **somente de visualização e ações autorizadas**, não software espião para celulares.
- `docs/` e `tests/`: especificações, auditoria, testes, critérios de aceitação.

Preferir dependências ativas, auditáveis, com versões fixadas. Toda permissão extra precisa de justificativa técnica.

## Ordem de entrega
1. M1 — aplicação desktop que inicia e mostra estado REAL, scanner local de arquivos, SHA-256, regras simples, histórico em SQLite, testes.
2. M2 — monitoramento de pastas com eventos locais, quarentena reversível, UI de gerenciamento, proteções contra symlinks e race conditions.
3. M3 — regras YARA-X/ClamAV opcionais com verificação de licença, limites e testes offline.
4. M4 — detecção de padrões de ransomware, backups versionados, notificações e recuperação testada.
5. M5 — pipeline de IA própria com dados licenciados, métricas de falsos positivos, inferência ONNX e fallback explicável.
6. M6 — eventos de rede e IPs de sistemas próprios/autorizados, consultas reputacionais, bloqueio opcional com rollback.
7. M7 — agentes nativos em cada plataforma, proteção mais profunda apenas quando suportada, painel móvel pareado.
8. M8 — assinatura, empacotamento, atualização assinada, acessibilidade, testes de estabilidade e segurança.

## Ao finalizar cada marco
Reportar arquivos alterados, funcionalidades reais, permissões necessárias, testes executados e resultados, limitações, riscos e plano para o próximo marco. Não pular fases sem autorização.

