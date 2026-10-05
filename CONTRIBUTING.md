# Como contribuir

## Referências

Uma proposta deve informar:

- metadados completos;
- DOI ou URL primária;
- fonte de verificação;
- módulo e nível sugeridos;
- função pedagógica em uma frase;
- justificativa para inclusão como essencial ou complementar.

## Recursos on-line

Informe URL oficial, modalidade de acesso, categoria, status e data de verificação. Serviços encerrados pertencem à seção histórica.

## Critérios

- Não anexe PDFs protegidos.
- Não use ResearchGate ou mecanismos de busca como prova final quando existir versão de registro.
- Não trate manifestação, relatório ou preprint como artigo revisado por pares.
- Preserve diferenças entre ano online-first e ano do fascículo.
- Explique conflitos de metadados.

## Validação

Antes do pull request:

```bash
python scripts/validate_repo.py
python exemplos/resumo_corpus.py data/referencias.csv
```
