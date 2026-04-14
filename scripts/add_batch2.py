#!/usr/bin/env python3
"""Add batch 2 — 374 releases from @guestsixonetwo."""

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

# ── Artist name cleanup ──────────────────────────────────────────────
ARTIST_MAP = {
    "atomtm": "Atom TM", "deleteeverything": "Delete Everything",
    "roberthood": "Robert Hood", "stephenbrown": "Stephen Brown",
    "dimiang": "Dimi Angelis", "speedyj": "Speedy J",
    "paulsthilaire": "Paul St Hilaire", "basicchannel": "Basic Channel",
    "stevebicknell": "Steve Bicknell", "silentservant": "Silent Servant",
    "richiehawtin": "Richie Hawtin", "mikeparker": "Mike Parker",
    "britishmurderboys": "British Murder Boys", "ciodor": "Cio D'Or",
    "takaakiitoh": "Takaaki Itoh", "nihadtule": "Nihad Tule",
    "luigitozzi": "Luigi Tozzi", "marceldettmann": "Marcel Dettmann",
    "donatodozzy": "Donato Dozzy", "jeffmills": "Jeff Mills",
    "anthonyshakir": "Anthony Shakir", "francoisx": "Francois X",
    "porterricks": "Porter Ricks", "marcusadam": "Marcus Adam",
    "jamesruskin": "James Ruskin", "fadimohem": "Fadi Mohem",
    "oliverrosemann": "Oliver Rosemann", "petervanhoesen": "Peter Van Hoesen",
    "inigokennedy": "Inigo Kennedy", "eduardodelacalle": "Eduardo De La Calle",
    "steverachmad": "Steve Rachmad", "jeroensearch": "Jeroen Search",
    "oscarmulero": "Oscar Mulero", "jaydenham": "Jay Denham",
    "alvanoto": "Alva Noto", "terencefixmer": "Terence Fixmer",
    "samulikemppi": "Samuli Kemppi", "claudeyoung": "Claude Young",
    "djshufflemaster": "DJ Shufflemaster", "anthonyrother": "Anthony Rother",
    "djsurgeles": "DJ Surgeles", "paperclippeople": "Paperclip People",
    "djslip": "DJ Slip", "abdullarashim": "Abdulla Rashim",
    "fumiyatanaka": "Fumiya Tanaka", "ryojiikeda": "Ryoji Ikeda",
    "daxj": "Dax J", "renewise": "Rene Wise",
    "terrencedixon": "Terrence Dixon", "djhell": "DJ Hell",
    "stanislavtolkachev": "Stanislav Tolkachev", "stanislvtolkachev": "Stanislav Tolkachev",
    "oliverho": "Oliver Ho", "woodymcbride": "Woody McBride",
    "stevestoll": "Steve Stoll", "the65dmavericks": "The 65D Mavericks",
    "anthonylinell": "Anthony Linell", "jonaskopp": "Jonas Kopp",
    "blacksabbath": "Black Sabbath", "fanonflowers": "Fanon Flowers",
    "aguycalledgerald": "A Guy Called Gerald", "chesterbeatty": "Chester Beatty",
    "conradvanorton": "Conrad Van Orton", "wataigarashi": "Wata Igarashi",
    "answercoderequest": "Answer Code Request", "brendonmoeller": "Brendon Moeller",
    "planetaryassaultsystems": "Planetary Assault Systems",
    "claudioprc": "Claudio PRC", "etappkyle": "Etapp Kyle",
    "djnobu": "DJ Nobu", "jesperdahlb": "Jesper Dahlback",
    "marcoshuttle": "Marco Shuttle", "linearsystem": "Linear System",
    "hiroakiiizuka": "Hiroaki Iizuka", "populationone": "Population One",
    "paulbirken": "Paul Birken", "spacedjz": "Space DJZ",
    "thebluntedboywonder": "The Blunted Boy Wonder",
    "iesopedrift": "Iesope Drift", "christianbor": "Christian Bor",
    "keithtucker": "Keith Tucker", "steveosullivan": "Steve O'Sullivan",
    "philkieran": "Phil Kieran", "caterinabarbieri": "Caterina Barbieri",
    "adrianalopez": "Adriana Lopez", "theotherpeopleplace": "The Other People Place",
    "theadvent": "The Advent", "pansonic": "Pan Sonic",
    "skeemask": "Skee Mask", "developr": "Developer",
    "bmb": "British Murder Boys", "plastikman": "Plastikman",
    "ricodaasylumproductions": "Rico", "stevenporter": "Steven Porter",
    "philbarton": "Phil Barton", "chrissattinger": "Chris Sattinger",
    "blankprogram": "Blank Program", "chancemcdermott": "Chance McDermott",
    "sphericalcoordinates": "Spherical Coordinates",
    "marcolenzi": "Marco Lenzi", "evigtm": "Evigt Morker",
    "christianw": "Christian Wunsch", "deepchord": "DeepChord",
    "alexcortex": "Alex Cortex", "sequentialcircuits": "Sequential Circuits",
    "modularsidem": "Modular Side M", "theadvent": "The Advent",
    "thefearratio": "The Fear Ratio", "antonpieete": "Anton Pieete",
    "nttr909": "NTTR 909", "rumenige": "Rumenige",
}

