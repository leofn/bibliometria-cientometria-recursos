# Esquema dos dados

## `referencias.json` e `referencias.csv`

Campos principais: identificador local, tipo, autoria, ano, título, veículo/editora, paginação, DOI, ISBN, URL, categoria original, tema didático, idioma, nível, papel de leitura, pré-requisitos, função pedagógica, nota e fonte de verificação.

## `recursos.json` e `recursos.csv`

Campos principais: nome, categoria, momento de uso, URL oficial, modalidade de acesso, descrição, status, data e fonte de verificação.

## Identidade e deduplicação

DOI normalizado é a chave preferencial. Na ausência de DOI, usa-se título normalizado para detectar duplicatas; conflitos exigem revisão humana.
