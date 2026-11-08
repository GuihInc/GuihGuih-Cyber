# Segurança, privacidade e limites

**Objetivo:** proteger apenas sistemas, redes, sites e serviços dos quais o operador é titular ou possui permissão explícita.

## Fora de escopo
- Localização ou identificação pessoal de indivíduos somente por IP.
- Captura de tráfego privado de terceiros, espionagem de celulares, keylogging, roubo de credenciais ou acesso clandestino.
- Malwares, backdoors, exploits ofensivos, controle remoto clandestino e exfiltração.
- Exclusão automática de arquivos, bloqueios irreversíveis e desativação de proteções existentes.

## Medidas obrigatórias
- Privilégios mínimos e permissões declaradas na UI.
- Configurações sensíveis armazenadas no serviço de chaves do SO.
- Logs minimizados, sanitizados e com prazos de retenção.
- Atualizações de modelos/regras com autenticidade criptográfica.
- Firewall e quarentena com revisão, lista de permissões, undo e trilha de auditoria.
- Nenhuma análise externa de arquivos ou indicadores privados sem consentimento explícito e base contratual apropriada.
- UI clara sobre estados: 'monitoramento de pastas' não significa 'bloqueio de malware antes da execução'.
- O sistema não deve interromper, substituir ou desabilitar antivírus nativo em versões iniciais.

## Notas por SO
- macOS: proteção avançada de execução via Endpoint Security requer entitlement `com.apple.developer.endpoint-security.client`, system extension e requisitos Apple.
- Linux: recursos fanotify podem exigir privilégios e têm limitações; implementar somente após revisão.
- Windows: interferir em mecanismos avançados de segurança e implementar drivers requer engenharia e testes especializados; não prometer substituto Defender com scanner em espaço de usuário.

