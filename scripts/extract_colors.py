#!/usr/bin/env python3
"""
Color extraction for release covers.

Goal: pick a *perceptually* dominant color so the color view sorts the way
a human would expect — vibrant accents win over dark backgrounds, flat
achromatic covers are grouped and sorted by lightness.

Algorithm:
  1. Center-crop ~88% to skip borders / vignettes / frames.
  2. Resize to 96x96 (balance fidelity vs. speed).
  3. Median-cut quantization into an 8-color palette (PIL's built-in).
  4. Score each palette entry = coverage × sqrt(saturation), with a
     penalty for extreme lightness (near-black / near-white), so
     backgrounds lose to accents unless the image is mostly monochrome.
  5. Representative color (`color`) = highest-scoring palette entry.
  6. `sort_hue`:
       - if all palette entries have saturation < 12 → achromatic:
         return -1 + lightness/100 (range -1..0, dark first)
       - else: saturation-weighted circular mean of top chromatic entries.

Outputs per release:
  color:      "#rrggbb"  representative hex
  colors:     ["#...", ...]  top 5 palette colors, coverage-ordered
  hsl:        {hex, h, s, l}  of representative color
  sort_hue:   float (-1..0 achromatic, 0..360 chromatic)
  palette:    [{hex, h, s, l, frac}, ...]  full palette for debugging

Re-runs are resumable via --skip-done: releases with non-null sort_hue
are left alone. Use --force to recompute everything.
"""

import argparse
import colorsys
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow required. pip install Pillow")

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RELEASES_FILE = DATA_DIR / "releases.json"

PALETTE_SIZE = 8
THUMB_SIZE = 96
CROP_RATIO = 0.06  # trim 6% from each edge → 88% central
# Chroma threshold for "colorful enough to read as a hue".
# chroma = (min(l,100-l)/50) * (s/100) * 100, peaks at l=50,s=100.
# A dark brown-black (l=10, s=40) has chroma ≈ 8 → treated as mono.
# A muted olive (l=40, s=35) has chroma ≈ 28 → chromatic.
CHROMA_MIN = 18
TOP_N_RETURN = 5   # colors[] length


def extract_palette(image_path):
    """Return list of palette entries sorted by score (representative first).
    Each entry: {rgb, hex, h, s, l, count, frac}."""
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return None, f"open: {e}"

    w, h = img.size
    if w < 10 or h < 10:
        return None, "too small"

    pw = int(w * CROP_RATIO)
    ph = int(h * CROP_RATIO)
    img = img.crop((pw, ph, w - pw, h - ph))
    img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)

    # Median-cut quantize into palette_size clusters.
    pal_img = img.quantize(colors=PALETTE_SIZE, method=Image.Quantize.MEDIANCUT)
    palette = pal_img.getpalette()  # flat [r0,g0,b0, r1,g1,b1, ...]
    color_counts = pal_img.getcolors()  # [(count, index), ...]
    if not color_counts:
        return None, "no colors"

    entries = []
    for count, idx in color_counts:
        r = palette[idx * 3]
        g = palette[idx * 3 + 1]
        b = palette[idx * 3 + 2]
        hue, light, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        l_pct = light * 100
        s_pct = sat * 100
        # Chroma — how visually "colorful" this pixel reads.
        # min(l,100-l)/50 caps the brightness factor at 1 (peak at mid-gray);
        # s/100 weights by saturation.
        chroma = (min(l_pct, 100 - l_pct) / 50) * (s_pct / 100) * 100
        entries.append({
            "rgb": (r, g, b),
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "h": round(hue * 360, 1),
            "s": round(s_pct, 1),
            "l": round(l_pct, 1),
            "c": round(chroma, 1),
            "count": count,
        })

    total = sum(e["count"] for e in entries) or 1
    for e in entries:
        e["frac"] = round(e["count"] / total, 4)

    return score_entries(entries), None


def score_entries(entries):
    """Score entries so the most visually-dominant color wins.
    score = chroma × frac — chroma is saturation × brightness-peakedness,
    so dark-near-black 'accents' can't beat a truly colorful region.
    Near-mono images will all score low → the representative is just the
    most-covered entry (the `frac` term still rewards coverage)."""
    for e in entries:
        # Base score: chroma * coverage. Add a tiny coverage floor so for
        # monochrome images we still pick by coverage (not noise).
        e["score"] = e["c"] * e["frac"] + 0.01 * e["frac"]
    entries.sort(key=lambda e: e["score"], reverse=True)
    return entries


