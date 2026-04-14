#!/usr/bin/env python3
"""
Enrich releases.json with year + country from Discogs API.
- Searches each release on Discogs to get year
- For solo artists: country = artist origin
- For "Various": country = release country
- Saves checkpoint every 50 releases
"""

import json
import os
import time
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

DATA_DIR = Path(__file__).parent.parent / "data"
RELEASES_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")
CHECKPOINT_FILE = DATA_DIR / "enrich_checkpoint.json"

# Map scene names to proper country labels
SCENE_TO_COUNTRY = {
    "Detroit": "US",
    "Chicago": "US",
    "New York": "US",
    "Berlin": "Germany",
    "Frankfurt": "Germany",
    "Hamburg": "Germany",
    "Munich": "Germany",
    "Germany": "Germany",
    "Chemnitz / Dresden": "Germany",
    "London": "UK",
    "Sheffield / Leeds": "UK",
    "Manchester": "UK",
    "Netherlands": "Netherlands",
    "Ghent / Brussels": "Belgium",
    "Italy": "Italy",
    "Spain": "Spain",
    "France": "France",
    "Sweden": "Sweden",
    "Scandinavia": "Scandinavia",
    "Japan": "Japan",
    "Canada": "Canada",
    "Georgia / Eastern Europe": "Georgia",
    "Cologne": "Germany",
}


def discogs_search(artist, title):
    """Search Discogs for a release. Returns (year, country) or (0, '')."""
    # Clean artist name for search
    query = f"{artist} {title}"
    # Remove slashes and extra info
    query = re.sub(r"\s*/\s*", " ", query)
    query = re.sub(r"\b(Pt|Vol|Ch)\.\s*\d+", "", query)
    query = query.strip()

    url = (
        f"https://api.discogs.com/database/search?q={quote(query)}"
        f"&type=release&genre=Electronic&per_page=5"
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
            results = data.get("results", [])
            for r in results:
                year = r.get("year")
                country = r.get("country", "")
                rt = (r.get("title") or "").lower()
                # Basic validation: artist name should appear in result
                artist_first = artist.split()[0].lower() if artist.split() else ""
                if artist_first and artist_first in rt:
                    return int(year) if year else 0, country
            # Fallback: return first result if any
            if results:
                r = results[0]
                return int(r.get("year", 0) or 0), r.get("country", "")
    except Exception as e:
        print(f"    Error: {e}")
    return 0, ""


def main():
    with open(RELEASES_FILE) as f:
        data = json.load(f)

    # Load checkpoint if exists
    done = {}
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            done = json.load(f)
        print(f"Resuming from checkpoint: {len(done)} already done")

    releases = data["releases"]
    total = len(releases)
    found_year = 0
    found_country = 0

    for i, r in enumerate(releases):
        rid = str(r["id"])

        # Skip if already enriched from checkpoint
        if rid in done:
            r["year"] = done[rid].get("year", r.get("year", 0))
            if "country" not in r or not r.get("country"):
                r["country"] = done[rid].get("country", "")
            found_year += 1 if r["year"] else 0
            found_country += 1 if r.get("country") else 0
            continue

        artist = r["artist"]
        title = r["title"]

        # Search Discogs
        year, discogs_country = discogs_search(artist, title)
        time.sleep(1.05)  # Rate limit

        r["year"] = year

        # Country logic:
        # For "Various" artists → use Discogs release country
        # For named artists → use scene-based origin, fallback to Discogs
        if artist.lower() == "various":
            r["country"] = discogs_country or SCENE_TO_COUNTRY.get(r.get("scene", ""), "")
        else:
            scene = r.get("scene", "")
            r["country"] = SCENE_TO_COUNTRY.get(scene, discogs_country or "")

        done[rid] = {"year": r["year"], "country": r.get("country", "")}

        status = f"[{i+1}/{total}]"
        yr = r["year"] if r["year"] else "—"
        co = r.get("country", "—") or "—"
        print(f"  {status} {artist} — {title}  →  {yr}, {co}")

        found_year += 1 if r["year"] else 0
        found_country += 1 if r.get("country") else 0

        # Checkpoint
        if (i + 1) % 50 == 0:
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump(done, f)
            _save(data)
            print(f"  --- Checkpoint saved ({i+1}/{total}) ---")

    # Final save
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(done, f)
    _save(data)

    print(f"\nDone: {total} releases")
    print(f"Years found: {found_year}/{total}")
    print(f"Countries assigned: {found_country}/{total}")

    years = [r["year"] for r in releases if r["year"]]
    if years:
        print(f"Year range: {min(years)}–{max(years)}")


def _save(data):
    releases = data["releases"]
    years = [r["year"] for r in releases if r["year"]]
    data["meta"]["year_range"] = [min(years), max(years)] if years else [0, 0]
    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
