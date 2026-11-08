# PROMPT PRINCIPAL PARA O CODEX — GUIHGUIH CYBER

Você é a equipe de engenharia do **GuihGuih Cyber**, um antivírus e sistema de defesa digital multiplataforma. Leia `AGENTS.md` e todos os arquivos em `docs/` antes de implementar.

## Visão
Construir um software sério e verificável para Windows, Linux e macOS, com interface profissional, proteção de arquivos, detecção de malware e comportamentos suspeitos, camada de IA própria, integração **opcional e devidamente licenciada** com VirusTotal, análise de eventos de rede e painel móvel autenticado.

Não quero só um design: cada botão da interface deve ter uma ação verdadeira. Não anuncie funcionalidades como concluídas sem teste e implementação.

## Plataforma e arquitetura
- Motor de segurança em Rust, voltado a análise local rápida e com segurança de memória.
- App desktop Tauri + React + TypeScript, responsivo e acessível, com tema escuro elegante azul/preto/verde.
- SQLite para configurações, histórico e registros; migrações versionadas.
- Separar scanner, detecção, quarentena, cofre criptográfico, rede, atualização e integrações externas em módulos testáveis.
- Camada `platform` com adapters para Windows/Linux/macOS; nunca fingir que uma API do SO está disponível nos demais.
- Treinamento da IA com Python, datasets licenciados e avaliações reprodutíveis; inferência ONNX local **apenas depois de um modelo realmente validado**.
- Integrações opcionais com YARA-X e ClamAV, com verificação de versões/licença e timeouts.
- Painel celular futuro (PWA): autenticação forte, pareamento explícito, TLS, mínimo de permissões, não expor porta na internet por padrão.

## Requisitos detalhados
1. **Scanner:** varredura rápida, completa e personalizada; SHA-256; tipos de arquivo; arquivos compactados com limites contra zip bombs; cache por hash/mtime; perfis de prioridade e limites de CPU/RAM; progresso, cancelamento e histórico.
2. **Proteção de arquivos:** monitoramento de diretórios configurados; avaliação de criação/alteração; quarentena reversível; não executar amostras; mecanismos para impedir troca de arquivos entre varredura e ação; logs e undo.
3. **Ransomware Guard:** detecção explicável de alterações rápidas e em massa, extensões incomuns e padrões de renomeação; alertas; proteção/backup versionado opt-in, teste de restauração; não prometer bloquear todos os ataques.
4. **GuihGuih AI:** motor híbrido com regras explicáveis e classificação local opcional. Criar pipeline de extração de features, datasets com proveniência, separação temporal entre treino e teste, FPR/FNR, precision/recall, curva PR, calibração, validação em ambientes distintos, versionamento e assinatura do modelo. Exibir motivo e nível de incerteza; IA não pode ser única razão para excluir arquivo.
5. **VirusTotal:** implementar interface adaptadora para API v3 com chave protegida, `GET /files/{sha256}` e, conforme licenciamento e consentimento, `GET /ip_addresses/{ip}` e domínio. Limitar chamadas, aplicar cache e mensagens de erro/quota. Sem envio automático de arquivos, URLs privadas ou IPs internos. A API pública não pode integrar um produto antivírus substituto ou comercial; manter conector DESABILITADO até licença apropriada; criar mock para testes.
6. **Hacker / Network Detection:** coletar somente logs dos próprios serviços, endpoints e firewalls autorizados; registrar IP de origem, horário UTC, protocolo/porta, sistema afetado e regra acionada; correlacionar eventos de força bruta, varredura e picos de tráfego; consulta reputacional opcional; filtros para IPs locais, NAT e VPN. Nunca afirmar identidade ou endereço residencial de pessoas a partir de um IP. Bloqueio só opt-in com revisão e reversão.
7. **Privacy Vault:** cofre local com AES-256-GCM (ou AEAD equivalente bem auditado), chave derivada por Argon2id com salt e parâmetros seguros, escrita atômica, permissões mínimas, mecanismo de backup e restauração. Não armazenar senha em texto puro; não inventar recuperação de chave impossível.
8. **Proteção do próprio app:** privilégios mínimos; entradas validadas; autenticação e autorização; assinaturas de regras/modelos/atualizações; logs sem segredos; retenção e exportação; tratamento de falhas; testes de path traversal, symlink e concorrência.
9. **UI:** resumo de proteção real (ativo, limitado, desligado), resultados de scan, ameaças, quarentena, eventos de rede, IA, cofre, configurações, logs e diagnósticos. Mostrar distintamente funcional, protótipo e futuro.
10. **Distribuição:** empacotamento e instaladores por SO, code-signing quando configurado, README e passos separados para Windows/Linux/macOS, sem assumir que foi testado em todos os SOs.

## Realidade de cada plataforma
- Windows: coexistir com Microsoft Defender; monitoramento de arquivos do usuário na primeira versão; bloqueio pré-execução exige projeto nativo específico e validação adicional.
- Linux: começar por monitoramento de diretórios; `fanotify` e recursos privilegiados apenas em fase posterior e sob análise de segurança.
- macOS: começo com monitoramento permitido e scanner manual; monitoramento/decisões de execução com Endpoint Security dependem de entitlement e system extension adequados.
- Celular: somente painel de administração, não alegar captura de tráfego ou IPs de outros celulares fora dos serviços protegidos.

## Ordem obrigatória
Implemente primeiro o **M1**: projeto que compila, UI inicial e scanner real de arquivos com SHA-256, banco SQLite e histórico, testes de código e fixtures sintéticas. Crie diretórios do monorepo, documentação, configuração de build, comandos de execução e CI básica.

Depois de executar testes disponíveis, reporte:
- arquivos criados;
- como iniciar no SO atual;
- demonstração funcional do scanner;
- testes realmente realizados e resultados;
- limitações atuais e atividades para M2.

Não desenvolva todas as etapas em uma única implementação superficial. Deixe o próximo marco preparado, mas NÃO apresente recursos inexistentes como implementados.

Leia também `docs/ROADMAP.md`, `docs/SECURITY.md`, `docs/ARCHITECTURE.md`, `docs/VIRUSTOTAL.md`.

