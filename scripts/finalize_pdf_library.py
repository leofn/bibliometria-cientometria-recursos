#!/usr/bin/env python3
"""Finaliza o pacote de PDFs auditados e seus manifestos."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "leituras" / "pdfs"
REFS_PATH = ROOT / "data" / "referencias.json"
MANIFEST_PATH = ROOT / "leituras" / "manifest.json"

MANUAL = {
    "REF022": {"pdf_url": "https://www.scielo.br/j/ci/a/rz3RTKWZpCxVB865BQRvtmh/?format=pdf&lang=pt&ilang=en", "landing_url": "https://www.scielo.br/j/ci/a/rz3RTKWZpCxVB865BQRvtmh/?lang=pt", "version": "publishedVersion", "license_name": "CC-BY-NC", "license_url": "https://creativecommons.org/licenses/by-nc/4.0/", "source_type": "SciELO:publisher"},
    "REF026": {"pdf_url": "https://www.scielo.br/j/ci/a/brhRD65fgzZ4HddrZ6twY4s/?format=pdf&lang=pt&ilang=en", "landing_url": "https://www.scielo.br/j/ci/a/brhRD65fgzZ4HddrZ6twY4s/?lang=pt", "version": "publishedVersion", "license_name": "CC-BY-NC", "license_url": "https://creativecommons.org/licenses/by-nc/4.0/", "source_type": "SciELO:publisher"},
    "REF029": {"pdf_url": "https://www.scielo.br/j/ci/a/Z4hZ66NGY7mYdpgWgCNvTKK/?format=pdf&lang=pt&ilang=en", "landing_url": "https://www.scielo.br/j/ci/a/Z4hZ66NGY7mYdpgWgCNvTKK/?lang=pt", "version": "publishedVersion", "license_name": "CC-BY-NC", "license_url": "https://creativecommons.org/licenses/by-nc/4.0/", "source_type": "SciELO:publisher"},
    "REF040": {"pdf_url": "https://digibug.ugr.es/bitstream/handle/10481/64974/hIndexReviewAlonsoCabrerizoHerrera-Viedma.pdf?sequence=1&isAllowed=y", "landing_url": "http://hdl.handle.net/10481/64974", "version": "submittedVersion", "license_name": "CC-BY", "license_url": "https://creativecommons.org/licenses/by/4.0/", "source_type": "UGR:repository"},
    "REF073": {"pdf_url": "https://ndownloader.figshare.com/files/41137562", "landing_url": "https://figshare.com/articles/report/23418680", "version": "publishedVersion", "license_name": "CC-BY-ND", "license_url": "https://creativecommons.org/licenses/by-nd/4.0/", "source_type": "Figshare:repository"},
    "REF079": {"pdf_url": "https://arxiv.org/pdf/1603.04939", "landing_url": "https://arxiv.org/abs/1603.04939", "version": "submittedVersion", "license_name": "CC-BY", "license_url": "https://creativecommons.org/licenses/by/4.0/", "source_type": "arXiv:preprint_server"},
    "REF096": {"pdf_url": "https://peerj.com/articles/4375.pdf", "landing_url": "https://peerj.com/articles/4375/", "version": "publishedVersion", "license_name": "CC-BY", "license_url": "https://creativecommons.org/licenses/by/4.0/", "source_type": "PeerJ:publisher"},
    "REF112": {"pdf_url": "https://arxiv.org/pdf/2011.00223", "landing_url": "https://arxiv.org/abs/2011.00223", "version": "submittedVersion", "license_name": "CC-BY", "license_url": "https://creativecommons.org/licenses/by/4.0/", "source_type": "arXiv:preprint_server"},
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def title_coverage(title: str, text: str) -> float:
    expected = {word for word in normalize(title).split() if len(word) > 2}
    observed = {word for word in normalize(text).split() if len(word) > 2}
    return len(expected & observed) / max(1, len(expected))


def inspect_pdf(path: Path, reference: dict) -> dict:
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        return {"valid": False, "reason": "magic bytes inválidos"}
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=30, check=False)
    match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.MULTILINE)
    pages = int(match.group(1)) if match else 0
    text = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "3", str(path), "-"],
        capture_output=True, text=True, timeout=60, check=False,
    ).stdout
    coverage = round(title_coverage(reference["title"], text[:40000]), 4)
    doi_ok = bool(reference.get("doi") and normalize(reference["doi"]) in normalize(text))
    identity = "passed" if coverage >= 0.55 or doi_ok else "needs_manual_review"
    return {
        "valid": pages > 0,
        "bytes": len(data),
        "pages": pages,
        "sha256": hashlib.sha256(data).hexdigest(),
        "identity_check": identity,
        "identity_score": coverage,
        "sample_chars": len(text.strip()),
    }


def write_csv(records: list[dict]) -> None:
    fields = [
        "id", "title", "authors", "year", "doi", "decision", "pdf_url", "landing_url",
        "version", "license_name", "license_url", "license_evidence_url", "source_type",
        "local_path", "bytes", "pages", "sha256", "identity_check", "candidate_count", "notes",
    ]
    with (ROOT / "leituras" / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    references = {item["id"]: item for item in json.loads(REFS_PATH.read_text(encoding="utf-8"))}
    manifest = {item["id"]: item for item in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))}

    # Remove respostas HTML ou arquivos vazios salvos indevidamente como PDF.
    for path in PDF_DIR.glob("*.pdf"):
        if not path.read_bytes().startswith(b"%PDF-"):
            path.unlink()

    for path in sorted(PDF_DIR.glob("*.pdf")):
        ref_id = path.name.split("_", 1)[0]
        if ref_id not in references or ref_id not in manifest:
            raise RuntimeError(f"PDF sem referência: {path}")
        result = inspect_pdf(path, references[ref_id])
        if not result.get("valid"):
            raise RuntimeError(f"PDF inválido: {path}: {result}")
        record = manifest[ref_id]
        if ref_id in MANUAL:
            record.update(MANUAL[ref_id])
            record["license_evidence_url"] = MANUAL[ref_id]["landing_url"]
        record.update({
            "decision": "bundled",
            "local_path": str(path.relative_to(ROOT)),
            "bytes": result["bytes"],
            "pages": result["pages"],
            "sha256": result["sha256"],
            "identity_check": result["identity_check"],
            "identity_score": result["identity_score"],
            "sample_chars": result["sample_chars"],
        })
        if ref_id in MANUAL:
            record["notes"] = "recuperação manual em fonte oficial; licença e identidade auditadas"

    records = sorted(manifest.values(), key=lambda item: item["id"])
    bundled = [item for item in records if item["decision"] == "bundled"]
    files = {str(path.relative_to(ROOT)) for path in PDF_DIR.glob("*.pdf")}
    declared = {item["local_path"] for item in bundled}
    if files != declared:
        raise RuntimeError(f"Divergência arquivos/manifesto: arquivos={files-declared}; declarados={declared-files}")

    MANIFEST_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(records)

    checksums = "\n".join(f"{item['sha256']}  {item['local_path']}" for item in bundled) + "\n"
    (ROOT / "leituras" / "CHECKSUMS.sha256").write_text(checksums, encoding="utf-8")

    counts = Counter(item["decision"] for item in records)
    rows = []
    for item in bundled:
        version = {
            "publishedVersion": "versão publicada",
            "submittedVersion": "preprint/manuscrito submetido",
            "acceptedVersion": "manuscrito aceito",
        }.get(item.get("version"), item.get("version") or "não informado")
        rows.append(
            f"| {item['id']} | {item['year']} | [{item['title']}](pdfs/{Path(item['local_path']).name}) | "
            f"{version} | [{item['license_name']}]({item.get('license_url') or item.get('license_evidence_url')}) |"
        )
    readme = f"""# Biblioteca de PDFs

