#!/usr/bin/env python3
"""Resume tipos, anos, temas e níveis de um CSV de referências."""
import csv
import sys
from collections import Counter
from pathlib import Path


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/referencias.csv")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    print(f"Registros: {len(rows)}")
    for field in ("type", "theme", "level"):
        print(f"\n{field}:")
        for value, count in Counter(row.get(field, "") or "[vazio]" for row in rows).most_common():
            print(f"  {count:3d}  {value}")
    years = [int(row["year"][:4]) for row in rows if row.get("year", "")[:4].isdigit()]
    if years:
        print(f"\nPeríodo: {min(years)}–{max(years)}")


if __name__ == "__main__":
    main()
