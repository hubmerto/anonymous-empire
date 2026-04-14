#!/usr/bin/env python3
"""
Techno Visual Archive — Discogs Data Collector
Fetches release data from Discogs API for curated label list.
Downloads thumbnails locally and extracts dominant colors.

Usage:
    python collect.py --token YOUR_DISCOGS_TOKEN
    python collect.py --token YOUR_DISCOGS_TOKEN --resume
    python collect.py --token YOUR_DISCOGS_TOKEN --label "Tresor"
    python collect.py --token YOUR_DISCOGS_TOKEN --max-per-label 15
    python collect.py --extract-colors  # color pass on existing data

Get your token: https://www.discogs.com/settings/developers
"""

import argparse
import collections
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# --- Config ---
API_BASE = "https://api.discogs.com"
PER_PAGE = 100
RATE_LIMIT_DELAY = 1.1  # seconds between API requests
IMAGE_DELAY = 0.05       # seconds between image downloads (CDN is less strict)
MAX_RETRIES = 3
RETRY_DELAY = 5

SCRIPT_DIR = Path(__file__).parent
LABELS_FILE = SCRIPT_DIR / "labels.json"
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_FILE = DATA_DIR / "releases.json"
PROGRESS_FILE = DATA_DIR / ".progress.json"

# Hardcoded coordinates for all scenes
GEO_COORDS = {
    "Detroit": {"lat": 42.3314, "lng": -83.0458},
    "Chicago": {"lat": 41.8781, "lng": -87.6298},
    "Berlin": {"lat": 52.5200, "lng": 13.4050},
    "Cologne": {"lat": 50.9375, "lng": 6.9603},
    "Frankfurt": {"lat": 50.1109, "lng": 8.6821},
    "Hamburg": {"lat": 53.5511, "lng": 9.9937},
    "Munich": {"lat": 48.1351, "lng": 11.5820},
    "Chemnitz / Dresden": {"lat": 51.0504, "lng": 13.7373},
    "Sheffield / Leeds": {"lat": 53.3811, "lng": -1.4701},
    "London": {"lat": 51.5074, "lng": -0.1278},
    "Ghent / Brussels": {"lat": 50.8503, "lng": 4.3517},
    "Netherlands": {"lat": 52.3676, "lng": 4.9041},
    "Paris": {"lat": 48.8566, "lng": 2.3522},
    "New York": {"lat": 40.7128, "lng": -74.0060},
    "Canada": {"lat": 43.6532, "lng": -79.3832},
    "Japan": {"lat": 35.6762, "lng": 139.6503},
    "Georgia / Eastern Europe": {"lat": 41.7151, "lng": 44.8271},
    "São Paulo / South America": {"lat": -23.5505, "lng": -46.6333},
    "Italy": {"lat": 45.4642, "lng": 9.1900},
    "Manchester": {"lat": 53.4808, "lng": -2.2426},
}


