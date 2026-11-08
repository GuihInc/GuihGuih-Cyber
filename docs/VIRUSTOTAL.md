# VirusTotal — integração e conformidade

Documentação oficial consultada em 2026-11-07:
- https://docs.virustotal.com/docs/api-overview
- https://docs.virustotal.com/docs/difference-public-private
- https://docs.virustotal.com/reference/getting-started
- https://docs.virustotal.com/reference/ip-info
- https://docs.virustotal.com/reference/files-scan

## Ponto de atenção contratual
A API **pública** é gratuita para uso não comercial/acadêmico, costuma ser limitada a **4 requisições/minuto** e **não pode** integrar um produto que substitua antivírus nem ser usada em produto comercial. Para distribuir GuihGuih Cyber com integração ao VirusTotal, verificar acordo/licença privada específica. Não assumir que uma chave pública autoriza o uso.

## Política técnica
- Conector **desabilitado por padrão** até haver licença e consentimento adequados.
- Consultas pertinentes, quando licenciadas: `GET /api/v3/files/{sha256}` e `GET /api/v3/ip_addresses/{ip}`.
- Nunca subir arquivos automaticamente; não submeter documentos pessoais, segredos ou PII.
- Como consultas de indicadores podem integrá-los ao conjunto de dados do serviço, filtrar IPs privados, URLs internas e indicadores sensíveis.
- Segredo na keychain do sistema operacional (ou variável de ambiente em DEV, jamais versionar).
- Cache, backoff em 429, timeouts, limites por minuto/dia, auditoria de consumo e opt-in explícito.
- Número de detecções de terceiros não é prova de malícia. Evitar rótulos absolutos; fornecer contexto e incerteza.
- Criar `MockThreatIntelProvider` para testes e desenvolvimento offline.

## Alternative offline
Se não houver licença, manter mecanismo local com regras YARA-X/ClamAV quando instalados, hashes públicos devidamente licenciados e modelos treinados/validados no projeto. Não copiar conteúdo proprietário ou burlar limites/termos.

