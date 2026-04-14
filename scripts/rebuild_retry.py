#!/usr/bin/env python3
"""Retry failed entries with shorter/simpler queries."""

import collections
import hashlib
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

# Simplified queries — shorter = better for Discogs
RETRY = [
    ("Atom Heart Ground Loop", "Germany"),
    ("Delete Everything Sub Records", "London"),
    ("Stephen Brown Afterlife Djax", "Netherlands"),
    ("Paul St. Hilaire Tikiman", "Berlin"),
    ("Sterac Electronics M-Plant", "Netherlands"),
    ("Bunker 4008", "Netherlands"),
    ("Richie Hawtin Boot Records", "Canada"),
    ("Takaaki Itoh WOLS008", "Japan"),
    ("Nihad Tule STHLM LTD", "Sweden"),
    ("VSK APM", "Spain"),
    ("Joel Linder Norrlands", "Sweden"),
    ("Orbe VS Final Musik", "Spain"),
    ("Luigi Tozzi Bios", "Italy"),
    ("Developer Archive 09 Korridor", "Berlin"),
    ("Sunil Blueprint Records", "London"),
    ("Charlton Tar Hallow TAR020", "London"),
    ("Donato Dozzy Tresor", "Italy"),
    ("Jeff Mills Purpose Maker", "Detroit"),
    ("Dimi Angélis Prologue", "Netherlands"),
    ("Surgeon Bad Sector", "London"),
    ("Sule Dekmantel", "Netherlands"),
    ("Anthony Shakir FXHE", "Detroit"),
    ("Shifted Avian Records", "Berlin"),
    ("Diversity Of Electronica", "Berlin"),
    ("Cassegrain Arcing Seas", "Berlin"),
    ("Tolkachev Mote-Evolver", "Georgia / Eastern Europe"),
    ("Charlton Tar Hallow TAR017", "London"),
    ("Marcus Adam Infrastructure", "New York"),
    ("Reus Suba", "Spain"),
    ("Jeff Mills Microscopic Music", "Detroit"),
    ("James Ruskin Blueprint", "London"),
    ("VSK Ear To Ground", "Spain"),
    ("Peter Van Hoesen Time To Express", "Ghent / Brussels"),
    ("Blawan Ternesc", "London"),
    ("White Noise MXCLR", "Berlin"),
    ("Stroboscopic Artefacts", "Berlin"),
    ("Eduardo De La Calle Analog Solutions", "Spain"),
    ("Grovskopa Avian", "Sweden"),
    ("Takaaki Itoh WOLS", "Japan"),
    ("CTSN Herdplatten Records", "Germany"),
    ("Peter Van Hoesen Archives Intérieures", "Ghent / Brussels"),
    ("Efdemin Decay", "Hamburg"),
    ("Truncate 78", "New York"),
    ("Oscar Mulero Warm Up", "Spain"),
    ("KVNT Semantica", "Spain"),
    ("Jay Denham Shockwave", "Detroit"),
    ("Nihad Tule Stockholm LTD", "Sweden"),
    ("Sleeparchive Tools Sketches", "Berlin"),
    ("Steven Porter Wevil", "London"),
    ("Anthony Rother Omnitronic", "Germany"),
    ("APM Translated", "Spain"),
    ("Developer Dynamic Reflection", "Berlin"),
    ("1st Bass NovaMute", "London"),
    ("Steve Rachmad Harmony", "Netherlands"),
    ("Developer Archive Dynamic Reflection", "Berlin"),
    ("Abdulla Rashim", "Sweden"),
    ("Takaaki Itoh Planet Rhythm", "Japan"),
    ("Svreca Semantica AW", "Spain"),
    ("Jeff Mills Axis Records", "Detroit"),
    ("Albert Van Abbe Raster", "Berlin"),
    ("Biosphere Novelty Waves", "Scandinavia"),
    ("Tolkachev Nightshift", "Georgia / Eastern Europe"),
    ("Surgeon Blueprint Unnatural", "London"),
    ("Luigi Tozzi Meridian", "Italy"),
    ("Developer Archive 7", "Berlin"),
    ("Svreca Incubation", "Spain"),
    ("Tresor Darklight", "Berlin"),
    ("Jeff Mills Guardian", "Detroit"),
    ("Immaterial Archives Subsoil", "Berlin"),
    ("Terrence Dixon Tresor", "Detroit"),
    ("Tolkachev Walk Bottom", "Georgia / Eastern Europe"),
    ("Woody McBride Peacefrog", "Detroit"),
    ("Chris Sattinger", "Berlin"),
    ("DJ Slip Subvoice", "Japan"),
    ("Steve Stoll Synewave", "New York"),
    ("Takaaki Itoh Electrique", "Japan"),
    ("Fumiya Tanaka Sundance", "Japan"),
    ("Svreca Reinhaled", "Spain"),
    ("Jonas Kopp Figure", "Berlin"),
    ("Donato Dozzy Squadra", "Italy"),
    ("Killawatt UK Red", "London"),
    ("Perc Trax Modern", "London"),
    ("Developer Archive Dynamic Reflection 09", "Berlin"),
    ("Biosphere Rands", "Scandinavia"),
    ("Takaaki Itoh Planet Rhythm nobody", "Japan"),
    ("Chester Beatty Accelerate", "Japan"),
    ("Phil Barton Blueprint", "London"),
    ("Mike Parker Geophone cyclic", "New York"),
    ("Steve Stoll Synewave Eldopa", "New York"),
    ("Jay Denham Carjacker", "Detroit"),
    ("Cerrone DJ Hell", "France"),
    ("Jeff Rushin Irakli", "Georgia / Eastern Europe"),
    ("Luigi Tozzi Non Series bios", "Italy"),
    ("Planetary Assault Systems Ostgut", "Berlin"),
    ("VSK APM rawax", "Spain"),
    ("Vakula Semantica", "Spain"),
    ("Function Infrastructure adjustments", "New York"),
    ("Orphx Sonic Groove night", "Canada"),
    ("Reeko Polegroup", "Spain"),
    ("Svreca AW Semantica", "Spain"),
    ("Fumiya Tanaka Perlon", "Japan"),
    ("Tolkachev Polegroup looped", "Georgia / Eastern Europe"),
    ("Klockworks compilation", "Berlin"),
    ("Charlton TAR016 Tar Hallow", "London"),
    ("Sliwinski Speaker Attack", "Netherlands"),
    ("Tolkachev Acropolis 24H", "Georgia / Eastern Europe"),
    ("Bandulu Basic Channel", "Berlin"),
    ("Kvantti", "Spain"),
    ("UUN Modern Cathedrals", "Berlin"),
    ("Sleeparchive Papercup", "Berlin"),
    ("Phil Kieran Skudge", "London"),
    ("Orbe Psyk", "Spain"),
    ("Conrad Van Orton APM", "Spain"),
    ("Trautmuzik Basement", "Berlin"),
    ("Rumenige Raummusik", "Berlin"),
    ("Adriana Lopez Semantica", "Spain"),
    ("Claudio PRC Figure", "Italy"),
    ("Jeroen Search Figure", "Netherlands"),
    ("Semantica Nonnative", "Spain"),
    ("Jonas Kopp Figure", "Berlin"),
    ("DJ Nobu Future Noise", "Japan"),
    ("Tolkachev Fridge", "Georgia / Eastern Europe"),
    ("Nihad Tule Bauri", "Sweden"),
    ("Jesper Dahlbäck Norrlands", "Sweden"),
    ("Troy Dynamic Reflection", "Berlin"),
    ("Orphx Sonic Groove voices", "Canada"),
    ("Marco Shuttle Dynavision", "Italy"),
    ("Abdulla Rashim Semi", "Sweden"),
    ("LSD Accelerate Records", "Japan"),
    ("Reeko Mental Disorder architectural", "Spain"),
    ("Korridor Records", "Germany"),
    ("Danza Nativa", "Spain"),
    ("Developer Surgeles", "Berlin"),
    ("Raiz Lo-Fi", "Italy"),
    ("Warsaw Admiral Records", "Georgia / Eastern Europe"),
    ("DJ Shufflemaster Subvoice playback", "Japan"),
    ("Paul Birken Ear Wiggle", "London"),
    ("Space DJz Peacefrog", "Detroit"),
    ("Blunted Boy Wonder Alphabet Set", "Detroit"),
    ("Christian Bor Tresor", "Berlin"),
    ("Keith Tucker Synthetic", "Detroit"),
    ("Pacou Tresor sound device", "Berlin"),
    ("Steve O'Sullivan Mosaic", "London"),
    ("Roiseux Editions Mego", "Germany"),
]


