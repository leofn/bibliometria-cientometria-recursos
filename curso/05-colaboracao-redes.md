# 05. Colaboração científica e análise de redes

**Nível:** intermediário → avançado
**Tempo estimado:** 7 horas
**Pré-requisito:** Módulos 01 a 04; noções de nós, arestas e componentes.

## Objetivos de aprendizagem

- Distinguir colaboração social de coautoria observada.
- Construir redes com contagem completa e fracionária.
- Interpretar centralidade e comunidades sem reificar o grafo.

## Conceitos centrais

coautoria, rede bipartida, projeção, contagem fracionária, centralidade, comunidade.

## Sequência de estudo

1. Comece pela crítica conceitual de Katz e Martin.
2. Leia Newman como exemplo de modelagem de redes de colaboração.
3. Compare contagem completa e fracionária com Perianes-Rodriguez et al.
4. Estude o algoritmo Leiden somente depois de entender o que uma comunidade representa.

## Leituras essenciais, nesta ordem

- **[REF020]** Katz, J. Sylvan; Martin, Ben R. (1997). *What is research collaboration?*. Research Policy, 26(1), 1–18. [Acesso](https://doi.org/10.1016/s0048-7333(96)00917-1) — Problematiza o conceito de colaboração e o uso da coautoria como seu indicador; leitura essencial para não confundir vínculos bibliográficos e práticas colaborativas.
- **[REF024]** Newman, M. E. J. (2001). *The structure of scientific collaboration networks*. Proceedings of the National Academy of Sciences, 98(2), 404–409. [Acesso](https://doi.org/10.1073/pnas.98.2.404) — Modela redes de colaboração a partir da coautoria e analisa agrupamento, distribuição de colaboradores e distâncias entre pesquisadores em diferentes áreas.
- **[REF076]** Perianes-Rodriguez, Antonio; Waltman, Ludo; van Eck, Nees Jan (2016). *Constructing bibliometric networks: A comparison between full and fractional counting*. Journal of Informetrics, 10(4), 1178–1195. [Acesso](https://doi.org/10.1016/j.joi.2016.10.006) — Compara contagem completa e fracionária na construção de redes de coautoria, acoplamento e cocitação; demonstra que a ponderação pode alterar substantivamente os mapas.

## Leituras complementares

- **[REF016]** White, Howard D.; Griffith, Belver C. (1981). *Author cocitation: A literature measure of intellectual structure*. Journal of the American Society for Information Science, 32(3), 163–171. [Acesso](https://doi.org/10.1002/asi.4630320302) — Estabelece a cocitação de autores como unidade de análise para reconstruir estruturas intelectuais, grupos e proximidades entre pesquisadores.
- **[REF097]** Traag, V. A.; Waltman, L.; van Eck, N. J. (2019). *From Louvain to Leiden: guaranteeing well-connected communities*. Scientific Reports, 9(1), artigo 5233. [Acesso](https://doi.org/10.1038/s41598-019-41695-z) — Apresenta o algoritmo Leiden e suas garantias de conectividade das comunidades; fundamento para escolhas de agrupamento em redes científicas.
- **[REF070]** Waltman, Ludo; van Eck, Nees Jan (2015). *Field-normalized citation impact indicators and the choice of an appropriate counting method*. Journal of Informetrics, 9(4), 872–894. [Acesso](https://doi.org/10.1016/j.joi.2015.08.001) — Mostra a relação entre normalização por campo e atribuição de publicações coautoradas; examina os vieses associados à contagem completa e suas alternativas fracionárias.

## Atividade

Realize o [Laboratório 02](../laboratorios/02-limpeza-e-redes.md), construa uma rede de coautoria e compare os resultados de contagem completa e fracionária.

## Perguntas de revisão

1. O que uma aresta de coautoria prova, e o que ela apenas sugere?
2. Como a desambiguação de nomes afeta centralidades?
3. Por que comunidades algorítmicas não equivalem automaticamente a grupos sociais?

## Avance quando

- [ ] Consigo justificar nós, arestas, pesos e limiar.
- [ ] Minha interpretação menciona erros de desambiguação e efeitos de projeção.

## Próximo passo

Siga para [06. Mapeamento científico](06-mapeamento-cientifico.md).
