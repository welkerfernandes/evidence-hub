# PHP document ingestion bridge

Integra sistemas PHP legados ao pipeline de recuperação de conhecimento. Requer PHP 8.0+,
extensões curl e mbstring e Evidence Hub em execução.

```powershell
$env:EVIDENCE_KEY='local-alpha'
$env:EVIDENCE_URL='http://127.0.0.1:8102'
'{"title":"Reembolsos","content":"Solicitar em até 30 dias."}' | php integrations/php/ingest.php
php integrations/php/test.php
```

A ponte valida o documento, limita o payload, restringe destinos e transmite a credencial por header.
Deduplicação e isolamento continuam na API Python. O CLI não repete POST automaticamente.
Não é endpoint público nem crawler. Em produção, configure rede interna e autenticação adequada.