# ── Scene assignment ─────────────────────────────────────────────────
ARTIST_SCENES = {
    "jeffmills": "Detroit", "roberthood": "Detroit", "drexciya": "Detroit",
    "millsart": "Detroit", "populationone": "Detroit", "anthonyshakir": "Detroit",
    "claudeyoung": "Detroit", "keithtucker": "Detroit", "paperclippeople": "Detroit",
    "jaydenham": "Detroit", "terrencedixon": "Detroit", "deepchord": "Detroit",
    "theotherpeopleplace": "Detroit", "spacedjz": "Detroit", "convextion": "Detroit",
    "woodymcbride": "Detroit", "thebluntedboywonder": "Detroit", "1stbass": "London",
    "surgeon": "London", "regis": "London", "britishmurderboys": "London",
    "bmb": "London", "perc": "London", "silentservant": "London", "blawan": "London",
    "female": "London", "sigha": "London", "inigokennedy": "London",
    "jamesruskin": "London", "oliverho": "London", "the65dmavericks": "London",
    "thefearratio": "London", "philbarton": "London", "sunil": "London",
    "charlton": "London", "stevebicknell": "London", "daxj": "London",
    "renewise": "London", "timeblind": "London", "killawatt": "London",
    "donatodozzy": "Italy", "luigitozzi": "Italy", "marcoshuttle": "Italy",
    "neel": "Italy", "ciodor": "Italy", "caterinabarbieri": "Italy",
    "claudioprc": "Italy", "marcolenzi": "Italy",
    "takaakiitoh": "Japan", "fumiyatanaka": "Japan", "djshufflemaster": "Japan",
    "djnobu": "Japan", "wataigarashi": "Japan", "hiroakiiizuka": "Japan",
    "ryojiikeda": "Japan", "chesterbeatty": "Japan",
    "petervanhoesen": "Ghent / Brussels",
    "shxcxchcxsh": "Sweden", "nihadtule": "Sweden", "abdullarashim": "Sweden",
    "anthonylinell": "Sweden", "joelinder": "Sweden", "jesperdahlb": "Sweden",
    "grovskopa": "Sweden", "tm404": "Sweden", "ulwhednar": "Sweden",
    "stanislavtolkachev": "Georgia / Eastern Europe", "stanislvtolkachev": "Georgia / Eastern Europe",
    "stanislav": "Georgia / Eastern Europe",
    "pacou": "Berlin", "marceldettmann": "Berlin", "basicchannel": "Berlin",
    "porterricks": "Berlin", "monolake": "Berlin", "sandwell": "Berlin",
    "maurizio": "Berlin", "sleeparchive": "Berlin", "developer": "Berlin",
    "developr": "Berlin", "shifted": "Berlin", "cassegrain": "Berlin",
    "planetaryassaultsystems": "Berlin", "answercoderequest": "Berlin",
    "paulsthilaire": "Berlin", "fluxion": "Berlin", "etappkyle": "Berlin",
    "samulikemppi": "Berlin", "jonaskopp": "Berlin", "christianbor": "Berlin",
    "brendonmoeller": "Berlin", "troy": "Berlin",
    "oscarmulero": "Spain", "reeko": "Spain", "svreca": "Spain",
    "eduardodelacalle": "Spain", "kwartz": "Spain", "adrianalopez": "Spain",
    "orbe": "Spain", "vsk": "Spain", "conradvanorton": "Spain",
    "exium": "Spain", "reus": "Spain", "cadency": "Spain",
    "function": "New York", "mikeparker": "New York", "marcusadam": "New York",
    "stevestoll": "New York", "damonwild": "New York", "truncate": "New York",
    "richiehawtin": "Canada", "plastikman": "Canada", "orphx": "Canada",
    "speedyj": "Netherlands", "sterac": "Netherlands", "steverachmad": "Netherlands",
    "damcase": "Netherlands", "dimiang": "Netherlands", "dimi": "Netherlands",
    "francoisx": "France", "zadig": "France", "terencefixmer": "France",
    "terence": "France", "cerrone": "France",
    "alvanoto": "Chemnitz / Dresden", "efdemin": "Hamburg",
    "skeemask": "Munich", "hell": "Munich", "djhell": "Munich",
    "anthonyrother": "Germany", "biosphere": "Scandinavia", "pansonic": "Scandinavia",
    "nas": "New York", "blacksabbath": "London",
    "aguycalledgerald": "Manchester", "roiseux": "Germany",
    "stevenporter": "London", "klankman": "Netherlands",
    "vril": "Germany", "marbod": "Germany", "whitenoise": "Berlin",
    "modularz": "Berlin", "modulariz": "Berlin",
    "atomtm": "Germany", "stephenbrown": "Netherlands",
    "deleteeverything": "London", "ricodaasylumproductions": "London",
    "anthonyrother": "Germany", "steveosullivan": "London",
    "philkieran": "London", "alexcortex": "Germany",
}

