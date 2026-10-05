# Curso aberto de bibliometria e cientometria

[![Validar repositório](https://github.com/leofn/bibliometria-cientometria-recursos/actions/workflows/validate.yml/badge.svg)](https://github.com/leofn/bibliometria-cientometria-recursos/actions/workflows/validate.yml)

Repositório didático, em português, para aprender **bibliometria, cientometria, informetria, webometria e ciência da ciência** em sequência progressiva. Ele combina leitura conceitual, exercícios, laboratórios com dados abertos e uma biblioteca de consulta.

> Este não é um ranking de autores, revistas ou instituições. É um percurso para aprender a formular perguntas, construir corpora, interpretar indicadores e reconhecer seus limites.

## Comece aqui

1. Leia [Como usar este curso](curso/00-como-usar.md).
2. Percorra os dez módulos na ordem apresentada em [Trilha de aprendizagem](curso/README.md).
3. Faça os cinco [laboratórios](laboratorios/README.md).
4. Acesse a [biblioteca de PDFs auditados](leituras/README.md).
5. Consulte o [glossário](GLOSSARIO.md) e a [bibliografia completa](bibliografia/bibliografia-completa.md).
6. Encerre com o [projeto final](curso/10-projeto-final.md) e a [autoavaliação](AUTOAVALIACAO.md).

## O que você encontrará

- **10 módulos**, do nível introdutório ao avançado;
- **74 horas estimadas** de estudo e prática;
- **120 referências verificadas**, com DOI ou URL primária quando disponível;
- **28 PDFs redistribuíveis**, com versão, licença e checksum registrados;
- **71 recursos on-line ativos**, classificados por acesso e momento de uso;
- dados em **JSON, CSV e BibTeX**;
- laboratórios com **OpenAlex, Crossref, OpenRefine/Python, bibliometrix e VOSviewer**;
- uma trilha específica de literatura **brasileira e lusófona**.

## Princípios pedagógicos

1. **Pergunta antes da ferramenta.** O método responde a um problema substantivo.
2. **Dados antes do indicador.** Cobertura, limpeza e proveniência condicionam o resultado.
3. **Interpretação antes do ranking.** Contagem não equivale automaticamente a qualidade.
4. **Sequência curta, biblioteca ampla.** Cada módulo indica poucas leituras essenciais; a coleção completa serve para aprofundamento.
5. **Métricas responsáveis.** Indicadores apoiam, mas não substituem, julgamento contextualizado.
6. **Reprodutibilidade proporcional.** Toda decisão relevante deve ser registrada e auditável.

## Mapa do curso

| Módulo | Tema | Nível | Horas |
|---|---|---:|---:|
| [01. Conceitos, história e objetos de estudo](curso/01-conceitos-historia.md) | comunicação científica, bibliometria, cientometria | fundamentos | 5 |
| [02. Pergunta, corpus, fontes e qualidade dos dados](curso/02-pergunta-corpus-dados.md) | corpus, estratégia de busca, cobertura | fundamentos → intermediário | 7 |
| [03. Leis bibliométricas e distribuições](curso/03-leis-distribuicoes.md) | cauda longa, núcleo e dispersão, rank-frequência | intermediário | 5 |
| [04. Citações, impacto e indicadores](curso/04-citacoes-indicadores.md) | comportamento de citação, fator de impacto, índice h | intermediário | 7 |
| [05. Colaboração científica e análise de redes](curso/05-colaboracao-redes.md) | coautoria, rede bipartida, projeção | intermediário → avançado | 7 |
| [06. Mapeamento científico e estruturas do conhecimento](curso/06-mapeamento-cientifico.md) | acoplamento bibliográfico, cocitação, copalavras | avançado | 9 |
| [07. Webometria, altmetria e atenção on-line](curso/07-webometria-altmetria.md) | webometria, altmetria, evento de atenção | intermediário | 5 |
| [08. Cobertura, vieses e infraestruturas abertas](curso/08-cobertura-vieses-abertura.md) | viés de cobertura, multilinguismo, ciência aberta | intermediário → avançado | 7 |
| [09. Métricas responsáveis e reforma da avaliação](curso/09-metricas-responsaveis.md) | DORA, Leiden Manifesto, Metric Tide | intermediário → avançado | 7 |
| [10. Projeto final reproduzível](curso/10-projeto-final.md) | protocolo, proveniência, reprodutibilidade | avançado | 15 |

## Para docentes

O material pode ser usado como disciplina curta, grupo de leitura ou oficina. Cada módulo contém objetivos, sequência, atividade, questões de revisão e critérios de avanço. Consulte [Guia para docentes](DOCENTES.md).

## Dados e atualização

- [Referências em JSON](data/referencias.json), [CSV](data/referencias.csv) e [BibTeX](data/referencias.bib)
- [Recursos em JSON](data/recursos.json) e [CSV](data/recursos.csv)
- [Inventário de PDFs em JSON](leituras/manifest.json) e [CSV](leituras/manifest.csv)
- [Checksums SHA-256](leituras/CHECKSUMS.sha256)
- [Proveniência e limites](data/PROVENIENCIA.md)
- [Esquema dos dados](data/SCHEMA.md)

As referências foram verificadas em fontes editoriais, Crossref, OpenAlex, periódicos e repositórios. “Verificada” significa que os metadados foram conferidos, não que toda obra tenha sido lida integralmente. Uma bibliografia ampla jamais é universalmente completa.

## Contribua

Correções e inclusões são bem-vindas. Leia [CONTRIBUTING.md](CONTRIBUTING.md). Toda nova referência precisa de fonte verificável e função pedagógica explícita.

## Licenças

- textos didáticos: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/);
- dados bibliográficos produzidos neste repositório: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/);
- scripts: [MIT](https://opensource.org/license/mit/).

Consulte [LICENSE.md](LICENSE.md). Metadados e links não transferem direitos sobre as obras referenciadas; nenhum PDF protegido é redistribuído.
