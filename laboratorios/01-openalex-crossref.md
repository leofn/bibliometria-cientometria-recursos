# Laboratório 01: OpenAlex e Crossref

**Objetivo:** construir um corpus pequeno e documentar sua proveniência.

## Rota A: sem programação

1. Faça uma busca no [OpenAlex](https://openalex.org/).
2. Defina tema, período e tipo documental.
3. Exporte uma amostra permitida.
4. Para dez DOI, confira título, ano e autores na [Crossref REST API](https://api.crossref.org/works/SEU_DOI).

## Rota B: Python

Execute:

```bash
python exemplos/coleta_openalex.py "bibliometrics" --limit 25 --output dados/openalex-bibliometrics.csv
```

O script usa apenas a biblioteca padrão. Consulte os termos e as cotas atuais do OpenAlex antes de ampliar a coleta.

## Entregáveis

- consulta e data de coleta;
- CSV bruto, quando a licença permitir;
- dicionário de campos;
- nota sobre cobertura e registros ausentes;
- log com filtros e transformações.

## Auditoria

Escolha cinco registros e compare-os com a página do editor ou Crossref. Registre diferenças sem escolher silenciosamente a versão mais conveniente.
