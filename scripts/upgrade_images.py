#!/usr/bin/env python3
"""Upgrade all cover images to high-res from Discogs release API."""

import collections
import hashlib
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")


def fetch_hires_url(release_id):
    """Get the highest-res image URL from a Discogs release."""
    url = f"https://api.discogs.com/releases/{release_id}"
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={TOKEN}",
        "Accept": "application/json",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            time.sleep(1.1)  # rate limit
            data = json.loads(resp.read().decode("utf-8"))
            imgs = data.get("images", [])
            if imgs:
                # Prefer primary image, fall back to first
                for img in imgs:
                    if img.get("type") == "primary":
                        return img.get("resource_url") or img.get("uri")
                return imgs[0].get("resource_url") or imgs[0].get("uri")
    except Exception as e:
        print(f"  ERR fetching release {release_id}: {e}")
    return None


def download_image(url, dest):
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={TOKEN}",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=20) as resp:
            data = resp.read()
            if len(data) > 1000:
                with open(dest, "wb") as f:
                    f.write(data)
                return len(data)
    except Exception as e:
        print(f"  ERR downloading: {e}")
    return 0


def extract_color(path):
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB").resize((32, 32))
        pixels = list(img.getdata())
        counts = collections.Counter()
        for pr, pg, pb in pixels:
            if (pr + pg + pb) / 3 < 10 or (pr + pg + pb) / 3 > 245:
                continue
            counts[(pr >> 4, pg >> 4, pb >> 4)] += 1
        if counts:
            top = counts.most_common(3)
            colors = [
                f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}"
                for (qr, qg, qb), _ in top
            ]
            return colors[0], colors
    except:
        pass
    return None, []


def main():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    releases = data["releases"]
    total = len(releases)
    upgraded = 0
    skipped = 0
    failed = 0

    print(f"Upgrading images for {total} releases...")

    for i, r in enumerate(releases):
        rid = r.get("id")
        if not rid:
            skipped += 1
            continue

        dest = IMAGES_DIR / f"{rid}.jpg"
        # Check if already high-res (>50KB = likely already upgraded)
        if dest.exists() and dest.stat().st_size > 50000:
            skipped += 1
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{total}] {upgraded} upgraded, {skipped} skipped")
            continue

        hires_url = fetch_hires_url(rid)
        if not hires_url:
            failed += 1
            continue

        size = download_image(hires_url, dest)
        if size > 0:
            r["image"] = f"images/{rid}.jpg"
            # Re-extract colors from better image
            color, colors = extract_color(dest)
            if color:
                r["color"] = color
                r["colors"] = colors
            upgraded += 1
        else:
            failed += 1

        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{total}] {upgraded} upgraded, {skipped} skipped, {failed} failed")

        # Checkpoint save every 100 upgrades
        if upgraded > 0 and upgraded % 100 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(data, f, separators=(",", ":"))
            print(f"  (checkpoint saved)")

    # Final save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\n{'='*50}")
    print(f"Done: {upgraded} upgraded, {skipped} already hi-res, {failed} failed")
    print(f"Total: {total} releases")


if __name__ == "__main__":
    main()
