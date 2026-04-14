#!/usr/bin/env python3
"""
Match Instagram cover images to releases by artist-title filename.
Instagram images are named: artistraw-titlefirstword.jpg
Source md entries have the same raw artist + raw title.
Uses instagram.json for the image paths + captions.
"""

import collections
import json
import os
import re
import shutil
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
RELEASES_FILE = DATA_DIR / "releases.json"
INSTAGRAM_JSON = DATA_DIR / "instagram.json"
SOURCE_FILE = Path("/Users/humbertomacbook/Downloads/guestsixonetwo_posts.md")


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


def parse_source_entries():
    """Parse source md to get raw artist + raw title for each entry (deduped)."""
    entries = []
    seen = set()
    with open(SOURCE_FILE) as f:
        for line in f:
            line = line.strip()
            if not re.match(r"^\d+\.\s+", line):
                continue
            line = re.sub(r"^\d+\.\s*", "", line)
            if " — " not in line:
                continue
            artist_raw, rest = line.split(" — ", 1)
            artist_raw = artist_raw.strip()
            # Remove label
            m = re.search(r"\(([^)]+)\)", rest)
            if m:
                rest = rest[: m.start()].strip()
            # Remove format
            m2 = re.search(r"\[([^\]]+)\]", rest)
            if m2:
                rest = rest[: m2.start()].strip() + " " + rest[m2.end() :].strip()
                rest = rest.strip()
            # Remove episode info
            title_raw = re.sub(r"\s+episode\s+.*", "", rest).strip()

            key = f"{artist_raw}|{title_raw}".lower()
            if key in seen:
                continue
            seen.add(key)
            entries.append({"artist_raw": artist_raw, "title_raw": title_raw})
    return entries


def strip_accents(s):
    """Remove accents/diacritics: ü→u, é→e, ø→o, å→a, í→i etc."""
    nfkd = unicodedata.normalize("NFKD", s)
    out = []
    for c in nfkd:
        if unicodedata.category(c) == "Mn":  # combining mark
            continue
        # Special: ø → o, Ø → O
        if c in ("ø", "Ø"):
            out.append("o" if c == "ø" else "O")
        else:
            out.append(c)
    return "".join(out)


def build_ig_index(ig_posts):
    """Build lookup from filename stem → post data.
    Filename format: artistraw-titleword.jpg (possibly with -2, -3 suffix for dupes)
    Index both with accents and without for matching.
    """
    index = {}
    for p in ig_posts:
        stem = p["image"].split("/")[-1].replace(".jpg", "")
        # Remove trailing -2, -3 etc (duplicate post markers)
        base = re.sub(r"-(\d+)$", "", stem)
        if base not in index:
            index[base] = p
        index[stem] = p
        # Also index accent-stripped version
        stripped = strip_accents(base).lower()
        if stripped not in index:
            index[stripped] = p
    return index


def main():
    # Parse source for raw names
    source_entries = parse_source_entries()
    print(f"Source entries: {len(source_entries)}")

    # Load instagram data
    with open(INSTAGRAM_JSON) as f:
        ig_data = json.load(f)
    ig_index = build_ig_index(ig_data["posts"])
    print(f"Instagram images indexed: {len(ig_index)}")

    # Load releases
    with open(RELEASES_FILE) as f:
        data = json.load(f)
    releases = data["releases"]
    print(f"Releases: {len(releases)}")

    # Match: for each release (by index), use the corresponding source entry's
    # raw artist + raw first title word to find the instagram image
    matched = 0
    unmatched = []

    for i, r in enumerate(releases):
        if i >= len(source_entries):
            break

        src = source_entries[i]
        artist_raw = src["artist_raw"].lower()
        title_parts = src["title_raw"].split()
        first_title = title_parts[0].lower() if title_parts else ""

        # Build match key: artist-firsttitleword
        match_key = f"{artist_raw}-{first_title}"

        post = ig_index.get(match_key)

        # Try accent-stripped
        if not post:
            post = ig_index.get(strip_accents(match_key).lower())

        # Try with full title (no spaces)
        if not post:
            full_key = f"{artist_raw}-{src['title_raw'].replace(' ', '').lower()}"
            post = ig_index.get(full_key) or ig_index.get(strip_accents(full_key))

        # Handle special char artists: ø→o, single-letter → ø prefix
        # e.g. artist "m" in source → "mønic" or "mørbeck" in instagram
        # e.g. artist "r" → "rødhåd" in instagram
        # e.g. artist "h" → "héctoroaks" in instagram
        if not post:
            # Search by title word in caption
            for stem, p in ig_index.items():
                caption = (p.get("caption") or "").lower()
                if first_title and len(first_title) > 4 and f"#{first_title}" in caption:
                    # Verify artist initial matches
                    stem_low = strip_accents(stem).lower()
                    if artist_raw and stem_low.startswith(artist_raw[0]):
                        post = p
                        break

        # Try prefix match on artist + caption search
        if not post:
            for stem, p in ig_index.items():
                if stem.startswith(f"{artist_raw}-"):
                    caption = (p.get("caption") or "").lower()
                    if first_title and f"#{first_title}" in caption:
                        post = p
                        break
                # Also try accent-stripped prefix
                stripped_stem = strip_accents(stem).lower()
                if stripped_stem.startswith(f"{artist_raw}-"):
                    caption = (p.get("caption") or "").lower()
                    if first_title and f"#{first_title}" in caption:
                        post = p
                        break

        if post:
            img_src = os.path.join(
                "/Users/humbertomacbook/Downloads/techno-visual-archive", post["image"]
            )
            if os.path.exists(img_src):
                # Copy to images/ with release id
                dest_name = f"cover_{r['id']}.jpg"
                dest_path = IMAGES_DIR / dest_name
                shutil.copy2(img_src, dest_path)

                color, colors = extract_colors(dest_path)
                r["image"] = f"images/{dest_name}"
                r["color"] = color
                r["colors"] = colors
                matched += 1
            else:
                unmatched.append((i + 1, r["artist"], r["title"], match_key))
        else:
            unmatched.append((i + 1, r["artist"], r["title"], match_key))

    print(f"\nMatched: {matched}/{len(releases)}")
    print(f"Unmatched: {len(unmatched)}")

    if unmatched:
        print("\nUnmatched releases:")
        for num, artist, title, key in unmatched[:30]:
            print(f"  #{num}: {artist} — {title}  (tried: {key})")
        if len(unmatched) > 30:
            print(f"  ... and {len(unmatched) - 30} more")

    # Save
    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("\nSaved!")


if __name__ == "__main__":
    main()
