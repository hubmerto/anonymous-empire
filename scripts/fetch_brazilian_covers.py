#!/usr/bin/env python3
"""
Fetch cover art from Discogs for Brazilian releases (no image yet).
Downloads full-size images, not just thumbnails.
"""

import collections
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
RELEASES_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")


def search_discogs(artist, title, label=""):
    """Search Discogs for a release. Returns (release_id, thumb_url) or None."""
    # Clean query
    query = f"{artist} {title}"
    query = query.replace(" / ", " ").replace(" & ", " ")

    url = (
        f"https://api.discogs.com/database/search?q={quote(query)}"
        f"&type=release&per_page=5"
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
                thumb = r.get("thumb", "")
                rid = r.get("id", 0)
                if thumb and rid:
                    return rid, thumb
    except Exception as e:
        print(f"    Search error: {e}")
    return None


def get_full_image(release_id):
    """Fetch full-size image URL from Discogs release page."""
    url = f"https://api.discogs.com/releases/{release_id}"
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={TOKEN}",
        "Accept": "application/json",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            images = data.get("images", [])
            if images:
                # Prefer primary image
                for img in images:
                    if img.get("type") == "primary":
                        return img.get("resource_url") or img.get("uri", "")
                # Fallback to first image
                return images[0].get("resource_url") or images[0].get("uri", "")
    except Exception as e:
        print(f"    Full image error: {e}")
    return None


def download_image(url, dest):
    """Download image to file."""
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(dest, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        print(f"    Download error: {e}")
    return False


def extract_colors(path):
    """Extract dominant colors from image."""
    try:
        from PIL import Image
        import colorsys, math
        img = Image.open(path).convert("RGB").resize((64, 64), Image.LANCZOS)
        pixels = list(img.getdata())
        counts = collections.Counter()
        for r, g, b in pixels:
            brightness = (r + g + b) / 3
            if brightness < 15 or brightness > 240:
                continue
            qr = (r >> 3) << 3
            qg = (g >> 3) << 3
            qb = (b >> 3) << 3
            counts[(qr, qg, qb)] += 1
        if not counts:
            for r, g, b in pixels:
                qr = (r >> 3) << 3
                qg = (g >> 3) << 3
                qb = (b >> 3) << 3
                counts[(qr, qg, qb)] += 1
        if not counts:
            return None
        top = counts.most_common(5)
        palette = []
        for (qr, qg, qb), _ in top:
            cr, cg, cb = min(qr+4, 255), min(qg+4, 255), min(qb+4, 255)
            hex_c = f"#{cr:02x}{cg:02x}{cb:02x}"
            h, l, s = colorsys.rgb_to_hls(cr/255, cg/255, cb/255)
            palette.append({"hex": hex_c, "h": round(h*360, 1), "s": round(s*100, 1), "l": round(l*100, 1)})

        # Compute sort_hue
        avg_sat = sum(c["s"] for c in palette[:3]) / min(3, len(palette))
        if avg_sat < 10:
            avg_l = sum(c["l"] for c in palette[:3]) / min(3, len(palette))
            sort_hue = -1 + (avg_l / 100)
        else:
            total_w, hx, hy = 0, 0, 0
            for c in palette[:3]:
                w = c["s"]
                rad = math.radians(c["h"])
                hx += math.cos(rad) * w
                hy += math.sin(rad) * w
                total_w += w
            avg_hue = math.degrees(math.atan2(hy/total_w, hx/total_w))
            if avg_hue < 0: avg_hue += 360
            sort_hue = avg_hue

        return {
            "color": palette[0]["hex"],
            "colors": [c["hex"] for c in palette],
            "hsl": palette[0],
            "sort_hue": round(sort_hue, 2),
            "palette": palette,
        }
    except Exception:
        return None


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with open(RELEASES_FILE) as f:
        data = json.load(f)

    # Find releases without images
    missing = [r for r in data["releases"] if not r.get("image")]
    print(f"Releases without covers: {len(missing)}")

    found = 0
    for i, r in enumerate(missing):
        artist = r["artist"]
        title = r["title"]
        label = r.get("label", "")

        print(f"  [{i+1}/{len(missing)}] {artist} — {title}", end="")

        # Search Discogs
        result = search_discogs(artist, title, label)
        time.sleep(1.05)

        if not result:
            # Try with label
            if label and label not in ("Self-Released", "Unknown"):
                result = search_discogs(artist, title + " " + label)
                time.sleep(1.05)

        if not result:
            print("  → not found")
            continue

        rid, thumb_url = result

        # Try to get full-size image
        full_url = get_full_image(rid)
        time.sleep(1.05)

        img_url = full_url or thumb_url
        dest = IMAGES_DIR / f"cover_{r['id']}.jpg"

        if download_image(img_url, dest):
            r["image"] = f"images/cover_{r['id']}.jpg"

            # Extract colors
            color_data = extract_colors(dest)
            if color_data:
                r["color"] = color_data["color"]
                r["colors"] = color_data["colors"]
                r["hsl"] = color_data["hsl"]
                r["sort_hue"] = color_data["sort_hue"]
                r["palette"] = color_data["palette"]

            found += 1
            print(f"  → ✓ (Discogs #{rid})")
        else:
            print(f"  → download failed")

        # Save checkpoint every 10
        if (i + 1) % 10 == 0:
            with open(RELEASES_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  --- Saved ({found} covers found) ---")

    # Final save
    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nDone: found {found}/{len(missing)} covers")


if __name__ == "__main__":
    main()
