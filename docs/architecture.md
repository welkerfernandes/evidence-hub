# ADR 001 — Escopo executável e consistência

Status: implementado.

## Contexto

Uma busca corporativa precisa citar documentos e impedir que uma empresa consulte a base de outra.

## Decisão

BM25 local oferece um baseline reproduzível e auditável sem credenciais de fornecedores. Filtragem por tenant ocorre antes do ranking. O sistema retorna trechos existentes, sem gerar alegações novas. Documentos são dados, nunca instruções executáveis.

## Alternativas e consequências

Um monólito modular reduz pontos de falha e mantém a demonstração reproduzível.
Microsserviços adicionariam rede, observabilidade distribuída e implantação sem necessidade comprovada.
SQLite reduz dependências, mas tem um escritor por vez. PostgreSQL é a evolução para concorrência sustentada.
A troca de banco exige revisão das transações e testes; não é apenas trocar a URL.

## Fronteiras de segurança

Credencial → identidade do tenant → caso de uso → SQL com filtro por tenant.
Não há header arbitrário de identidade. Credenciais locais existem somente para demonstração.
Documentação interativa e health são públicos; operações de negócio são autenticadas.

## Evolução

Adicionar avaliação rotulada com recall@k e MRR; PostgreSQL com RLS; índice híbrido lexical/vetorial; autorização por documento; adaptador de geração opcional que preserve citações e use testes de fidelidade.
