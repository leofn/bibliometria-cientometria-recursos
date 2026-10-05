#!/usr/bin/env python3
"""Coleta uma amostra pequena da API OpenAlex usando stdlib."""
import argparse
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--output", type=Path, default=Path("dados/openalex.csv"))
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit deve estar entre 1 e 100")
    params = urllib.parse.urlencode({"search": args.query, "per-page": args.limit})
    request = urllib.request.Request(
        "https://api.openalex.org/works?" + params,
        headers={"User-Agent": "curso-bibliometria/1.0 (mailto:SEU_EMAIL)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    rows = []
    for work in payload.get("results", []):
        rows.append({
            "openalex_id": work.get("id", ""),
            "doi": work.get("doi", ""),
            "title": work.get("display_name", ""),
            "year": work.get("publication_year", ""),
            "type": work.get("type", ""),
            "cited_by_count": work.get("cited_by_count", 0),
            "source": ((work.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["openalex_id", "doi", "title", "year", "type", "cited_by_count", "source"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} registros gravados em {args.output}")


if __name__ == "__main__":
    main()
