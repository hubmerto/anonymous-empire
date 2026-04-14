#!/usr/bin/env python3
"""Add specific important releases to the archive by searching Discogs."""

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

# Important releases from the research document + iconic techno canon
WANTED = [
    # Detroit pioneers
    {"q": "Cybotron Clear", "scene": "Detroit"},
    {"q": "Rhythim Is Rhythim Nude Photo", "scene": "Detroit"},
    {"q": "Rhythim Is Rhythim Strings Of Life", "scene": "Detroit"},
    {"q": "Model 500 No UFOs", "scene": "Detroit"},
    {"q": "Model 500 Night Drive", "scene": "Detroit"},
    {"q": "Drexciya Neptune's Lair", "scene": "Berlin"},
    {"q": "Drexciya Journey Of The Deep Sea Dweller", "scene": "Detroit"},
    {"q": "Drexciya Harnessed The Storm", "scene": "Detroit"},
    {"q": "Underground Resistance World 2 World", "scene": "Detroit"},
    {"q": "Underground Resistance Revolution For Change", "scene": "Detroit"},
    {"q": "Underground Resistance Final Frontier", "scene": "Detroit"},
    {"q": "Robert Hood Minimal Nation", "scene": "Detroit"},
    {"q": "Robert Hood Internal Empire", "scene": "Detroit"},
    {"q": "Jeff Mills Waveform Transmission", "scene": "Detroit"},
    {"q": "Jeff Mills Purpose Maker", "scene": "Detroit"},
    {"q": "Juan Atkins Deep Space", "scene": "Detroit"},
    {"q": "Carl Craig More Songs About Food And Revolutionary Art", "scene": "Detroit"},
    {"q": "Carl Craig Landcruising", "scene": "Detroit"},
    {"q": "Derrick May Innovator", "scene": "Detroit"},
    {"q": "Eddie Fowlkes Goodbye Kiss", "scene": "Detroit"},
    {"q": "Kevin Saunderson Face To Face", "scene": "Detroit"},
    {"q": "Blake Baxter Dream Sequence", "scene": "Detroit"},
    # Berlin
    {"q": "Tresor X-101", "scene": "Berlin"},
    {"q": "Tresor Scion", "scene": "Berlin"},
    {"q": "Basic Channel Quadrant Dub", "scene": "Berlin"},
    {"q": "Basic Channel Phylyps Trak", "scene": "Berlin"},
    {"q": "Moritz von Oswald Rhythm & Sound", "scene": "Berlin"},
    {"q": "Ostgut Ton Berghain 01", "scene": "Berlin"},
    {"q": "Ostgut Ton Berghain 02", "scene": "Berlin"},
    {"q": "Marcel Dettmann Dettmann", "scene": "Berlin"},
    {"q": "Ben Klock Subzero", "scene": "Berlin"},
    {"q": "BPitch Control Ellen Allien Berlinette", "scene": "Berlin"},
    {"q": "Stroboscopic Artefacts Lucy Wordplay", "scene": "Berlin"},
    {"q": "Dystopian Alex.Do Dust", "scene": "Berlin"},
    {"q": "Giegling Kettenkarussell", "scene": "Berlin"},
    # Raster-Noton / Chemnitz
    {"q": "Alva Noto Xerrox", "scene": "Chemnitz / Dresden"},
    {"q": "Alva Noto Unitxt", "scene": "Chemnitz / Dresden"},
    {"q": "Byetone Death Of A Typographer", "scene": "Chemnitz / Dresden"},
    # Sheffield / Warp
    {"q": "Warp Artificial Intelligence", "scene": "Sheffield / Leeds"},
    {"q": "LFO LFO", "scene": "Sheffield / Leeds"},
    {"q": "Nightmares On Wax Smokers Delight", "scene": "Sheffield / Leeds"},
    # London / UK
    {"q": "Surgeon Force + Form", "scene": "London"},
    {"q": "Regis Gymnastics", "scene": "London"},
    {"q": "Perc Trax Perc Wicker & Steel", "scene": "London"},
    {"q": "Blackest Ever Black Raime Quarter Turns", "scene": "London"},
    {"q": "Vatican Shadow Kneel Before Religious Authority", "scene": "New York"},
    {"q": "Sandwell District Feed Forward", "scene": "London"},
    {"q": "Burial Untrue", "scene": "London"},
    {"q": "Burial Burial", "scene": "London"},
    {"q": "Kode9 Memories Of The Future", "scene": "London"},
    # Cologne
    {"q": "Kompakt Total 1", "scene": "Cologne"},
    {"q": "Kompakt Pop Ambient 2001", "scene": "Cologne"},
    {"q": "Wolfgang Voigt Gas Konigsforst", "scene": "Cologne"},
    {"q": "Gas Narkopop", "scene": "Cologne"},
    # Munich
    {"q": "Skee Mask Compro", "scene": "Munich"},
    {"q": "Skee Mask Pool", "scene": "Munich"},
    {"q": "Ilian Tape Zenker Brothers", "scene": "Munich"},
    # Frankfurt
    {"q": "Mille Plateaux Clicks & Cuts", "scene": "Frankfurt"},
    # New York
    {"q": "L.I.E.S. Legowelt Smackos", "scene": "New York"},
    {"q": "L.I.E.S. Torn Hawk", "scene": "New York"},
    # PAN
    {"q": "PAN Lee Gamble Dutch Tvashar", "scene": "Berlin"},
    {"q": "PAN Objekt Flatland", "scene": "Berlin"},
    # Ghent
    {"q": "R&S Records Joey Beltram Energy Flash", "scene": "Ghent / Brussels"},
    {"q": "R&S Records Aphex Twin Didgeridoo", "scene": "Ghent / Brussels"},
    # Perlon (missing label)
    {"q": "Perlon Baby Ford", "scene": "Berlin"},
    {"q": "Perlon Ricardo Villalobos", "scene": "Berlin"},
    # Japan
    {"q": "Ken Ishii Jelly Tones", "scene": "Japan"},
    # Italy
    {"q": "Mannequin Records", "scene": "Italy"},
    # Manchester
    {"q": "Modern Love Andy Stott Luxury Problems", "scene": "Manchester"},
    {"q": "Modern Love Demdike Stare", "scene": "Manchester"},
]