LABEL_SCENES = {
    "tresor": "Berlin", "ostgut": "Berlin", "basicchannel": "Berlin",
    "chainreaction": "Berlin", "raster": "Berlin", "stroboscopic": "Berlin",
    "avian": "Berlin", "sandwell": "Berlin", "marceldettmann": "Berlin",
    "klockworks": "Berlin", "raummusik": "Berlin", "monnom": "Berlin",
    "figur": "Berlin", "dynamicreflection": "Berlin", "rawraw": "Berlin",
    "voam": "Berlin", "selected": "Berlin", "background": "Berlin",
    "falsetuned": "Berlin", "modularz": "Berlin",
    "blueprint": "London", "downwards": "London", "counterbalance": "London",
    "dynamictension": "London", "perctrax": "London", "moteevolver": "London",
    "nonplus": "London", "missile": "London", "badsector": "London",
    "cosmicrecords": "London", "tarhallow": "London", "asymmetric": "London",
    "novamute": "London", "enemy": "London",
    "mplant": "Detroit", "axis": "Detroit", "purposemaker": "Detroit",
    "shockwave": "Detroit", "fxhe": "Detroit",
    "geophone": "New York", "infrastructure": "New York",
    "sonicgroove": "New York", "hospitalproductions": "New York",
    "synewave": "New York",
    "nonseries": "Italy", "hypnus": "Italy", "prologue": "Italy",
    "dynavision": "Italy", "fineaudio": "Italy", "lofi": "Italy",
    "electricdeluxe": "Netherlands", "bunker": "Netherlands",
    "search": "Netherlands", "djax": "Netherlands", "rachma": "Netherlands",
    "dekmantel": "Netherlands", "keysoflife": "Netherlands",
    "speakerattack": "Netherlands",
    "stockholmltd": "Sweden", "stockholmlimited": "Sweden",
    "norrlands": "Sweden", "northernelectronics": "Sweden",
    "kontramusik": "Sweden", "abdullarashim": "Sweden", "skudge": "Sweden",
    "wols": "Japan", "planetrhythm": "Japan", "subvoice": "Japan",
    "futurenoise": "Japan", "torema": "Japan", "counterpulse": "Japan",
    "accelerate": "Japan", "element": "Japan",
    "illiantape": "Munich", "giegling": "Germany",
    "noton": "Chemnitz / Dresden", "editionsmego": "Frankfurt",
    "perlon": "Frankfurt", "curle": "Hamburg",
    "mentaldisorder": "Spain", "polegroup": "Spain", "warmup": "Spain",
    "semantica": "Spain", "fautsection": "Spain", "apm": "Spain",
    "eartoground": "Spain", "analogsolutions": "Spain", "danzanativa": "Spain",
    "nheo": "Spain", "finalmusik": "Spain", "suba": "Spain",
    "cabrera": "Spain", "esp": "Spain",
    "plus8": "Canada", "turbo": "Canada",
    "warp": "Sheffield / Leeds", "peacefrog": "London",
    "planete": "France", "childrenoftomorrow": "France",
    "24h": "Georgia / Eastern Europe", "nechto": "Georgia / Eastern Europe",
    "admiral": "Georgia / Eastern Europe",
    "archivesinteriures": "Ghent / Brussels", "timetoexpress": "Ghent / Brussels",
    "arcing": "Berlin", "dokument": "Berlin",
    "techumrecords": "Spain", "mohemrecords": "Germany",
    "rand": "Scandinavia", "blastfirst": "Scandinavia",
    "columbia": "New York", "diskob": "Munich",
}


