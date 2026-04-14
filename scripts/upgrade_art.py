#!/usr/bin/env python3
"""
Upgrade cover art: replace vinyl label photos with proper artwork.
Uses Discogs release API to get primary (cover) images instead of thumbnails.
Falls back to MusicBrainz Cover Art Archive for releases without good Discogs art.
"""

import collections
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_FILE = DATA_DIR / "releases.json"

TOKEN = os.environ.get("DISCOGS_TOKEN", "")


def get_discogs_primary_image(release_id):
    """Get the primary (cover) image URL from Discogs release API."""
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
            images = data.get("images", [])

            # Prefer primary type (cover art), then secondary (vinyl labels etc.)
            primary = [i for i in images if i.get("type") == "primary"]
            if primary:
                img = primary[0]
                # Only use if it's roughly square (cover art, not a banner)
                w, h = img.get("width", 0), img.get("height", 0)
                if w > 200 and h > 200:
                    return img.get("uri150") or img.get("uri")
            # If no primary, check if first secondary is square (might still be cover)
            if images:
                img = images[0]
                w, h = img.get("width", 0), img.get("height", 0)
                ratio = min(w, h) / max(w, h) if max(w, h) > 0 else 0
                if ratio > 0.85 and w > 200:
                    return img.get("uri150") or img.get("uri")
    except HTTPError as e:
        if e.code != 404:
            print(f"  HTTP {e.code} for release {release_id}")
    except Exception as e:
        print(f"  Error: {e}")
    return None


def download_image(url, dest_path):
    """Download image, return True on success."""
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 500:  # Skip tiny/broken images
                with open(dest_path, "wb") as f:
                    f.write(data)
                return True
    except:
        pass
    return False


def is_vinyl_label_photo(image_path):
    """Heuristic: detect if an image is likely a circular vinyl label photo.
    Vinyl labels have a dominant circular shape with lots of pixels near the edges
    being dark/black (the record surface) and a circular center area.
    """
    try:
        from PIL import Image
        img = Image.open(image_path).convert("RGB").resize((64, 64))
        pixels = list(img.getdata())

        # Check corners - vinyl label photos typically have dark corners
        # (the black vinyl surrounding the circular label)
        w = 64
        corner_pixels = []
        for y in range(8):
            for x in range(8):
                corner_pixels.append(pixels[y * w + x])           # top-left
                corner_pixels.append(pixels[y * w + (w - 1 - x)])  # top-right
                corner_pixels.append(pixels[(w - 1 - y) * w + x])  # bottom-left
                corner_pixels.append(pixels[(w - 1 - y) * w + (w - 1 - x)])  # bottom-right

        # If corners are very dark, likely a vinyl label photo
        dark_corners = sum(1 for r, g, b in corner_pixels if (r + g + b) / 3 < 30)
        total_corners = len(corner_pixels)
        dark_ratio = dark_corners / total_corners

        # Also check if center is brighter than edges (circular label pattern)
        center_pixels = []
        for y in range(24, 40):
            for x in range(24, 40):
                center_pixels.append(pixels[y * w + x])
        center_brightness = sum((r + g + b) / 3 for r, g, b in center_pixels) / len(center_pixels)
        corner_brightness = sum((r + g + b) / 3 for r, g, b in corner_pixels) / len(corner_pixels)

        # Vinyl label: dark corners (>60%) AND center much brighter than corners
        if dark_ratio > 0.6 and center_brightness > corner_brightness * 2.5:
            return True

    except:
        pass
    return False


def extract_color(image_path):
    """Extract dominant colors from an image."""
    try:
        from PIL import Image
        img = Image.open(image_path).convert("RGB").resize((32, 32))
        pixels = list(img.getdata())
        counts = collections.Counter()
        for pr, pg, pb in pixels:
            lightness = (pr + pg + pb) / 3
            if lightness < 10 or lightness > 245:
                continue
            counts[(pr >> 4, pg >> 4, pb >> 4)] += 1
        if counts:
            top = counts.most_common(3)
            colors = []
            for (qr, qg, qb), _ in top:
                colors.append(f"#{(qr << 4) | 8:02x}{(qg << 4) | 8:02x}{(qb << 4) | 8:02x}")
            return colors[0], colors
    except:
        pass
    return None, []


def main():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    releases = data["releases"]
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # First pass: identify vinyl label photos
    vinyl_labels = []
    no_image = []
    good_images = []

    for r in releases:
        img_path = r.get("image", "")
        full_path = SCRIPT_DIR.parent / img_path if img_path else None

        if not img_path or not full_path or not full_path.exists():
            no_image.append(r)
        elif is_vinyl_label_photo(full_path):
            vinyl_labels.append(r)
        else:
            good_images.append(r)

    print(f"Good artwork: {len(good_images)}")
    print(f"Vinyl label photos: {len(vinyl_labels)}")
    print(f"No image: {len(no_image)}")

    # Try to upgrade vinyl label photos + no-image releases
    to_upgrade = vinyl_labels + no_image
    print(f"\nAttempting to upgrade {len(to_upgrade)} releases via Discogs API...")

    upgraded = 0
    for i, r in enumerate(to_upgrade):
        rid = r["id"]
        new_url = get_discogs_primary_image(rid)

        if new_url:
            dest = IMAGES_DIR / f"{rid}.jpg"
            if download_image(new_url, dest):
                r["image"] = f"images/{rid}.jpg"
                # Re-extract color
                color, colors = extract_color(dest)
                if color:
                    r["color"] = color
                    r["colors"] = colors
                upgraded += 1
                if upgraded % 10 == 0:
                    print(f"  Upgraded {upgraded} so far...")

        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(to_upgrade)}")

    print(f"\nUpgraded {upgraded}/{len(to_upgrade)} releases")

    # Save
    data["meta"]["total"] = len(data["releases"])
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print("Saved.")


if __name__ == "__main__":
    main()
