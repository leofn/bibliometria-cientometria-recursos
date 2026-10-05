#!/usr/bin/env python3
"""Valida a biblioteca local de PDFs contra o manifesto e checksums."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "leituras" / "manifest.json"
PDF_DIR = ROOT / "leituras" / "pdfs"


def main() -> int:
    records = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(records) != 120:
        raise SystemExit(f"esperadas 120 referências no manifesto; encontradas {len(records)}")
    bundled = [item for item in records if item.get("decision") == "bundled"]
    if not bundled:
        raise SystemExit("nenhum PDF incorporado")
    declared = set()
    for item in bundled:
        path = ROOT / item["local_path"]
        declared.add(path.resolve())
        if not path.is_file():
            raise SystemExit(f"arquivo ausente: {item['local_path']}")
        data = path.read_bytes()
        if not data.startswith(b"%PDF-"):
            raise SystemExit(f"magic bytes inválidos: {item['local_path']}")
        if len(data) != int(item["bytes"]):
            raise SystemExit(f"tamanho divergente: {item['local_path']}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != item["sha256"]:
            raise SystemExit(f"checksum divergente: {item['local_path']}")
        if int(item.get("pages") or 0) < 1:
            raise SystemExit(f"paginação inválida: {item['local_path']}")
        if not item.get("license_name") or not item.get("license_evidence_url"):
            raise SystemExit(f"licença sem evidência: {item['id']}")
    actual = {path.resolve() for path in PDF_DIR.glob("*.pdf")}
    if actual != declared:
        raise SystemExit(f"divergência entre diretório e manifesto: {len(actual)} != {len(declared)}")
    print(f"OK: {len(records)} referências auditadas; {len(bundled)} PDFs; {sum(int(x['bytes']) for x in bundled)} bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
