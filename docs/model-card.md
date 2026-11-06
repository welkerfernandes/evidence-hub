# Modelo, evidência e limitações

BM25 com k1=1,2 e b=0,75, tokens Unicode normalizados, chunks de 120 palavras com overlap de 25. Score de ranking não é probabilidade nem confiança calibrada. Sem palavras em comum, o sistema se abstém.

## Uso pretendido

Demonstração técnica e avaliação controlada com dados sintéticos. A execução é local e determinística.
Não existem métricas de produção ou benchmarks de desempenho declarados.

## Avaliação disponível

A suíte verifica comportamentos esperados, cenários adversos e invariantes. Isso não demonstra
generalização estatística em dados reais. Antes de adoção, defina um dataset independente,
critérios de aceitação, avaliação por segmento e revisão humana dos erros.

## Limitações do produto

É a camada de recuperação de uma arquitetura RAG, com resposta extrativa; não há LLM, embeddings ou busca semântica. Uma correspondência lexical não comprova relevância ou veracidade. O corpus é carregado em memória por consulta, sem paginação; apropriado para demonstração pequena. Excluir um documento não equivale a apagar backups ou mídias físicas.