def compute_sort_hue(palette):
    """Return -1..0 for achromatic (sorted by lightness),
    0..360 for chromatic (chroma-weighted circular mean of top entries)."""
    if not palette:
        return 0.0

    # "Chromatic enough" — chroma above threshold.
    chromatic = [e for e in palette if e["c"] >= CHROMA_MIN]
    # Also require the chromatic mass to be meaningful — otherwise a single
    # vibrant speck shouldn't drag a predominantly dark cover into a hue bucket.
    chromatic_frac = sum(e["frac"] for e in chromatic)
    if not chromatic or chromatic_frac < 0.08:
        # Achromatic — sort by coverage-weighted lightness
        total = sum(e["frac"] for e in palette) or 1
        avg_l = sum(e["l"] * e["frac"] for e in palette) / total
        return round(-1 + avg_l / 100, 4)

    # Chroma-weighted circular mean of top chromatic entries.
    total_w = 0.0
    x = 0.0
    y = 0.0
    for e in chromatic[:4]:
        w = e["frac"] * e["c"]
        rad = math.radians(e["h"])
        x += math.cos(rad) * w
        y += math.sin(rad) * w
        total_w += w

    if total_w == 0:
        return chromatic[0]["h"]

    hue = math.degrees(math.atan2(y / total_w, x / total_w))
    if hue < 0:
        hue += 360
    return round(hue, 2)


def process(release, force=False):
    """Fill in color fields on one release. Returns True if processed."""
    if not force and release.get("sort_hue") is not None:
        return False

    img_rel = release.get("image")
    if not img_rel:
        return False
    path = BASE_DIR / img_rel
    if not path.exists():
        return False

    palette, err = extract_palette(path)
    if not palette:
        return False

    sort_hue = compute_sort_hue(palette)

    # Representative color:
    #   - If sort_hue is achromatic (< 0), the cover reads as dark/light/mono.
    #     Pick the most-covered entry so the border tint matches the bucket
    #     instead of screaming with a tiny red accent that got scored high.
    #   - If chromatic, use the chroma-weighted dominant (already palette[0]).
    if sort_hue < 0:
        rep = max(palette, key=lambda e: e["frac"])
    else:
        rep = palette[0]

    top5 = palette[:TOP_N_RETURN]

    release["color"] = rep["hex"]
    release["colors"] = [e["hex"] for e in top5]
    release["hsl"] = {"hex": rep["hex"], "h": rep["h"], "s": rep["s"], "l": rep["l"]}
    release["sort_hue"] = sort_hue
    release["palette"] = [
        {"hex": e["hex"], "h": e["h"], "s": e["s"], "l": e["l"],
         "c": e["c"], "frac": e["frac"]}
        for e in top5
    ]
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="Recompute colors even if sort_hue already exists")
    ap.add_argument("--limit", type=int, default=None,
                    help="Only process N releases (for testing)")
    args = ap.parse_args()

    with open(RELEASES_FILE) as f:
        data = json.load(f)

    releases = data["releases"]
    processed = 0
    skipped = 0
    for i, r in enumerate(releases):
        if args.limit and processed >= args.limit:
            break
        if process(r, force=args.force):
            processed += 1
            if processed % 50 == 0:
                print(f"  [{i+1}/{len(releases)}] {processed} processed")
        else:
            skipped += 1

    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    # Stats
    with_hue = [r for r in releases if r.get("sort_hue") is not None]
    achromatic = sum(1 for r in with_hue if r["sort_hue"] < 0)
    print(f"\nDone: {processed} processed, {skipped} skipped")
    print(f"Total with sort_hue: {len(with_hue)} / {len(releases)}")
    print(f"  Achromatic: {achromatic}")
    print(f"  Chromatic:  {len(with_hue) - achromatic}")

    # Hue histogram
    if with_hue:
        buckets = [0] * 13
        for r in with_hue:
            h = r["sort_hue"]
            if h < 0:
                buckets[12] += 1
            else:
                buckets[int(h // 30) % 12] += 1
        names = ["red", "orange", "yellow", "y-green", "green", "cyan-g",
                 "cyan", "blue", "indigo", "purple", "magenta", "pink-red", "achromatic"]
        print("\nHue distribution:")
        for name, count in zip(names, buckets):
            bar = "█" * int(count / max(buckets) * 40) if max(buckets) else ""
            print(f"  {name:12} {count:4}  {bar}")


if __name__ == "__main__":
    main()