def api_request(url, token):
    """Make a rate-limited request to Discogs API."""
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={token}",
        "Accept": "application/json",
    }
    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url, headers=headers)
            with urlopen(req) as resp:
                time.sleep(RATE_LIMIT_DELAY)
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 429:
                wait = RETRY_DELAY * (attempt + 2)
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            elif e.code == 404:
                print(f"  404: {url} — skipping")
                return None
            else:
                print(f"  HTTP {e.code}: {url} — retry {attempt + 1}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY)
        except URLError as e:
            print(f"  Network error: {e} — retry {attempt + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    print(f"  Failed after {MAX_RETRIES} retries: {url}")
    return None


def download_image(url, dest_path):
    """Download an image to a local path. Returns True on success."""
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    for attempt in range(2):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=10) as resp:
                data = resp.read()
                with open(dest_path, "wb") as f:
                    f.write(data)
                time.sleep(IMAGE_DELAY)
                return True
        except Exception as e:
            if attempt == 0:
                time.sleep(1)
            else:
                return False
    return False


def fetch_label_releases(label_id, label_name, scene, token, max_releases=None):
    """Fetch releases for a label, handling pagination."""
    releases = []
    page = 1
    total_pages = 1

    while page <= total_pages:
        if max_releases and len(releases) >= max_releases:
            break

        url = f"{API_BASE}/labels/{label_id}/releases?page={page}&per_page={PER_PAGE}&sort=year&sort_order=asc"
        data = api_request(url, token)

        if not data:
            break

        total_pages = data.get("pagination", {}).get("pages", 1)
        total_items = data.get("pagination", {}).get("items", 0)

        if page == 1:
            print(f"  {total_items} total on Discogs", end="")
            if max_releases:
                print(f" (capping at {max_releases})", end="")
            print()

        for r in data.get("releases", []):
            if max_releases and len(releases) >= max_releases:
                break
            releases.append({
                "id": r.get("id"),
                "title": r.get("title", "Untitled"),
                "artist": r.get("artist", "Unknown"),
                "year": r.get("year", 0),
                "catno": r.get("catno", ""),
                "thumb": r.get("thumb", ""),
                "format": r.get("format", ""),
                "label": label_name,
                "label_id": label_id,
                "scene": scene,
                "discogs_url": f"https://www.discogs.com/release/{r.get('id', '')}",
                "resource_url": r.get("resource_url", ""),
            })

        print(f"  Page {page}/{total_pages} — {len(releases)} collected")
        page += 1

    return releases


def download_thumbnails(releases):
    """Download thumbnail images for all releases. Updates release dicts with local paths."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped = 0
    failed = 0

    for i, r in enumerate(releases):
        if not r.get("thumb"):
            r["image"] = ""
            skipped += 1
            continue

        ext = "jpg"
        filename = f"{r['id']}.{ext}"
        dest = IMAGES_DIR / filename
        local_path = f"images/{filename}"

        if dest.exists():
            r["image"] = local_path
            skipped += 1
            continue

        if download_image(r["thumb"], dest):
            r["image"] = local_path
            downloaded += 1
        else:
            r["image"] = ""
            failed += 1

        if (i + 1) % 50 == 0:
            print(f"  Images: {i + 1}/{len(releases)} ({downloaded} new, {skipped} existing, {failed} failed)")

    print(f"  Images done: {downloaded} downloaded, {skipped} skipped, {failed} failed")


def extract_colors(releases):
    """Extract dominant colors from downloaded thumbnails using Pillow."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed. Run: pip install Pillow")
        sys.exit(1)

    processed = 0
    skipped = 0

    for i, r in enumerate(releases):
        if r.get("color"):
            skipped += 1
            continue

        image_path = r.get("image", "")
        if not image_path:
            r["color"] = None
            r["colors"] = []
            skipped += 1
            continue

        full_path = SCRIPT_DIR.parent / image_path
        if not full_path.exists():
            r["color"] = None
            r["colors"] = []
            skipped += 1
            continue

        try:
            img = Image.open(full_path).convert("RGB").resize((32, 32))
            pixels = list(img.getdata())

            # Quantize to 4-bit per channel and count
            counts = collections.Counter()
            for pr, pg, pb in pixels:
                qr, qg, qb = pr >> 4, pg >> 4, pb >> 4
                # Filter near-black and near-white
                lightness = (pr + pg + pb) / 3
                if lightness < 10 or lightness > 245:
                    continue
                counts[(qr, qg, qb)] += 1

            if not counts:
                # All pixels were near-black/white
                r["color"] = None
                r["colors"] = []
            else:
                top = counts.most_common(3)
                hex_colors = []
                for (qr, qg, qb), _ in top:
                    hr = (qr << 4) | 8
                    hg = (qg << 4) | 8
                    hb = (qb << 4) | 8
                    hex_colors.append(f"#{hr:02x}{hg:02x}{hb:02x}")
                r["color"] = hex_colors[0]
                r["colors"] = hex_colors

            processed += 1
        except Exception as e:
            r["color"] = None
            r["colors"] = []

        if (i + 1) % 100 == 0:
            print(f"  Colors: {i + 1}/{len(releases)} ({processed} extracted)")

    print(f"  Colors done: {processed} extracted, {skipped} skipped")