def parse_entry(line):
    """Parse: 'artist — title [FORMAT] (label)' → (artist_raw, title_raw, label_raw)"""
    line = re.sub(r"^\d+\.\s*", "", line.strip())
    if " — " not in line:
        return None
    artist_raw, rest = line.split(" — ", 1)
    # Extract label
    label_raw = ""
    m = re.search(r"\(([^)]+)\)", rest)
    if m:
        label_raw = m.group(1).strip()
        rest = rest[: m.start()].strip()
    # Remove format tag
    rest = re.sub(r"\s*\[(?:EP|ALBUM|LP|COMPILATION|REMIX)\]\s*", " ", rest).strip()
    # Remove "episode ..." remix descriptions (keep main title)
    rest = re.sub(r"\s+episode\s+.*", "", rest).strip()
    title_raw = rest
    return artist_raw.strip(), title_raw.strip(), label_raw


def split_smashed(text):
    """Insert spaces into smashedtogether words using heuristics."""
    # Don't split known acronyms or short words
    if len(text) < 5 or text.isupper() or text.isdigit():
        return text
    # Insert space before runs of uppercase in mixed case
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # Insert space between digit and letter transitions
    text = re.sub(r"([a-z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([a-z])", r"\1 \2", text)
    return text


def get_scene(artist_raw, label_raw):
    """Determine scene from artist and label."""
    a = artist_raw.lower().strip()
    if a in ARTIST_SCENES:
        return ARTIST_SCENES[a]
    l = label_raw.lower().replace(" ", "")
    for key, scene in LABEL_SCENES.items():
        if key in l:
            return scene
    return "Berlin"  # default


def build_query(artist_raw, title_raw, label_raw):
    """Build a Discogs search query."""
    artist = ARTIST_MAP.get(artist_raw.lower().strip(), split_smashed(artist_raw))
    title = split_smashed(title_raw)
    # Clean up common patterns
    title = title.replace("vs", "").strip()
    if not title or title == artist:
        # title is same as artist or empty — use label hint
        label_clean = re.sub(r"records?$", "", label_raw).strip()
        label_clean = split_smashed(label_clean)
        return f"{artist} {label_clean}".strip()
    return f"{artist} - {title}"


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
            time.sleep(1.1)  # rate limit
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
            colors = [
                f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}"
                for (qr, qg, qb), _ in top
            ]
            return colors[0], colors
    except:
        pass
    return None, []


def main():
    # Read raw entries
    raw_path = SCRIPT_DIR.parent.parent / "guestsixonetwo_posts.txt"
    if not raw_path.exists():
        raw_path = Path("/Users/humbertomacbook/Downloads/guestsixonetwo_posts.txt")
    lines = []
    with open(raw_path) as f:
        for line in f:
            line = line.strip()
            if re.match(r"^\d+\.\s+", line):
                lines.append(line)
    print(f"Parsed {len(lines)} entries from source file")

    # Load existing data
    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    existing_ids = {r["id"] for r in data["releases"]}
    existing_titles = {
        f"{r['artist'].lower()}|{r['title'].lower()}" for r in data["releases"]
    }

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    added = 0
    skipped = 0
    failed = 0
    fail_list = []

    for i, line in enumerate(lines):
        parsed = parse_entry(line)
        if not parsed:
            print(f"  SKIP (parse): {line[:60]}")
            failed += 1
            continue

        artist_raw, title_raw, label_raw = parsed
        query = build_query(artist_raw, title_raw, label_raw)
        scene = get_scene(artist_raw, label_raw)

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

        # Extract color
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
            "label": label_raw.replace("records", "").replace("Records", "").strip(),
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
            print(
                f"  [{i+1}/{len(lines)}] +{added} new, {skipped} existed, {failed} failed"
            )
            # Checkpoint save every 50 new
            if added > 0 and added % 50 == 0:
                _save(data)
                print(f"  (checkpoint saved)")

    # ── Dedup by cover hash ──
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

    _save(data)

    print(f"\n{'='*50}")
    print(f"Done: +{added} new, {skipped} existed, {failed} not found")
    print(f"Total archive: {data['meta']['total']} releases")
    if fail_list:
        print(f"\nFailed queries ({len(fail_list)}):")
        for q in fail_list:
            print(f"  - {q}")


def _save(data):
    data["releases"].sort(key=lambda r: (r.get("year", 0), r.get("label", "")))
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r["year"] > 0]
    if years:
        data["meta"]["year_range"] = [min(years), max(years)]
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
