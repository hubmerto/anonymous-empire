#!/usr/bin/env python3
"""
Rename Instagram images from shortcode.jpg to artist-releasename.jpg
based on caption hashtags. Updates the manifest accordingly.
"""

import json
import re
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "images" / "instagram"
DATA_FILE = PROJECT_ROOT / "data" / "instagram.json"


def parse_caption(caption):
    """Extract artist and release name from hashtag caption."""
    # Extract hashtags
    tags = re.findall(r'#(\w+)', caption.lower())
    if len(tags) < 2:
        return None, None

    artist = tags[0]
    release = tags[1]
    return artist, release


def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    # Replace non-alphanumeric chars (except dash/underscore) with dash
    name = re.sub(r'[^\w\-]', '-', name)
    # Collapse multiple dashes
    name = re.sub(r'-+', '-', name)
    # Trim dashes from ends
    name = name.strip('-')
    return name[:80]  # Cap length


def main():
    with open(DATA_FILE) as f:
        data = json.load(f)

    used_names = {}
    renamed = 0
    skipped = 0

    for post in data["posts"]:
        old_filename = f"{post['shortcode']}.jpg"
        old_path = IMAGES_DIR / old_filename

        if not old_path.exists():
            skipped += 1
            continue

        artist, release = parse_caption(post.get("caption", ""))
        if not artist or not release:
            # Keep original name
            skipped += 1
            continue

        base_name = sanitize_filename(f"{artist}-{release}")

        # Handle duplicates by appending a counter
        if base_name in used_names:
            used_names[base_name] += 1
            final_name = f"{base_name}-{used_names[base_name]}.jpg"
        else:
            used_names[base_name] = 1
            final_name = f"{base_name}.jpg"

        new_path = IMAGES_DIR / final_name

        # Rename file
        os.rename(old_path, new_path)
        post["image"] = f"images/instagram/{final_name}"
        renamed += 1

    # Write updated manifest
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Renamed: {renamed}, Skipped: {skipped}")
    print(f"Manifest updated: {DATA_FILE}")


if __name__ == "__main__":
    main()
