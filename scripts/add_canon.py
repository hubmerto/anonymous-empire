#!/usr/bin/env python3
"""Add the techno canon — ~500 iconic releases searched by name."""

import collections
import hashlib
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

# The techno canon — iconic releases by scene
RELEASES = [
    # === DETROIT ===
    ("Cybotron - Alleys of Your Mind", "Detroit"),
    ("Cybotron - Clear", "Detroit"),
    ("Cybotron - Techno City", "Detroit"),
    ("Cybotron - Cosmic Cars", "Detroit"),
    ("Model 500 - No UFOs", "Detroit"),
    ("Model 500 - Night Drive Thru-Babylon", "Detroit"),
    ("Model 500 - The Chase", "Detroit"),
    ("Model 500 - Starlight", "Detroit"),
    ("Model 500 - Off To Battle", "Detroit"),
    ("Rhythim Is Rhythim - Nude Photo", "Detroit"),
    ("Rhythim Is Rhythim - Strings of Life", "Detroit"),
    ("Rhythim Is Rhythim - It Is What It Is", "Detroit"),
    ("Rhythim Is Rhythim - The Dance", "Detroit"),
    ("Eddie Flashin Fowlkes - Goodbye Kiss", "Detroit"),
    ("Blake Baxter - Dream Sequence", "Detroit"),
    ("Blake Baxter - When We Used To Play", "Detroit"),
    ("Reese Santonio - The Sound", "Detroit"),
    ("Inner City - Big Fun", "Detroit"),
    ("Inner City - Good Life", "Detroit"),
    ("Kevin Saunderson - Faces Phases", "Detroit"),
    ("E-Dancer - Heavenly", "Detroit"),
    ("Underground Resistance - Sonic Destroyer", "Detroit"),
    ("Underground Resistance - World 2 World", "Detroit"),
    ("Underground Resistance - Revolution For Change", "Detroit"),
    ("Underground Resistance - Message to the Majors", "Detroit"),
    ("Underground Resistance - Riot", "Detroit"),
    ("Underground Resistance - Final Frontier", "Detroit"),
    ("Galaxy 2 Galaxy - Hi-Tech Jazz", "Detroit"),
    ("The Martian - Star Dancer", "Detroit"),
    ("X-101 - X-101", "Detroit"),
    ("X-102 - Discovers the Rings of Saturn", "Detroit"),
    ("Jeff Mills - Waveform Transmission Vol 1", "Detroit"),
    ("Jeff Mills - The Bells", "Detroit"),
    ("Jeff Mills - Changes of Life", "Detroit"),
    ("Jeff Mills - The Exhibitionist", "Detroit"),
    ("Robert Hood - Minimal Nation", "Detroit"),
    ("Robert Hood - Internal Empire", "Detroit"),
    ("Robert Hood - Nighttime World", "Detroit"),
    ("Robert Hood - Protein Valve", "Detroit"),
    ("Carl Craig - Landcruising", "Detroit"),
    ("Carl Craig - More Songs About Food", "Detroit"),
    ("Carl Craig - 4 Jazz Funk Classics", "Detroit"),
    ("Paperclip People - Throw", "Detroit"),
    ("Innerzone Orchestra - Bug in the Bass Bin", "Detroit"),
    ("Drexciya - Aquatic Invasion", "Detroit"),
    ("Drexciya - Neptune's Lair", "Detroit"),
    ("Drexciya - Harnessed the Storm", "Detroit"),
    ("Drexciya - Grava 4", "Detroit"),
    ("Drexciya - Journey of the Deep Sea Dweller", "Detroit"),
    ("Moodymann - Silentintroduction", "Detroit"),
    ("Moodymann - Forevernevermore", "Detroit"),
    ("Theo Parrish - First Floor", "Detroit"),
    ("Theo Parrish - Parallel Dimensions", "Detroit"),
    ("Stacey Pullen - Silent Phase", "Detroit"),
    ("Kenny Larkin - Azimuth", "Detroit"),
    ("Kenny Larkin - Metaphor", "Detroit"),
    ("Kenny Larkin - Dark Comedy", "Detroit"),
    ("Octave One - Blackwater", "Detroit"),
    ("Octave One - I Believe", "Detroit"),
    ("Anthony Shakir - Frictionalism", "Detroit"),
    ("Derrick May - Innovator", "Detroit"),
    ("Juan Atkins - Deep Space", "Detroit"),
    ("Mike Huckaby - Deep Transportation", "Detroit"),
    ("Terrence Parker - Loves Got Me High", "Detroit"),
    ("Aux 88 - Bass Magnetic", "Detroit"),
    ("Aux 88 - Is It Man or Machine", "Detroit"),
    ("DJ Bone - Subject to Change", "Detroit"),
    ("Plastikman - Sheet One", "Detroit"),
    ("Plastikman - Musik", "Detroit"),
    ("Plastikman - Consumed", "Detroit"),
    ("F.U.S.E. - Dimension Intrusion", "Detroit"),
    ("Random Noise Generation - Ambulance", "Detroit"),
    # === BERLIN ===
    ("Basic Channel - BCD", "Berlin"),
    ("Basic Channel - Phylyps Trak", "Berlin"),
    ("Basic Channel - Quadrant Dub", "Berlin"),
    ("Maurizio - M4", "Berlin"),
    ("Maurizio - M7", "Berlin"),
    ("Porter Ricks - Biokinetics", "Berlin"),
    ("Monolake - Hongkong", "Berlin"),
    ("Fluxion - Vibrant Forms", "Berlin"),
    ("Vainqueur - Elevation", "Berlin"),
    ("Shinichi Atobe - Ship-Scope", "Berlin"),
    ("Marcel Dettmann - Dettmann", "Berlin"),
    ("Marcel Dettmann - Dettmann II", "Berlin"),
    ("Ben Klock - One", "Berlin"),
    ("Ben Klock - Subzero", "Berlin"),
    ("Shed - Shedding The Past", "Berlin"),
    ("Shed - The Traveller", "Berlin"),
    ("Steffi - Yours Mine", "Berlin"),
    ("Ellen Allien - Stadtkind", "Berlin"),
    ("Ellen Allien - Berlinette", "Berlin"),
    ("Ellen Allien Apparat - Orchestra Of Bubbles", "Berlin"),
    ("Apparat - Walls", "Berlin"),
    ("Apparat - Multifunktionsebene", "Berlin"),
    ("Lucy - Wordplay For Working Bees", "Berlin"),
    ("Lucy - Totem", "Berlin"),
    ("Rrose - Triptych", "Berlin"),
    ("Eomac - Spoock", "Berlin"),
    ("Traumprinz - Mothercave", "Berlin"),
    ("Leafar Legov - Elaine", "Berlin"),
    ("Rodhad - Woo Doo", "Berlin"),
    ("Recondite - Hinterland", "Berlin"),
    ("Errorsmith - Superlative Fatigue", "Berlin"),
    ("M.E.S.H. - Hesaitix", "Berlin"),
    ("Amnesia Scanner - Another Life", "Berlin"),
    ("Objekt - Flatland", "Berlin"),
    ("Lee Gamble - Dutch Tvashar Plumes", "Berlin"),
    ("Moritz von Oswald Trio - Horizontal Structures", "Berlin"),
    ("Rhythm Sound - The Versions", "Berlin"),
    ("Monolake - Gravity", "Berlin"),
    ("Thomas Brinkmann - Klick Revolution", "Berlin"),
    ("Berghain 01 Andre Galluzzi", "Berlin"),
    ("Berghain 02 Marcel Dettmann", "Berlin"),
    ("Tresor Never Sleeps", "Berlin"),
    ("Sandwell District - Feed-Forward", "Berlin"),
    ("Kettenkarussell - Insecurity Guard", "Berlin"),
    ("Phase Fatale - Alcatraz", "Berlin"),
    ("Headless Horseman - Alpha Sector", "Berlin"),
    ("Tommy Four Seven - Primate", "Berlin"),
    # === COLOGNE ===
    ("Gas - Pop", "Cologne"),
    ("Gas - Narkopop", "Cologne"),
    ("Gas - Königsforst", "Cologne"),
    ("Gas - Zauberberg", "Cologne"),
    ("Gas - Oktember", "Cologne"),
    ("Wolfgang Voigt - Rückverzauberung", "Cologne"),
    ("Kompakt Total 1", "Cologne"),
    ("Pop Ambient 2001", "Cologne"),
    ("Dettinger - Intershop", "Cologne"),
    ("Dettinger - Oasis", "Cologne"),
    ("Michael Mayer - Immer", "Cologne"),
    ("Robag Wruhme - Wuppdeckmischmampflow", "Cologne"),
    ("Ricardo Villalobos - Thé Au Harem D'Archimède", "Cologne"),
    ("Ricardo Villalobos - Alcachofa", "Cologne"),
    ("Ricardo Villalobos - Fizheuer Zieheuer", "Cologne"),
    ("Thomas Brinkmann - Anna", "Cologne"),
    ("Akufen - The Unexpected Guest", "Cologne"),
    ("STL - Purple Saturn Days", "Cologne"),
    ("Margaret Dygas - Even 11", "Cologne"),
    ("Extrawelt - Soopertrack", "Cologne"),
    # === FRANKFURT ===
    ("Oval - Wohnton", "Frankfurt"),
    ("Pole - 1", "Frankfurt"),
    ("Pole - 2", "Frankfurt"),
    ("Jan Jelinek - Loop-Finding-Jazz-Records", "Frankfurt"),
    ("Clicks Cuts", "Frankfurt"),
    ("Isolée - Rest", "Frankfurt"),
    ("Roman Flügel - Fatty Folders", "Frankfurt"),
    ("Atom Heart - Datacide", "Frankfurt"),
    # === HAMBURG ===
    ("Efdemin - Efdemin", "Hamburg"),
    ("Efdemin - Chicago", "Hamburg"),
    ("Efdemin - Decay", "Hamburg"),
    ("Pantha du Prince - This Bliss", "Hamburg"),
    ("Pantha du Prince - Black Noise", "Hamburg"),
    ("Lawrence - Yoyogi Park", "Hamburg"),
    ("Benjamin Brunn - Songs From The Beehive", "Hamburg"),
    # === MUNICH ===
    ("Skee Mask - Compro", "Munich"),
    ("Skee Mask - Pool", "Munich"),
    ("Zenker Brothers - Immersion", "Munich"),
    ("DJ Hell - Geteert Gefedert", "Munich"),
    ("DJ Hell - Munich Machine", "Munich"),
    ("Ilian Tape Decade", "Munich"),
    # === CHEMNITZ / DRESDEN ===
    ("Alva Noto - Transform", "Chemnitz / Dresden"),
    ("Alva Noto - Unitxt", "Chemnitz / Dresden"),
    ("Alva Noto - Xerrox Vol 1", "Chemnitz / Dresden"),
    ("Alva Noto - Xerrox Vol 2", "Chemnitz / Dresden"),
    ("Byetone - Death of a Typographer", "Chemnitz / Dresden"),
    ("Byetone - Symeta", "Chemnitz / Dresden"),
    ("Frank Bretschneider - Rhythm", "Chemnitz / Dresden"),
    ("Ryoji Ikeda - Dataplex", "Chemnitz / Dresden"),
    ("Kangding Ray - Or", "Chemnitz / Dresden"),
    ("Mark Fell - Multistability", "Chemnitz / Dresden"),
    # === SHEFFIELD / LEEDS ===
    ("Autechre - Incunabula", "Sheffield / Leeds"),
    ("Autechre - Amber", "Sheffield / Leeds"),
    ("Autechre - Tri Repetae", "Sheffield / Leeds"),
    ("Autechre - Chiastic Slide", "Sheffield / Leeds"),
    ("Autechre - Confield", "Sheffield / Leeds"),
    ("Aphex Twin - Selected Ambient Works 85-92", "Sheffield / Leeds"),
    ("Aphex Twin - Selected Ambient Works Volume II", "Sheffield / Leeds"),
    ("Aphex Twin - Richard D James Album", "Sheffield / Leeds"),
    ("Aphex Twin - Come to Daddy", "Sheffield / Leeds"),
    ("Aphex Twin - Windowlicker", "Sheffield / Leeds"),
    ("LFO - LFO", "Sheffield / Leeds"),
    ("LFO - Frequencies", "Sheffield / Leeds"),
    ("Boards of Canada - Music Has the Right to Children", "Sheffield / Leeds"),
    ("Boards of Canada - Geogaddi", "Sheffield / Leeds"),
    ("Squarepusher - Feed Me Weird Things", "Sheffield / Leeds"),
    ("Squarepusher - Hard Normal Daddy", "Sheffield / Leeds"),
    ("The Black Dog - Bytes", "Sheffield / Leeds"),
    ("The Black Dog - Spanners", "Sheffield / Leeds"),
    ("Sweet Exorcist - Clonk", "Sheffield / Leeds"),
    ("Nightmares on Wax - A Word of Science", "Sheffield / Leeds"),
    ("Speedy J - Ginger", "Sheffield / Leeds"),
    # === LONDON ===
    ("Burial - Burial", "London"),
    ("Burial - Untrue", "London"),
    ("Burial - Rival Dealer", "London"),
    ("Burial - Kindred", "London"),
    ("Surgeon - Basictonalvocabulary", "London"),
    ("Surgeon - Force Form", "London"),
    ("Surgeon - Balance", "London"),
    ("Surgeon - Breaking the Frame", "London"),
    ("Regis - Gymnastics", "London"),
    ("Regis - Penetration", "London"),
    ("British Murder Boys", "London"),
    ("Perc - Wicker Steel", "London"),
    ("Perc - The Power the Glory", "London"),
    ("Raime - Quarter Turns Over a Living Line", "London"),
    ("Kode9 Spaceape - Memories of the Future", "London"),
    ("Kode9 - Nothing", "London"),
    ("The Bug - London Zoo", "London"),
    ("Darkstar - North", "London"),
    ("Pearson Sound", "London"),
    ("Joy Orbison - Hyph Mngo", "London"),
    ("Blawan - Getting Me Down", "London"),
    ("Broken English Club - English Beach", "London"),
    ("Andy Stott - Passed Me By", "Manchester"),
    ("Andy Stott - Luxury Problems", "Manchester"),
    ("Andy Stott - Faith in Strangers", "Manchester"),
    ("Demdike Stare - Tryptych", "Manchester"),
    ("Demdike Stare - Testpressings", "Manchester"),
    ("Millie Andrea - Drop the Vowels", "Manchester"),
    # === GHENT / BRUSSELS ===
    ("Joey Beltram - Energy Flash", "Ghent / Brussels"),
    ("Joey Beltram - Beltram Vol 1", "Ghent / Brussels"),
    ("CJ Bolland - Ravesignal III", "Ghent / Brussels"),
    ("CJ Bolland - The 4th Sign", "Ghent / Brussels"),
    ("Aphex Twin - Didgeridoo", "Ghent / Brussels"),
    ("Second Phase - Mentasm", "Ghent / Brussels"),
    # === NETHERLANDS ===
    ("Clone Records Various", "Netherlands"),
    ("Sterac - Electronics", "Netherlands"),
    ("Orphx - Pitch Black Mirror", "Netherlands"),
    # === CHICAGO ===
    ("Marshall Jefferson - Move Your Body", "Chicago"),
    ("Phuture - Acid Tracks", "Chicago"),
    ("Larry Heard - Can You Feel It", "Chicago"),
    ("Ron Trent - Altered States", "Chicago"),
    ("Virgo Four - Stairway to Heaven", "Chicago"),
    ("Green Velvet - Walk in the Park", "Chicago"),
    ("Green Velvet - Genedefekt", "Chicago"),
    ("Paul Johnson - Get Get Down", "Chicago"),
    ("DJ Rush - Get On Up", "Chicago"),
    ("DJ Funk - Work That Mutha", "Chicago"),
    ("Traxman - Hit It From the Back", "Chicago"),
    ("Dance Mania Hardcore Traxx", "Chicago"),
    ("Trax Records House Sound of Chicago", "Chicago"),
    # === NEW YORK ===
    ("L.I.E.S. American Noise", "New York"),
    ("Ron Morelli - Spit", "New York"),
    ("Vatican Shadow - Kneel Before Religious Icons", "New York"),
    ("Pharmakon - Bestial Burden", "New York"),
    ("Anthony Parasole - Subliminal Visitor", "New York"),
    # === CANADA ===
    ("Richie Hawtin - Dimension Intrusion", "Canada"),
    ("Plastikman - Sheet One", "Canada"),
    ("Plastikman - Consumed", "Canada"),
    # === JAPAN ===
    ("Ken Ishii - Jelly Tones", "Japan"),
    ("Ken Ishii - Reference to Difference", "Japan"),
    ("Fumiya Tanaka - Virtuality", "Japan"),
    ("DJ Nobu - Bitta", "Japan"),
    ("Wata Igarashi - Mood of the Machines", "Japan"),
    # === GEORGIA / EASTERN EUROPE ===
    ("Hieroglyphic Being - Disco of Imhotep", "Georgia / Eastern Europe"),
    # === ITALY ===
    ("Donato Dozzy - Voices from the Lake", "Italy"),
    ("Donato Dozzy - Squadra Quadra", "Italy"),
    # === SAO PAULO ===
    # (limited canonical techno from here)
]


