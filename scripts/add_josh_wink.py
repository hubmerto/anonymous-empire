#!/usr/bin/env python3
"""Add Josh Wink - Don't Laugh to the archive."""

import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_FILE = DATA_DIR / "releases.json"

TOKEN = os.environ.get("DISCOGS_TOKEN", "")

# Search for the original 1995 Strictly Rhythm 12"
WANTED = [
    {"q": "Josh Wink Don't Laugh Strictly Rhythm", "scene": "New York", "label": "Strictly Rhythm"},
]


def search_discogs(query, token):
    url = f"https://api.discogs.com/database/search?q={quote(query)}&type=release&per_page=5"
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={token}",
        "Accept": "application/json",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req) as resp:
            time.sleep(1.1)
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            # Prefer earliest year
            results = [r for r in results if r.get("year")]
            if not results:
                return None
            results.sort(key=lambda r: int(r.get("year") or 9999))
            r = results[0]
            title = r.get("title", "")
            artist, _, rest = title.partition(" - ")
            return {
                "id": r.get("id"),
                "title": rest.strip() if rest else title,
                "artist": artist.strip() if rest else "Josh Wink",
                "year": int(r.get("year") or 1995),
                "catno": r.get("catno", ""),
                "thumb": r.get("cover_image") or r.get("thumb", ""),
                "format": ", ".join(r.get("format", [])) if isinstance(r.get("format"), list) else r.get("format", ""),
                "country": r.get("country", "US"),
            }
    except Exception as e:
        print(f"  Error: {e}")
    return None


def download_image(url, dest_path):
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
            return True
    except Exception as e:
        print(f"  download error: {e}")
        return False


def main():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    existing_ids = {r["id"] for r in data["releases"]}
    added = 0

    for item in WANTED:
        # Dup check on artist+title first
        for r in data["releases"]:
            if (r.get("artist", "").lower() == "josh wink"
                and "don't laugh" in r.get("title", "").lower()):
                print(f"  Already present: {r['artist']} - {r['title']}")
                return

        result = search_discogs(item["q"], TOKEN)
        if not result:
            print(f"  NOT FOUND: {item['q']}")
            continue

        if result["id"] in existing_ids:
            print(f"  Duplicate id: {result['id']}")
            continue

        image_path = ""
        if result["thumb"]:
            IMAGES_DIR.mkdir(parents=True, exist_ok=True)
            dest = IMAGES_DIR / f"{result['id']}.jpg"
            if dest.exists() or download_image(result["thumb"], dest):
                image_path = f"images/{result['id']}.jpg"

        release = {
            "id": result["id"],
            "title": result["title"] or "Don't Laugh",
            "artist": result["artist"] or "Josh Wink",
            "year": result["year"],
            "catno": result["catno"],
            "thumb": result["thumb"],
            "format": result["format"] or "12\"",
            "label": item["label"],
            "label_id": 0,
            "scene": item["scene"],
            "discogs_url": f"https://www.discogs.com/release/{result['id']}",
            "image": image_path,
            "color": None,
            "colors": [],
            "country": result["country"],
        }

        data["releases"].append(release)
        existing_ids.add(result["id"])
        added += 1
        print(f"  ADDED: {release['artist']} - {release['title']} ({release['year']}) id={result['id']}")
        print(f"  image: {image_path}")

    if added == 0:
        print("Nothing added.")
        return

    data["releases"].sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r["year"] > 0]
    data["meta"]["year_range"] = [min(years, default=0), max(years, default=0)]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nAdded {added}. Total: {data['meta']['total']}")


if __name__ == "__main__":
    main()
