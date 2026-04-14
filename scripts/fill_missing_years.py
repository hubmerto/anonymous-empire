#!/usr/bin/env python3
"""
Search Discogs for years of releases that are still missing them.
Uses broader search strategies for entries the first pass missed.
"""

import json
import os
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

DATA_DIR = Path(__file__).parent.parent / "data"
RELEASES_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")


def search_discogs(query, genre_filter=True):
    """Search Discogs, return year or 0."""
    genre = "&genre=Electronic" if genre_filter else ""
    url = (
        f"https://api.discogs.com/database/search?q={quote(query)}"
        f"&type=release{genre}&per_page=5"
    )
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={TOKEN}",
        "Accept": "application/json",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for r in data.get("results", []):
                year = r.get("year")
                if year:
                    return int(year)
    except Exception:
        pass
    return 0


def clean_title(title):
    """Remove slashes, volume markers, etc for cleaner search."""
    title = re.sub(r"\s*/\s*", " ", title)
    title = re.sub(r"\b(Pt|Vol|Ch)\.\s*\d+", "", title)
    title = re.sub(r"\b(Remixes?|Episode)\b", "", title, flags=re.IGNORECASE)
    return title.strip()


def main():
    with open(RELEASES_FILE) as f:
        data = json.load(f)

    missing = [r for r in data["releases"] if not r.get("year")]
    print(f"Missing years: {len(missing)}")

    found = 0
    for i, r in enumerate(missing):
        artist = r["artist"]
        title = clean_title(r["title"])
        label = r.get("label", "")

        # Strategy 1: artist + title (Electronic genre)
        year = search_discogs(f"{artist} {title}")
        time.sleep(1.05)

        # Strategy 2: artist + title (no genre filter)
        if not year:
            year = search_discogs(f"{artist} {title}", genre_filter=False)
            time.sleep(1.05)

        # Strategy 3: artist + label
        if not year and label and label != "Unknown":
            year = search_discogs(f"{artist} {label}")
            time.sleep(1.05)

        if year:
            r["year"] = year
            found += 1

        status = f"[{i+1}/{len(missing)}]"
        print(f"  {status} {artist} — {r['title']}  →  {year or '—'}")

        # Save every 25
        if (i + 1) % 25 == 0:
            _save(data)
            print(f"  --- Saved ({found} found so far) ---")

    _save(data)

    total_years = sum(1 for r in data["releases"] if r.get("year"))
    print(f"\nDone. Found {found} new years.")
    print(f"Total with year: {total_years}/{len(data['releases'])}")
    years = [r["year"] for r in data["releases"] if r.get("year")]
    if years:
        print(f"Range: {min(years)}-{max(years)}")


def _save(data):
    years = [r["year"] for r in data["releases"] if r.get("year")]
    data["meta"]["year_range"] = [min(years), max(years)] if years else [0, 0]
    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
