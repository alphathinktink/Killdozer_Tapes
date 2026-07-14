from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    missing: list[tuple[str, str, str]] = []
    for item in catalog:
        for key in ["audio", "txt", "vtt", "srt", "transcriptPage"]:
            if not (ROOT / item[key]).exists():
                missing.append((item["id"], key, item[key]))
        if not item["cues"]:
            raise AssertionError(f"{item['id']} has no timestamp cues")

    for path in [ROOT / "index.html", ROOT / "provenance.html", *sorted((ROOT / "transcripts").glob("*.html"))]:
        text = path.read_text(encoding="utf-8")
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
        if not blocks:
            raise AssertionError(f"{path.name} has no JSON-LD block")
        for block in blocks:
            json.loads(block)

    print(
        json.dumps(
            {
                "recordings": len(catalog),
                "missing": missing,
                "total_cues": sum(len(item["cues"]) for item in catalog),
                "total_words": sum(item["wordCount"] for item in catalog),
            },
            indent=2,
        )
    )
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