def load_progress():
    """Load progress from previous interrupted run."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed_labels": [], "releases": []}


def save_progress(progress):
    """Save progress for resumability."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def save_output(releases):
    """Save final releases.json with geo data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    releases.sort(key=lambda r: (r.get("year", 0), r.get("label", "")))

    # Remove internal fields
    for r in releases:
        r.pop("resource_url", None)

    output = {
        "meta": {
            "total": len(releases),
            "labels": len(set(r["label"] for r in releases)),
            "scenes": sorted(set(r["scene"] for r in releases)),
            "year_range": [
                min((r["year"] for r in releases if r["year"] > 0), default=0),
                max((r["year"] for r in releases if r["year"] > 0), default=0),
            ],
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "geo": GEO_COORDS,
        "releases": releases,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_mb = OUTPUT_FILE.stat().st_size / 1024 / 1024
    print(f"\nSaved {len(releases)} releases to {OUTPUT_FILE} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Collect techno release data from Discogs")
    parser.add_argument("--token", help="Discogs personal access token")
    parser.add_argument("--resume", action="store_true", help="Resume from last progress")
    parser.add_argument("--label", help="Collect only this label (by name)")
    parser.add_argument("--max-per-label", type=int, default=None, help="Max releases per label")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected")
    parser.add_argument("--extract-colors", action="store_true", help="Extract colors from existing data")
    parser.add_argument("--skip-images", action="store_true", help="Skip image downloads")
    args = parser.parse_args()

    # Color extraction pass (no token needed)
    if args.extract_colors:
        if not OUTPUT_FILE.exists():
            print("No releases.json found. Run collection first.")
            sys.exit(1)
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        print(f"Extracting colors for {len(data['releases'])} releases...")
        extract_colors(data["releases"])
        save_output(data["releases"])
        print("Done.")
        return

    if not args.token:
        print("--token is required for collection. Use --extract-colors for color-only pass.")
        sys.exit(1)

    # Load label list
    with open(LABELS_FILE) as f:
        label_data = json.load(f)

    all_labels = []
    for scene_group in label_data["labels"]:
        scene = scene_group["scene"]
        for label in scene_group["labels"]:
            all_labels.append({
                "name": label["name"],
                "discogs_id": label["discogs_id"],
                "scene": scene,
            })

    if args.label:
        all_labels = [l for l in all_labels if args.label.lower() in l["name"].lower()]
        if not all_labels:
            print(f"No label matching '{args.label}' found in labels.json")
            sys.exit(1)

    if args.dry_run:
        print(f"Would collect from {len(all_labels)} labels:")
        for l in all_labels:
            suffix = f" (max {args.max_per_label})" if args.max_per_label else ""
            print(f"  [{l['scene']}] {l['name']} (ID: {l['discogs_id']}){suffix}")
        sys.exit(0)

    # Load or init progress
    if args.resume:
        progress = load_progress()
        print(f"Resuming: {len(progress['completed_labels'])} labels done, {len(progress['releases'])} releases")
    else:
        progress = {"completed_labels": [], "releases": []}

    # Collect
    total = len(all_labels)
    for i, label in enumerate(all_labels):
        label_key = f"{label['discogs_id']}:{label['name']}"

        if label_key in progress["completed_labels"]:
            print(f"[{i+1}/{total}] {label['name']} — already done, skipping")
            continue

        print(f"\n[{i+1}/{total}] {label['name']} ({label['scene']}) — ID {label['discogs_id']}")
        releases = fetch_label_releases(
            label["discogs_id"],
            label["name"],
            label["scene"],
            args.token,
            max_releases=args.max_per_label,
        )

        progress["releases"].extend(releases)
        progress["completed_labels"].append(label_key)
        save_progress(progress)
        print(f"  {len(releases)} releases — running total: {len(progress['releases'])}")

    # Deduplicate by release ID
    seen = set()
    unique = []
    for r in progress["releases"]:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique.append(r)

    print(f"\nDeduplication: {len(progress['releases'])} -> {len(unique)} unique releases")

    # Download images
    if not args.skip_images:
        print("\nDownloading thumbnails...")
        download_thumbnails(unique)

    # Extract colors
    print("\nExtracting colors...")
    extract_colors(unique)

    # Save final output
    save_output(unique)

    # Clean up progress file
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()

    print("Done.")


if __name__ == "__main__":
    main()