def search_discogs(query, token):
    """Search Discogs for a release."""
    url = f"https://api.discogs.com/database/search?q={quote(query)}&type=release&per_page=3"
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
            if results:
                r = results[0]
                return {
                    "id": r.get("id"),
                    "title": r.get("title", "").split(" - ")[-1].strip() if " - " in r.get("title", "") else r.get("title", ""),
                    "artist": r.get("title", "").split(" - ")[0].strip() if " - " in r.get("title", "") else "Various",
                    "year": int(r.get("year", 0)) if r.get("year") else 0,
                    "catno": r.get("catno", ""),
                    "thumb": r.get("thumb", ""),
                    "format": ", ".join(r.get("format", [])) if isinstance(r.get("format"), list) else r.get("format", ""),
                }
    except Exception as e:
        print(f"  Error searching '{query}': {e}")
    return None


def download_image(url, dest_path):
    """Download an image."""
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
            time.sleep(0.05)
            return True
    except:
        return False


def main():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    existing_ids = {r["id"] for r in data["releases"]}
    added = 0

    for item in WANTED:
        result = search_discogs(item["q"], TOKEN)
        if not result:
            print(f"  NOT FOUND: {item['q']}")
            continue

        if result["id"] in existing_ids:
            print(f"  EXISTS: {result['artist']} - {result['title']}")
            continue

        # Download image
        image_path = ""
        if result["thumb"]:
            IMAGES_DIR.mkdir(parents=True, exist_ok=True)
            dest = IMAGES_DIR / f"{result['id']}.jpg"
            if dest.exists() or download_image(result["thumb"], dest):
                image_path = f"images/{result['id']}.jpg"

        # Extract color
        color = None
        colors = []
        if image_path:
            try:
                from PIL import Image
                import collections
                full_path = SCRIPT_DIR.parent / image_path
                img = Image.open(full_path).convert("RGB").resize((32, 32))
                pixels = list(img.getdata())
                counts = collections.Counter()
                for pr, pg, pb in pixels:
                    lightness = (pr + pg + pb) / 3
                    if lightness < 10 or lightness > 245:
                        continue
                    counts[(pr >> 4, pg >> 4, pb >> 4)] += 1
                if counts:
                    top = counts.most_common(3)
                    for (qr, qg, qb), _ in top:
                        colors.append(f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}")
                    color = colors[0]
            except:
                pass

        release = {
            "id": result["id"],
            "title": result["title"],
            "artist": result["artist"],
            "year": result["year"],
            "catno": result["catno"],
            "thumb": result["thumb"],
            "format": result["format"],
            "label": item["q"].split()[0] if " " in item["q"] else item["q"],
            "label_id": 0,
            "scene": item["scene"],
            "discogs_url": f"https://www.discogs.com/release/{result['id']}",
            "image": image_path,
            "color": color,
            "colors": colors,
        }

        data["releases"].append(release)
        existing_ids.add(result["id"])
        added += 1
        print(f"  ADDED: {result['artist']} - {result['title']} ({result['year']})")

    # Re-sort and update meta
    data["releases"].sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r["year"] > 0]
    data["meta"]["year_range"] = [min(years, default=0), max(years, default=0)]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nAdded {added} releases. Total: {data['meta']['total']}")


if __name__ == "__main__":
    main()
