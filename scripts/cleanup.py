#!/usr/bin/env python3
"""
Clean up releases.json:
1. Query Discogs for each release's actual genre/style and country
2. Remove releases that aren't electronic/techno
3. Fix scene assignments based on actual label country
4. Remove duplicates and junk entries
"""

import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "releases.json"

TOKEN = os.environ.get("DISCOGS_TOKEN", "")

# Genres/styles that belong in a techno archive
VALID_GENRES = {
    "electronic", "techno", "house", "ambient", "experimental",
    "electro", "minimal", "dub techno", "acid", "industrial",
    "idm", "breakbeat", "drum n bass", "dubstep", "trance",
    "downtempo", "abstract", "noise", "dark ambient",
    "leftfield", "uk garage", "grime", "jungle",
    "synth-pop", "ebm", "new wave", "post-punk",
}

# Obvious non-electronic artists to remove immediately
BLACKLIST_ARTISTS = {
    "rolling stones", "sex pistols", "deep purple", "men at work",
    "flaming lips", "they might be giants", "liege lord",
    "wire", "funeral leech", "michael boddicker",
    "hannah peel", "laura j martin", "corduroy", "mother earth",
    "sharon redd", "albert west",
}


def get_release_info(release_id):
    """Get genre, style, and country from Discogs release API."""
    url = f"https://api.discogs.com/releases/{release_id}"
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={TOKEN}",
        "Accept": "application/json",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as resp:
            time.sleep(1.1)
            data = json.loads(resp.read().decode("utf-8"))
            genres = [g.lower() for g in data.get("genres", [])]
            styles = [s.lower() for s in data.get("styles", [])]
            country = data.get("country", "")
            year = data.get("year", 0)
            title = data.get("title", "")
            artists = [a.get("name", "") for a in data.get("artists", [])]
            labels = [l.get("name", "") for l in data.get("labels", [])]
            return {
                "genres": genres,
                "styles": styles,
                "country": country,
                "year": year,
                "title": title,
                "artists": artists,
                "labels": labels,
            }
    except HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 429:
            print("  Rate limited, waiting 30s...")
            time.sleep(30)
            return get_release_info(release_id)
    except Exception as e:
        print(f"  Error for {release_id}: {e}")
    return None


def is_electronic(info):
    """Check if a release's genres/styles indicate electronic music."""
    if not info:
        return False
    all_tags = set(info["genres"] + info["styles"])
    return bool(all_tags & VALID_GENRES)


def main():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    releases = data["releases"]
    print(f"Starting with {len(releases)} releases")

    # Phase 1: Quick blacklist filter (no API calls)
    before = len(releases)
    releases = [
        r for r in releases
        if r.get("artist", "").lower() not in BLACKLIST_ARTISTS
        and not any(bl in r.get("artist", "").lower() for bl in BLACKLIST_ARTISTS)
    ]
    print(f"After artist blacklist: {len(releases)} (removed {before - len(releases)})")

    # Phase 2: Query Discogs for genre/country validation
    to_remove = []
    to_update = []
    checked = 0

    for i, r in enumerate(releases):
        rid = r["id"]
        info = get_release_info(rid)
        checked += 1

        if info is None:
            # 404 — release doesn't exist on Discogs anymore
            to_remove.append(rid)
            print(f"  REMOVE (404): {r['artist']} - {r['title']}")
            continue

        if not is_electronic(info):
            to_remove.append(rid)
            genres_str = ", ".join(info["genres"] + info["styles"])
            print(f"  REMOVE (not electronic): {r['artist']} - {r['title']} [{genres_str}]")
            continue

        # Update year if we had 0
        if r.get("year", 0) == 0 and info.get("year", 0) > 0:
            r["year"] = info["year"]

        # Update country/scene if available
        if info.get("country"):
            r["country"] = info["country"]

        if (i + 1) % 25 == 0:
            print(f"  Checked {i + 1}/{len(releases)} — {len(to_remove)} to remove")

    # Remove non-electronic releases
    releases = [r for r in releases if r["id"] not in set(to_remove)]
    print(f"\nAfter genre filter: {len(releases)} (removed {len(to_remove)} non-electronic)")

    # Phase 3: Deduplicate by title+artist (same release appearing under multiple labels)
    seen = set()
    unique = []
    dupes = 0
    for r in releases:
        key = f"{r['artist'].lower().strip()}|{r['title'].lower().strip()}"
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        unique.append(r)
    releases = unique
    print(f"After title dedup: {len(releases)} (removed {dupes} duplicates)")

    # Update and save
    releases.sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["releases"] = releases
    data["meta"]["total"] = len(releases)
    data["meta"]["labels"] = len(set(r["label"] for r in releases))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in releases))
    years = [r["year"] for r in releases if r["year"] > 0]
    data["meta"]["year_range"] = [min(years, default=0), max(years, default=0)]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nFinal: {len(releases)} releases, {data['meta']['labels']} labels")
    print("Saved.")


if __name__ == "__main__":
    main()