def search_discogs(query):
    url = f"https://api.discogs.com/database/search?q={quote(query)}&type=release&per_page=3"
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
                    "format": ", ".join(r.get("format", [])) if isinstance(r.get("format"), list) else str(r.get("format", "")),
                }
    except Exception as e:
        print(f"  ERR: {e}")
    return None


def download_image(url, dest):
    headers = {"User-Agent": "TechnoVisualArchive/1.0"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as resp:
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
    added = 0
    skipped = 0
    failed = 0

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    for i, (query, scene) in enumerate(RELEASES):
        result = search_discogs(query)
        if not result:
            print(f"  NOT FOUND: {query}")
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
        if image_path and os.path.exists(image_path):
            color, colors = extract_color(image_path)

        release = {
            "id": result["id"],
            "title": result["title"],
            "artist": result["artist"],
            "year": result["year"],
            "catno": result["catno"],
            "thumb": result["thumb"],
            "format": result["format"],
            "label": query.split(" - ")[0] if " - " in query else query.split()[0],
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

        if added % 20 == 0:
            print(f"  Progress: {added} added, {skipped} skipped, {failed} failed ({i+1}/{len(RELEASES)})")

    # Dedup by cover hash
    hash_seen = set()
    no_dupe = []
    for r in data["releases"]:
        img = r.get("image", "")
        if img and os.path.exists(img):
            h = hashlib.md5(open(img, "rb").read()).hexdigest()
            if h in hash_seen:
                continue
            hash_seen.add(h)
        no_dupe.append(r)
    data["releases"] = no_dupe

    # Sort and save
    data["releases"].sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r["year"] > 0]
    if years:
        data["meta"]["year_range"] = [min(years), max(years)]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nDone: +{added} new, {skipped} existed, {failed} not found")
    print(f"Total archive: {data['meta']['total']} releases")


if __name__ == "__main__":
    main()