def search_discogs(query):
    url = f"https://api.discogs.com/database/search?q={quote(query)}&type=release&per_page=5"
    headers = {
        "User-Agent": "TechnoVisualArchive/1.0",
        "Authorization": f"Discogs token={TOKEN}",
        "Accept": "application/json",
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            time.sleep(1.1)
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            if results:
                r = results[0]
                tf = r.get("title", "")
                parts = tf.split(" - ", 1)
                artist = parts[0].strip() if len(parts) > 1 else "Various"
                title = parts[1].strip() if len(parts) > 1 else tf
                return {
                    "id": r.get("id"),
                    "title": title,
                    "artist": artist,
                    "year": int(r.get("year", 0)) if r.get("year") else 0,
                    "catno": r.get("catno", ""),
                    "thumb": r.get("thumb", ""),
                    "format": ", ".join(r.get("format", []))
                    if isinstance(r.get("format"), list)
                    else str(r.get("format", "")),
                }
    except Exception as e:
        print(f"  ERR: {e}")
    return None


def download_image(url, dest):
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(dest, "wb") as f:
                    f.write(data)
                return True
    except:
        pass
    return False


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
            colors = [f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}" for (qr, qg, qb), _ in top]
            return colors[0], colors
    except:
        pass
    return None, []


def main():
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    existing_ids = {r["id"] for r in data["releases"]}
    existing_titles = {f"{r['artist'].lower()}|{r['title'].lower()}" for r in data["releases"]}
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    added = 0
    failed = 0
    fail_list = []

    for i, (query, scene) in enumerate(RETRY):
        result = search_discogs(query)
        if not result:
            print(f"  NOT FOUND [{i+1}]: {query}")
            fail_list.append(query)
            failed += 1
            continue

        if result["id"] in existing_ids:
            continue
        key = f"{result['artist'].lower()}|{result['title'].lower()}"
        if key in existing_titles:
            continue

        image_path = ""
        if result["thumb"]:
            dest = IMAGES_DIR / f"{result['id']}.jpg"
            if dest.exists() or download_image(result["thumb"], dest):
                image_path = f"images/{result['id']}.jpg"

        color, colors = None, []
        full_img = SCRIPT_DIR.parent / image_path if image_path else None
        if full_img and full_img.exists():
            color, colors = extract_color(full_img)

        release = {
            "id": result["id"],
            "title": result["title"],
            "artist": result["artist"],
            "year": result["year"],
            "catno": result["catno"],
            "thumb": result["thumb"],
            "format": result["format"],
            "label": query.split()[-1] if len(query.split()) > 1 else scene,
            "label_id": 0,
            "scene": scene,
            "discogs_url": f"https://www.discogs.com/release/{result['id']}",
            "image": image_path,
            "color": color,
            "colors": colors or [],
        }

        data["releases"].append(release)
        existing_ids.add(result["id"])
        existing_titles.add(key)
        added += 1

        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(RETRY)}] +{added} new, {failed} failed")

    # Dedup by cover hash
    hash_seen = set()
    no_dupe = []
    for r in data["releases"]:
        img = r.get("image", "")
        full = SCRIPT_DIR.parent / img if img else None
        if full and full.exists():
            h = hashlib.md5(open(full, "rb").read()).hexdigest()
            if h in hash_seen:
                continue
            hash_seen.add(h)
        no_dupe.append(r)
    data["releases"] = no_dupe

    data["releases"].sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r["year"] > 0]
    if years:
        data["meta"]["year_range"] = [min(years), max(years)]
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nDone: +{added} new, {failed} not found")
    print(f"Total archive: {data['meta']['total']} releases")
    if fail_list:
        print(f"\nStill not found ({len(fail_list)}):")
        for q in fail_list:
            print(f"  - {q}")


if __name__ == "__main__":
    main()