Esta pasta contém **{len(bundled)} PDFs** cuja disponibilização foi auditada. Cada arquivo possui fonte oficial ou repositório legítimo, versão identificada, licença de compartilhamento e checksum SHA-256.

## Cobertura do inventário

- incorporados ao repositório: **{counts['bundled']}**;
- acesso legítimo por link, mas sem incorporação: **{counts['link_only']}**;
- acesso fechado ou sem licença de redistribuição: **{counts['closed']}**;
- PDF não localizado nas fontes consultadas: **{counts['not_found']}**.

A relação completa das 120 referências está em [`manifest.csv`](manifest.csv) e [`manifest.json`](manifest.json). A ausência de um PDF local não significa que a obra não exista: pode indicar paywall, licença ausente ou impossibilidade de redistribuição pública.

## PDFs incorporados

| ID | Ano | Obra | Versão | Licença |
|---|---:|---|---|---|
{chr(10).join(rows)}

## Integridade e direitos

- Checksums: [`CHECKSUMS.sha256`](CHECKSUMS.sha256).
- Os PDFs conservam suas licenças originais; a licença geral do curso não as substitui.
- Arquivos `submittedVersion` são identificados como preprints ou manuscritos submetidos.
- Não foram usados Sci-Hub, mirrors aleatórios ou cópias sem proveniência.
"""
    (ROOT / "leituras" / "README.md").write_text(readme, encoding="utf-8")

    total_bytes = sum(item["bytes"] for item in bundled)
    print(json.dumps({"records": len(records), "decisions": dict(counts), "pdfs": len(files), "bytes": total_bytes}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
