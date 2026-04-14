#!/usr/bin/env python3
"""
Assign Instagram cover images to releases.
1956 images from ~662 posts (carousel ~3 imgs each).
Sort by media ID (newest first = post #1), take first of each group.
Copy assigned covers to images/ with release ID as filename.
"""

import collections
import json
import os
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
INSTAGRAM_DIR = IMAGES_DIR / "instagram"
RELEASES_FILE = DATA_DIR / "releases.json"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def shortcode_to_id(shortcode):
    result = 0
    for c in shortcode:
        result = result * 64 + ALPHABET.index(c)
    return result


def extract_colors(path):
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
    except Exception:
        pass
    return "#1a1a1a", ["#1a1a1a", "#0a0a0a", "#2a2a2a"]


def main():
    # Get all instagram images
    files = [f for f in os.listdir(INSTAGRAM_DIR) if f.endswith(".jpg")]
    print(f"Found {len(files)} Instagram images")

    # Sort by media ID, newest first (post #1 = most recent)
    items = []
    for f in files:
        shortcode = f.replace(".jpg", "")
        try:
            mid = shortcode_to_id(shortcode)
            items.append((mid, f))
        except (ValueError, IndexError):
            continue

    items.sort(reverse=True)  # newest first
    print(f"Sorted {len(items)} images by media ID (newest first)")

    # Load releases
    with open(RELEASES_FILE) as f:
        data = json.load(f)

    releases = data["releases"]
    n_releases = len(releases)
    n_images = len(items)
    print(f"Releases: {n_releases}, Images: {n_images}")
    print(f"Ratio: {n_images / n_releases:.2f} images per post")

    # Distribute evenly: for post i, take image at position round(i * n_images / n_releases)
    # This picks the first image from each ~3-image group
    assigned = 0
    for i, release in enumerate(releases):
        idx = round(i * n_images / n_releases)
        if idx >= n_images:
            idx = n_images - 1

        _, src_file = items[idx]
        src_path = INSTAGRAM_DIR / src_file

        # Copy to images/ with release id as name
        dest_name = f"cover_{release['id']}.jpg"
        dest_path = IMAGES_DIR / dest_name

        shutil.copy2(src_path, dest_path)

        # Extract colors
        color, colors = extract_colors(dest_path)

        release["image"] = f"images/{dest_name}"
        release["color"] = color
        release["colors"] = colors
        assigned += 1

    print(f"Assigned {assigned} covers")

    # Save
    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()
