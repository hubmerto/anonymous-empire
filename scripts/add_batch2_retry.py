#!/usr/bin/env python3
"""Retry failed queries from batch 2 with manually cleaned search terms."""

import collections
import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")

# Manually cleaned search queries with scene assignments
# Format: (search_query, scene)
RETRY = [
    ("Reeko Exium Regenerative Circuits Mental Disorder", "Spain"),
    ("Atom TM Ground Loop Bunker New York", "Germany"),
    ("Paul St Hilaire Ren Faith False Tuned", "Berlin"),
    ("Basic Channel Quadrant Dub", "Berlin"),
    ("Steve Bicknell Lost Recordings 7 Cosmic", "London"),
    ("Silent Servant In Memoriam Tresor", "London"),
    ("Sterac Skreelah Nemec M-Plant", "Netherlands"),
    ("Drexciya Deep Sea Dweller Shockwave", "Detroit"),
    ("Tin Man Love Sex Acid", "Netherlands"),
    ("Takaaki Itoh Things We've Made In Our Dreams Wols", "Japan"),
    ("VSK APM Records", "Spain"),
    ("Regis Application Of Language Downwards", "London"),
    ("Joel Inder Delusion Norrlands", "Sweden"),
    ("Orbe Final Musik", "Spain"),
    ("Luigi Tozzi Bios Non Series", "Italy"),
    ("Sunil Sharper Sounds Blueprint", "London"),
    ("Donato Dozzy Vapors Dance Tresor", "Italy"),
    ("Jeff Mills Everyday Life Purpose Maker", "Detroit"),
    ("Surgeon BAW Bad Sector", "London"),
    ("Sule Tuareg Kultur Dekmantel", "Netherlands"),
    ("Anthony Shakir Frictionless FXHE", "Detroit"),
    ("Cassegrain Collabs 02 Arcing Seas", "Berlin"),
    ("Marcus Adam BKLYN Infrastructure New York", "New York"),
    ("Reus Redefine Suba", "Spain"),
    ("Jeff Mills Microscopic Music Something", "Detroit"),
    ("Anton Pieete The News Rejected", "Berlin"),
    ("Oliver Rosemann Alexander Kowalski Muzzleblast", "Berlin"),
    ("Cirkle Sonic Surge Sublunar", "Berlin"),
    ("Blawan Bohm Ternesc", "London"),
    ("White Noise MXCLR", "Berlin"),
    ("Stroboscopic Artefacts Monad", "Berlin"),
    ("Eduardo De La Calle Inter Elementary Forms Analog Solutions", "Spain"),
    ("Grovskopa Letvagen Avian", "Sweden"),
    ("Mike Parker Inversion Geophone", "New York"),
    ("Peter Van Hoesen Cosmic Entropy Archives Interieures", "Ghent / Brussels"),
    ("Raster Noton compilation", "Berlin"),
    ("Truncate Untitled 78", "New York"),
    ("Modularz 11", "Berlin"),
    ("Jeff Mills If Tango Axis", "Detroit"),
    ("Jay Denham Shockwave", "Detroit"),
    ("Alva Noto Hybr:ID Noton", "Chemnitz / Dresden"),
    ("Donato Dozzy Filo Loves The Acid Tresor", "Italy"),
    ("Kwartz Form And Void Polegroup", "Spain"),
    ("Terence Fixmer Le Terrible Electric Deluxe", "France"),
    ("Eduardo De La Calle Rather Than Deep Semantica", "Spain"),
    ("Sleeparchive Tools Sketches", "Berlin"),
    ("Plastikman Chilly Gonzales Consumed In Key Turbo", "Canada"),
    ("Samuli Kemppi Dark Matter Mote Evolver", "Berlin"),
    ("Cassegrain Tin Man Infrastructure New York", "Berlin"),
    ("Regis In A Syrian Tongue Blackest Ever Black", "London"),
    ("Claude Young The Dexit Elypsia", "Detroit"),
    ("DJ Shufflemaster Elektronique Dweller Subvoice", "Japan"),
    ("Robert Hood Moveable Parts Chapter 2 M-Plant", "Detroit"),
    ("Sigha I Am Apathy I Am Submission Blueprint", "London"),
    ("DJ Surgeles Cosmic Distance Markers Techum", "Spain"),
    ("Pacou State Of Mind Tresor", "Berlin"),
    ("Kilner Walk Type Avian", "Berlin"),
    ("1st Bass Slammed Down NovaMute", "London"),
    ("Steve Bicknell Several Streams Of Thought KR3", "London"),
    ("Paperclip People Basic Reshape Basic Channel", "Detroit"),
    ("DJ Slip 808 To Nice Subvoice", "Japan"),
    ("Dis x3 Brothers In Mind Tresor", "Berlin"),
    ("Steve Rachmad Cosmic Harmony", "Netherlands"),
    ("Abdulla Rashim Ecstasy", "Sweden"),
    ("Takaaki Itoh Planet Rhythm Group", "Japan"),
    ("Svreca AW02 Semantica", "Spain"),
    ("Jeff Mills Chasing The Beat Axis", "Detroit"),
    ("Takaaki Itoh Fancy Haircut Planet Rhythm", "Japan"),
    ("Millsart Inner Life React", "Detroit"),
    ("Ryoji Ikeda Time And Space Staalplaat", "Japan"),
    ("Dax J Imperial Propaganda Monnom Black", "London"),
    ("Albert Van Abbe Raster", "Berlin"),
    ("Samuli Kemppi New Iron Age Power Of Voltages", "Berlin"),
    ("Concrete Lines compilation", "Berlin"),
    ("Astigmatic Vol 4", "Berlin"),
    ("Stanislav Tolkachev Nightshift Mote Evolver", "Georgia / Eastern Europe"),
    ("Luigi Tozzi Meridians", "Italy"),
    ("Svreca Incubation Process Semantica", "Spain"),
    ("Tresor Darklight compilation", "Berlin"),
    ("Silent Servant Negative Fascination Hospital Productions", "London"),
    ("Jeff Mills The Guardian Purpose Maker", "Detroit"),
    ("Agony Forces Wild Innocence", "Berlin"),
    ("Subsoil compilation Immaterial Archives", "Berlin"),
    ("Terrence Dixon Minimalism Revision Tresor", "Detroit"),
    ("Stanislav Tolkachev Walk Along The Bottom Mote Evolver", "Georgia / Eastern Europe"),
    ("426 Mono Middle", "Berlin"),
    ("Stockholm Limited Planets In Palm", "Sweden"),
    ("Chris Sattinger Think Less Thoughts", "Berlin"),
    ("DJ Slip Never Look Back Kid Subvoice", "Japan"),
    ("Regis Application Of Language Downwards", "London"),
    ("65D Mavericks Defining The Symptom Blueprint", "London"),
    ("Anthony Linell Emerald Fluorescents Northern Electronics", "Sweden"),
    ("Jeff Mills The Other Day Axis", "Detroit"),
    ("Svreca Reinhaled Semantica", "Spain"),
    ("Mike Parker Vesuvio Tremors Geophone", "New York"),
    ("Donato Dozzy Squadra Quadra Vos", "Italy"),
    ("British Murder Boys Counterbalance", "London"),
    ("Perc Modern Heads Perc Trax", "London"),
    ("Sleeparchive A Man Dies In The Street", "Berlin"),
    ("Fanon Flowers Hunt Patterns", "Berlin"),
    ("Mike Parker Vertebrae Waltz Geophone", "New York"),
    ("Damon Wild Synewave", "New York"),
    ("Blank Program We Need Input", "Germany"),
    ("Regis Divine Ritual Downwards", "London"),
    ("Pacou Reel Techno Tresor", "Berlin"),
    ("Takaaki Itoh Nobody Can Take What Everybody Owns Planet Rhythm", "Japan"),
    ("A Guy Called Gerald How Long Is Now Juice Box", "Manchester"),
    ("Chester Beatty Accelerate", "Japan"),
    ("Mike Parker Cyclic Intonations Geophone", "New York"),
    ("Chance McDermott Return Of The Prophet 600", "Detroit"),
    ("Jeff Rushin Irakli", "Georgia / Eastern Europe"),
    ("Spherical Coordinates Vector Projection", "Berlin"),
    ("Hallucinator Black Angel Chain Reaction", "Berlin"),
    ("Evigt Morker Helmet Of Bones Semantica", "Sweden"),
    ("Christian Wunsch False Flag Pole Recordings", "Germany"),
    ("Terrence Dixon Point Of View Finest Blend", "Detroit"),
    ("Marco Lenzi Unfinished Business Fine Audio", "Italy"),
    ("Inigo Kennedy The Difficult Third Asymmetric", "London"),
    ("Cadency Gazing In A Social Hub Cabrera", "Spain"),
    ("Answer Code Request Main Mode Marcel Dettmann", "Berlin"),
    ("Brendon Moeller Work Ethics Electric Deluxe", "Berlin"),
    ("DeepChord Functional Extraits Soma", "Detroit"),
    ("Function Various Plates", "New York"),
    ("Luigi Tozzi Bios 2 Non Series", "Italy"),
    ("Planetary Assault Systems Deep Bass Weight Ostgut", "Berlin"),
    ("VSK Rawax APM", "Spain"),
    ("Vakula Svreca Semantica", "Spain"),
    ("Orphx Night Music Sonic Groove", "Canada"),
    ("Reeko Aletheia Polegroup", "Spain"),
    ("Svreca AW05 Semantica", "Spain"),
    ("Surgeon Force And Form Dynamic Tension", "London"),
    ("Stanislav Tolkachev Looped Life Polegroup", "Georgia / Eastern Europe"),
    ("Klockworks compilation", "Berlin"),
    ("Planetary Assault Systems Planetary Funk Peacefrog", "Berlin"),
    ("Pacou A Universal Movement Tresor", "Berlin"),
    ("Abdulla Rashim Axel Hallqvist Sorunda", "Sweden"),
    ("Modular Side M", "Berlin"),
    ("Eduardo De La Calle My Own Transition Analog Solutions", "Spain"),
    ("SHXCXCHCXSH Strgths Rcnstrctns Avian", "Sweden"),
    ("Kvantti Semantica", "Spain"),
    ("UUN Sacred Seven SI Modern Cathedrals", "Berlin"),
    ("Oscar Mulero Elementary Geometry Faut Section", "Spain"),
    ("The Other People Place Lifestyles Of The Laptop Cafe Warp", "Detroit"),
    ("Steve Stoll Damon Wild Synewave", "New York"),
    ("Function Dielectric Coefficient Infrastructure", "New York"),
    ("Phil Kieran Jochem Paap Skudge", "London"),
    ("Oscar Mulero Black Propaganda Warm Up", "Spain"),
    ("Terrence Dixon Bionic Man Tresor", "Detroit"),
    ("Tresor Music From The Basement", "Berlin"),
    ("Fanon Flowers Hunt Patterns", "Berlin"),
    ("UVB What I've Learned", "Berlin"),
    ("Spectrum 33 On The 5th Day", "Berlin"),
    ("DJ ESP Sick And Tired", "Spain"),
    ("Semantica Non Native 04", "Spain"),
    ("DJ Nobu Extra Tools Future Noise", "Japan"),
    ("Geophone GPH 135 Mike Parker", "New York"),
    ("Stanislav Tolkachev The Fridge Mote Evolver", "Georgia / Eastern Europe"),
    ("Surgeon Convenience Trap Dynamic Tension", "London"),
    ("Cio D'Or Magnetfluss Prologue", "Italy"),
    ("Selected Edits 4", "Berlin"),
    ("Orphx Other Voices Sonic Groove", "Canada"),
    ("DC11 Stroboscopic Slow Motion", "Italy"),
    ("Abdulla Rashim Semi Enterara", "Sweden"),
    ("Wata Igarashi Counter Pulse Series 8", "Japan"),
    ("LSD Second Process Accelerate", "Japan"),
    ("Rene Wise Moving Pressure", "London"),
    ("Korridor Path Dynamic Reflection", "Germany"),
    ("Danza Nativa 5 Years compilation", "Spain"),
    ("Developer DJ Surgeles Developer Sound Works", "Berlin"),
    ("Hiroaki Iizuka The Run Them", "Japan"),
    ("Pearl Four Cardinal Falling Ethics", "Italy"),
    ("Warsaw Admixture Admiral", "Georgia / Eastern Europe"),
    ("DJ Shufflemaster Playback Part 3 Subvoice", "Japan"),
    ("Population One The Return M-Plant", "Detroit"),
    ("Paul Birken Acid Youth Of Malibu Ear Wiggle", "London"),
    ("Space DJZ Side On Peacefrog", "Detroit"),
    ("Iesope Drift People Drift Element", "Japan"),
    ("Christian Bor Life Divine Tresor", "Berlin"),
    ("Pacou Sound Device Tresor", "Berlin"),
    ("James Ruskin Into A Circle Blueprint", "London"),
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
                title_full = r.get("title", "")
                parts = title_full.split(" - ", 1)
                artist = parts[0].strip() if len(parts) > 1 else "Various"
                title = parts[1].strip() if len(parts) > 1 else title_full
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
    skipped = 0
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
            skipped += 1
            continue

        key = f"{result['artist'].lower()}|{result['title'].lower()}"
        if key in existing_titles:
            skipped += 1
            continue

        # Download image
        image_path = ""
        if result["thumb"]:
            dest = IMAGES_DIR / f"{result['id']}.jpg"
            if dest.exists() or download_image(result["thumb"], dest):
                image_path = f"images/{result['id']}.jpg"

        # Color
        color, colors = None, []
        full_img = SCRIPT_DIR.parent / image_path if image_path else None
        if full_img and full_img.exists():
            color, colors = extract_color(full_img)

        # Clean label from query
        label = query.split()[-1] if len(query.split()) > 2 else scene

        release = {
            "id": result["id"],
            "title": result["title"],
            "artist": result["artist"],
            "year": result["year"],
            "catno": result["catno"],
            "thumb": result["thumb"],
            "format": result["format"],
            "label": label,
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
            print(f"  [{i+1}/{len(RETRY)}] +{added} new, {skipped} skipped, {failed} failed")

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

    # Save
    data["releases"].sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r["year"] > 0]
    if years:
        data["meta"]["year_range"] = [min(years), max(years)]
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\n{'='*50}")
    print(f"Done: +{added} new, {skipped} skipped, {failed} not found")
    print(f"Total archive: {data['meta']['total']} releases")
    if fail_list:
        print(f"\nStill failed ({len(fail_list)}):")
        for q in fail_list:
            print(f"  - {q}")


if __name__ == "__main__":
    main()
