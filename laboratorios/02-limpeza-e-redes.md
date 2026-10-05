# Laboratório 02: limpeza, desambiguação e redes

**Objetivo:** transformar um corpus bruto em dados analisáveis sem apagar ambiguidades.

## Procedimento

1. Preserve o arquivo bruto como somente leitura.
2. Normalize espaços, Unicode e pontuação em campos auxiliares.
3. Deduplicate primeiro por DOI; depois examine título, ano e autoria.
4. Não una autores homônimos sem evidência adicional, como ORCID ou afiliação.
5. Crie uma tabela de autoria com `work_id`, `author_id`, `author_name` e `position`.
6. Projete a rede de coautoria e compare contagem completa e fracionária.

Você pode usar [OpenRefine](https://openrefine.org/) ou Python. Registre cada transformação reproduzível.

## Entregáveis

- dados brutos e processados separados;
- regras de deduplicação;
- tabela de decisões ambíguas;
- lista de arestas com peso completo e fracionário;
- interpretação que não confunda coautoria com toda forma de colaboração.
