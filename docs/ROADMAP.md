# Roadmap e critérios de aceitação

| Marco | Entrega verificável | Critério mínimo |
|---|---|---|
| M1 | Scanner desktop + logs | Abre, escaneia fixtures sintéticas, reporta SHA-256, cancela, registra histórico, testes passam |
| M2 | Monitoramento + quarentena | Monitora apenas pastas permitidas, apresenta alertas, restaura arquivo sem perda após confirmação |
| M3 | Inteligência externa opcional | Mock e integração com licença habilitada; cache/quota e erros testados, sem upload automático |
| M4 | Ransomware e backup | Detecta cenários simulados, reduz falso alerta e restaura backups de teste |
| M5 | IA própria | Pipeline reprodutível, origem licenciada de dados, métricas publicadas, inferência local verificável |
| M6 | Eventos de IP/rede | Lê logs simulados e reais autorizados, correlaciona, não confunde IP com identidade |
| M7 | Adapters de SO + celular | Declara capacidades por SO; acesso móvel somente autenticado e pareado |
| M8 | Distribuição segura | Builds, assinatura quando possível, atualização verificada, auditoria, regressão e manuais |

## Diretrizes de teste
- Não usar malware real durante testes de desenvolvimento cotidiano; usar arquivos inofensivos sintéticos e registros simulados.
- Testar arquivos grandes, formatos corrompidos, diretórios enormes, arquivos bloqueados, links simbólicos, nomes unicode e concorrência.
- Reproduzir rate limit, timeout e falha de rede com mocks.
- Provar restauração da quarentena e recuperação do cofre a partir de backups de teste.
- Adicionar CI por Windows, Linux e macOS quando runners disponíveis. Reportar quando alguma plataforma não foi testada.
- Testes de dados de IA devem evitar vazamento entre conjuntos e medir falsos positivos em arquivos legítimos.

