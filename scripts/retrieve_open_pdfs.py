#!/usr/bin/env python3
"""Recupera apenas PDFs acadêmicos com licença explícita de compartilhamento.

Fontes de descoberta: OpenAlex e Unpaywall. A ausência de licença explícita
produz ``link_only``; nunca autoriza re-hospedagem.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS_PATH = ROOT / "data" / "referencias.json"
READINGS = ROOT / "leituras"
PDF_DIR = READINGS / "pdfs"
MANIFEST_JSON = READINGS / "manifest.json"
MANIFEST_CSV = READINGS / "manifest.csv"
WORK = Path(os.environ.get(
    "PDF_RETRIEVAL_WORK",
    "/home/hermes/.hermes/profiles/filosofo/work/bibliometria-cientometria-repositorio/pdf-work",
))
CACHE = WORK / "cache"
QUARANTINE = WORK / "quarantine"
USER_AGENT = "curso-bibliometria-pdf-audit/1.0 (mailto:leofn@ufba.br)"
OPEN_LICENSE_PREFIXES = (
    "cc-by", "cc0", "cc-by-sa", "cc-by-nc", "cc-by-nd",
    "cc-by-nc-sa", "cc-by-nc-nd", "public-domain",
)


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def words(text: str) -> set[str]:
    return {word for word in normalize(text).split() if len(word) > 2}


def slug(text: str, limit: int = 68) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", normalize(text)).strip("-")
    return value[:limit].rstrip("-")


def request(url: str, timeout: int = 35) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def request_json(url: str) -> dict:
    return json.loads(request(url).decode("utf-8"))


def get_with_retry(url: str, attempts: int = 3) -> tuple[dict | None, str]:
    last = ""
    for index in range(attempts):
        try:
            return request_json(url), ""
        except Exception as error:  # network/API errors become manifest evidence
            last = f"{type(error).__name__}: {error}"
            if index + 1 < attempts:
                time.sleep(1.5 * (index + 1))
    return None, last


def similarity(left: str, right: str) -> float:
    a, b = words(left), words(right)
    return len(a & b) / max(1, len(a | b))


def title_coverage(title: str, text: str) -> float:
    """Share of meaningful title words found in extracted PDF text."""
    expected = words(title)
    observed = words(text)
    return len(expected & observed) / max(1, len(expected))


def select_openalex_work(reference: dict, payload: dict | None) -> dict | None:
    if not payload:
        return None
    results = payload.get("results", [])
    if not results:
        return None
    if reference.get("doi"):
        return results[0]
    ranked = sorted(results, key=lambda item: similarity(reference["title"], item.get("title", "")), reverse=True)
    return ranked[0] if similarity(reference["title"], ranked[0].get("title", "")) >= 0.55 else None


def discover(reference: dict, refresh: bool = False) -> dict:
    cache_path = CACHE / f"{reference['id']}.json"
    if cache_path.exists() and not refresh:
        return json.loads(cache_path.read_text(encoding="utf-8"))

    doi = reference.get("doi", "")
    if doi:
        oa_query = urllib.parse.urlencode({"filter": f"doi:{doi}", "per-page": 1})
    else:
        oa_query = urllib.parse.urlencode({"search": reference["title"], "per-page": 5})
    oa_payload, oa_error = get_with_retry(f"https://api.openalex.org/works?{oa_query}")
    oa_work = select_openalex_work(reference, oa_payload)

    unpaywall = None
    up_error = ""
    if doi:
        encoded = urllib.parse.quote(doi, safe="")
        unpaywall, up_error = get_with_retry(
            f"https://api.unpaywall.org/v2/{encoded}?email=leofn%40ufba.br"
        )

    result = {
        "id": reference["id"],
        "openalex": oa_work,
        "unpaywall": unpaywall,
        "errors": [item for item in (oa_error, up_error) if item],
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def canonical_license(value: str | None) -> tuple[str, str]:
    if not value:
        return "", ""
    raw = value.strip()
    low = raw.lower().rstrip("/")
    if "creativecommons.org/licenses/" in low:
        part = low.split("creativecommons.org/licenses/", 1)[1].split("/", 1)[0]
        return f"CC {part.upper()}", raw
    if "creativecommons.org/publicdomain/zero" in low:
        return "CC0", raw
    if "creativecommons.org/publicdomain/mark" in low:
        return "Public Domain Mark", raw
    compact = low.replace("_", "-").replace(" ", "-")
    compact = compact.removeprefix("https://").removeprefix("http://")
    if any(compact.startswith(prefix) for prefix in OPEN_LICENSE_PREFIXES):
        if compact == "cc0":
            return "CC0", "https://creativecommons.org/publicdomain/zero/1.0/"
        if compact == "public-domain":
            return "Public Domain", ""
        return compact.upper(), f"https://creativecommons.org/licenses/{compact.removeprefix('cc-')}/4.0/"
    return raw, ""


def candidates(discovery: dict) -> list[dict]:
    output: list[dict] = []
    oa = discovery.get("openalex") or {}
    for location in oa.get("locations") or []:
        license_name, license_url = canonical_license(location.get("license"))
        output.append({
            "pdf_url": location.get("pdf_url") or "",
            "landing_url": location.get("landing_page_url") or "",
            "version": location.get("version") or "",
            "license_name": license_name,
            "license_url": license_url,
            "license_raw": location.get("license") or "",
            "source_type": f"OpenAlex:{(location.get('source') or {}).get('type') or (location.get('source') or {}).get('host_organization_name') or 'location'}",
            "license_evidence_url": location.get("landing_page_url") or oa.get("id", ""),
            "is_oa": bool(location.get("is_oa")),
        })

    up = discovery.get("unpaywall") or {}
    for location in up.get("oa_locations") or []:
        license_name, license_url = canonical_license(location.get("license"))
        output.append({
            "pdf_url": location.get("url_for_pdf") or "",
            "landing_url": location.get("url_for_landing_page") or "",
            "version": location.get("version") or "",
            "license_name": license_name,
            "license_url": license_url,
            "license_raw": location.get("license") or "",
            "source_type": f"Unpaywall:{location.get('host_type') or 'location'}",
            "license_evidence_url": location.get("url_for_landing_page") or up.get("doi_url", ""),
            "is_oa": True,
        })

    seen = set()
    deduped = []
    for item in output:
        key = item["pdf_url"] or item["landing_url"]
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    deduped.sort(key=lambda item: (
        not bool(item["license_url"] or normalize(item["license_name"]) in {"cc0", "public domain"}),
        not bool(item["pdf_url"]),
        item["source_type"],
    ))
    return deduped


def license_allows_sharing(candidate: dict) -> bool:
    name = normalize(candidate.get("license_name", "")).replace(" ", "-")
    url = (candidate.get("license_url") or "").lower()
    raw = (candidate.get("license_raw") or "").lower().replace("_", "-")
    return (
        name.startswith("cc-")
        or name in {"cc0", "public-domain", "public-domain-mark"}
        or raw.startswith(OPEN_LICENSE_PREFIXES)
        or "creativecommons.org/licenses/" in url
        or "creativecommons.org/publicdomain/" in url
    )


def first_author(reference: dict) -> str:
    first = re.split(r";| and ", reference.get("authors", ""))[0]
    if "," in first:
        return first.split(",", 1)[0]
    return first.split()[-1] if first.split() else "anon"


def pdf_metadata(path: Path, reference: dict) -> dict:
    data = path.read_bytes()
    result = {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic_ok": data.startswith(b"%PDF-"),
        "pages": 0,
        "sample_chars": 0,
        "identity_check": "failed",
        "identity_score": 0.0,
    }
    if not result["magic_ok"]:
        return result
    try:
        info = subprocess.run(
            ["pdfinfo", str(path)], capture_output=True, text=True, timeout=30, check=False
        )
        match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.MULTILINE)
        result["pages"] = int(match.group(1)) if match else 0
        text = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "3", str(path), "-"],
            capture_output=True, text=True, timeout=60, check=False,
        ).stdout
        result["sample_chars"] = len(text.strip())
        score = title_coverage(reference["title"], text[:30000])
        result["identity_score"] = round(score, 4)
        doi_ok = bool(reference.get("doi") and normalize(reference["doi"]) in normalize(text))
        author_ok = normalize(first_author(reference)) in normalize(text)
        title_ok = score >= 0.55
        if doi_ok or title_ok or (author_ok and score >= 0.35):
            result["identity_check"] = "passed"
        elif result["sample_chars"] < 80:
            result["identity_check"] = "needs_visual_check_or_ocr"
    except Exception as error:
        result["validation_error"] = f"{type(error).__name__}: {error}"
    return result


def download_candidate(url: str, target: Path) -> tuple[bool, str]:
    try:
        payload = request(url, timeout=90)
        if len(payload) > 99_000_000:
            return False, "arquivo excede o limite seguro de 99 MB"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return True, ""
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"


def inventory_record(reference: dict, discovery: dict, download: bool = True) -> dict:
    options = candidates(discovery)
    record = {
        "id": reference["id"],
        "title": reference["title"],
        "authors": reference.get("authors", ""),
        "year": reference.get("year", ""),
        "doi": reference.get("doi", ""),
        "reference_url": reference.get("url", ""),
        "decision": "not_found",
        "pdf_url": "",
        "landing_url": "",
        "version": "",
        "license_name": "",
        "license_url": "",
        "license_evidence_url": "",
        "source_type": "",
        "local_path": "",
        "bytes": 0,
        "pages": 0,
        "sha256": "",
        "identity_check": "not_checked",
        "notes": "; ".join(discovery.get("errors") or []),
        "candidate_count": len(options),
    }
    openly_accessible = [item for item in options if item.get("is_oa")]
    allowed = [item for item in options if license_allows_sharing(item)]
    allowed_with_pdf = [item for item in allowed if item.get("pdf_url")]

    if not options:
        oa = discovery.get("openalex") or {}
        up = discovery.get("unpaywall") or {}
        if oa or up:
            record["decision"] = "closed" if not oa.get("open_access", {}).get("is_oa") and not up.get("is_oa") else "link_only"
        return record

    preferred = allowed_with_pdf[0] if allowed_with_pdf else allowed[0] if allowed else openly_accessible[0] if openly_accessible else options[0]
    for field in ("pdf_url", "landing_url", "version", "license_name", "license_url", "license_evidence_url", "source_type"):
        record[field] = preferred.get(field, "")

    if not allowed:
        record["decision"] = "link_only" if openly_accessible else "closed"
        record["notes"] = (record["notes"] + "; " if record["notes"] else "") + "sem licença explícita de compartilhamento"
        return record
    if not allowed_with_pdf:
        record["decision"] = "link_only"
        record["notes"] = (record["notes"] + "; " if record["notes"] else "") + "licença aberta, mas URL direta de PDF não localizada"
        return record
    if not download:
        record["decision"] = "link_only"
        record["notes"] = "candidato elegível; download desativado"
        return record

    last_error = ""
    for candidate in allowed_with_pdf:
        filename = f"{reference['id']}_{slug(first_author(reference), 20)}_{reference['year']}_{slug(reference['title'])}.pdf"
        target = PDF_DIR / filename
        ok, error = download_candidate(candidate["pdf_url"], target)
        if not ok:
            last_error = error
            continue
        metadata = pdf_metadata(target, reference)
        if not metadata["magic_ok"] or metadata["pages"] < 1 or metadata["identity_check"] == "failed":
            QUARANTINE.mkdir(parents=True, exist_ok=True)
            quarantine = QUARANTINE / filename
            target.replace(quarantine)
            last_error = f"falha de identidade/integridade; movido para {quarantine}"
            continue
        record.update({field: candidate.get(field, "") for field in (
            "pdf_url", "landing_url", "version", "license_name", "license_url",
            "license_evidence_url", "source_type",
        )})
        record.update({
            "decision": "bundled",
            "local_path": str(target.relative_to(ROOT)),
            "bytes": metadata["bytes"],
            "pages": metadata["pages"],
            "sha256": metadata["sha256"],
            "identity_check": metadata["identity_check"],
            "sample_chars": metadata["sample_chars"],
            "identity_score": metadata["identity_score"],
        })
        return record
    record["decision"] = "link_only"
    record["notes"] = (record["notes"] + "; " if record["notes"] else "") + f"download/validação falhou: {last_error}"
    return record


def write_manifests(records: list[dict]) -> None:
    records.sort(key=lambda item: item["id"])
    READINGS.mkdir(parents=True, exist_ok=True)
    MANIFEST_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = [
        "id", "title", "authors", "year", "doi", "decision", "pdf_url", "landing_url",
        "version", "license_name", "license_url", "license_evidence_url", "source_type",
        "local_path", "bytes", "pages", "sha256", "identity_check", "candidate_count", "notes",
    ]
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="REF001")
    parser.add_argument("--end", default="REF120")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    references = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    selected = [ref for ref in references if args.start <= ref["id"] <= args.end]
    existing: dict[str, dict] = {}
    if MANIFEST_JSON.exists():
        existing = {item["id"]: item for item in json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))}

    discoveries: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(discover, ref, args.refresh): ref for ref in selected}
        for future in as_completed(futures):
            reference = futures[future]
            try:
                discoveries[reference["id"]] = future.result()
            except Exception as error:
                discoveries[reference["id"]] = {"id": reference["id"], "errors": [f"{type(error).__name__}: {error}"]}

    for index, reference in enumerate(selected, 1):
        record = inventory_record(reference, discoveries[reference["id"]], download=not args.no_download)
        existing[reference["id"]] = record
        write_manifests(list(existing.values()))
        print(f"[{index:03d}/{len(selected):03d}] {reference['id']} {record['decision']} {record.get('license_name', '')}")

    counts: dict[str, int] = {}
    for item in existing.values():
        counts[item["decision"]] = counts.get(item["decision"], 0) + 1
    total_bytes = sum(int(item.get("bytes") or 0) for item in existing.values())
    print(json.dumps({"processed": len(selected), "manifest_total": len(existing), "decisions": counts, "bundled_bytes": total_bytes}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
