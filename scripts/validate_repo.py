#!/usr/bin/env python3
"""Valida estrutura, dados e links Markdown internos do repositório."""
from __future__ import annotations
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "curso/README.md", "bibliografia/bibliografia-completa.md",
    "recursos/recursos-online.md", "data/referencias.json", "data/referencias.csv",
    "data/referencias.bib", "data/recursos.json", "data/recursos.csv",
    "GLOSSARIO.md", "AUTOAVALIACAO.md", "CONTRIBUTING.md", "CITATION.cff",
]


def fail(message, errors):
    errors.append(message)


def main():
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"arquivo obrigatório ausente: {rel}", errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    refs = json.loads((ROOT / "data/referencias.json").read_text(encoding="utf-8"))
    resources = json.loads((ROOT / "data/recursos.json").read_text(encoding="utf-8"))
    if len(refs) < 90:
        fail(f"poucas referências: {len(refs)}", errors)
    if len(resources.get("resources", [])) < 60:
        fail(f"poucos recursos: {len(resources.get('resources', []))}", errors)

    ids = [r.get("id") for r in refs]
    if len(ids) != len(set(ids)):
        fail("IDs de referência duplicados", errors)
    dois = [r.get("doi", "").lower() for r in refs if r.get("doi")]
    if len(dois) != len(set(dois)):
        fail("DOI duplicados", errors)
    titles = [re.sub(r"\W+", " ", r.get("title", "").lower()).strip() for r in refs]
    if len(titles) != len(set(titles)):
        fail("títulos normalizados duplicados", errors)
    for ref in refs:
        for field in ("id", "authors", "year", "title", "venue", "level", "pedagogical_function", "verification_source"):
            if not ref.get(field):
                fail(f"{ref.get('id', '?')}: campo ausente {field}", errors)
        if ref.get("doi") and not re.match(r"^10\.\d{4,9}/\S+$", ref["doi"], re.I):
            fail(f"{ref['id']}: DOI inválido {ref['doi']}", errors)

    with (ROOT / "data/referencias.csv").open(encoding="utf-8", newline="") as handle:
        csv_refs = list(csv.DictReader(handle))
    if len(csv_refs) != len(refs):
        fail(f"contagem CSV/JSON diverge: {len(csv_refs)} != {len(refs)}", errors)
    bib_count = len(re.findall(r"^@\w+\{", (ROOT / "data/referencias.bib").read_text(encoding="utf-8"), re.M))
    if bib_count != len(refs):
        fail(f"contagem BibTeX/JSON diverge: {bib_count} != {len(refs)}", errors)

    modules = sorted((ROOT / "curso").glob("[0-9][0-9]-*.md"))
    if len(modules) != 11:
        fail(f"esperados 11 arquivos de curso (orientação + 10 módulos), encontrados {len(modules)}", errors)
    for module in modules[1:]:
        text = module.read_text(encoding="utf-8")
        for heading in ("## Objetivos de aprendizagem", "## Leituras essenciais, nesta ordem", "## Perguntas de revisão", "## Avance quando"):
            if heading not in text:
                fail(f"{module.relative_to(ROOT)}: seção ausente {heading}", errors)

    link_re = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for md in ROOT.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if "	" in text:
            fail(f"tabulação em {md.relative_to(ROOT)}", errors)
        for raw in link_re.findall(text):
            target = raw.split()[0].strip("<>")
            parsed = urlparse(target)
            if parsed.scheme in ("http", "https", "mailto") or target.startswith("#"):
                continue
            clean = unquote(target.split("#", 1)[0])
            if not clean:
                continue
            resolved = (md.parent / clean).resolve()
            if not resolved.exists():
                fail(f"link interno quebrado em {md.relative_to(ROOT)}: {target}", errors)

    if errors:
        print("FALHOU")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: {len(refs)} referências, {len(resources['resources'])} recursos ativos, {len(resources['historical'])} históricos, {len(modules)-1} módulos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
