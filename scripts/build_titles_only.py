#!/usr/bin/env python3
"""
Build releases.json from @guestsixonetwo list — titles only, no images.
Every entry gets added with metadata from the source list.
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "releases.json"
SOURCE_FILE = Path("/Users/humbertomacbook/Downloads/guestsixonetwo_posts.md")

# ── Artist name cleanup ──────────────────────────────────────────────
ARTIST_MAP = {
    "keithtucker": "Keith Tucker", "dopplereffekt": "Dopplereffekt",
    "missdjax": "Miss Djax", "jeffmills": "Jeff Mills",
    "juanatkins": "Juan Atkins", "stevestoll": "Steve Stoll",
    "helenahauff": "Helena Hauff", "stanislavtolkachev": "Stanislav Tolkachev",
    "stanislvtolkachev": "Stanislav Tolkachev", "mikeparker": "Mike Parker",
    "marcoshuttle": "Marco Shuttle", "thewisecaucasian": "The Wise Caucasian",
    "theevader": "The Evader", "rhythmandsound": "Rhythm & Sound",
    "planetaryassaultsystems": "Planetary Assault Systems",
    "djskull": "DJ Skull", "jamiebissmire": "Jamie Bissmire",
    "djesp": "DJ ESP", "damonwild": "Damon Wild",
    "silentservant": "Silent Servant", "christianw": "Christian Wünsch",
    "oliverrosemann": "Oliver Rosemann", "nihadtule": "Nihad Tule",
    "claudeyoung": "Claude Young", "terrencedixon": "Terrence Dixon",
    "marceldettmann": "Marcel Dettmann", "fadimohem": "Fadi Mohem",
    "anthonyrother": "Anthony Rother", "donatodozzy": "Donato Dozzy",
    "aphextwin": "Aphex Twin", "dasharush": "Dasha Rush",
    "wataigarashi": "Wata Igarashi", "eduardodelacalle": "Eduardo De La Calle",
    "oscarmulero": "Oscar Mulero", "dimiang": "Dimi Angélis",
    "heikolaux": "Heiko Laux", "djslip": "DJ Slip",
    "alexcortex": "Alex Cortex", "steveosullivan": "Steve O'Sullivan",
    "chesterbeatty": "Chester Beatty", "albertvanabbe": "Albert Van Abbe",
    "shxcxchcxsh": "SHXCXCHCXSH", "daveclarke": "Dave Clarke",
    "jamesruskin": "James Ruskin", "stewartswalker": "Stewart Walker",
    "oliverho": "Oliver Ho", "stevebicknell": "Steve Bicknell",
    "rinocerrone": "Rino Cerrone", "djshufflemaster": "DJ Shufflemaster",
    "richiehawtin": "Richie Hawtin", "christianmorgenstern": "Christian Morgenstern",
    "babyford": "Baby Ford", "plastikman": "Plastikman",
    "djt1000": "DJ T-1000", "arthurrobert": "Arthur Robert",
    "fanonflowers": "Fanon Flowers", "roberthood": "Robert Hood",
    "atomtm": "Atom TM", "benssims": "Ben Sims",
    "charlesmingus": "Charles Mingus", "andystott": "Andy Stott",
    "takaakiitoh": "Takaaki Itoh", "petervanhoesen": "Peter Van Hoesen",
    "inigokennedy": "Inigo Kennedy", "thesuburbanknight": "The Suburban Knight",
    "jaydenham": "Jay Denham", "joeybeltram": "Joey Beltram",
    "djstingray313": "DJ Stingray 313", "renewise": "Rene Wise",
    "lewisfautzi": "Lewis Fautzi", "fumiyatanaka": "Fumiya Tanaka",
    "carilekebusch": "Cari Lekebusch", "thomasbrinkmann": "Thomas Brinkmann",
    "danielbell": "Daniel Bell", "thebluntedboywonder": "The Blunted Boy Wonder",
    "garymartin": "Gary Martin", "adambeyer": "Adam Beyer",
    "basmooy": "Bas Mooy", "populationone": "Population One",
    "deepchord": "DeepChord", "answercoderequest": "Answer Code Request",
    "lukeslater": "Luke Slater", "kangdingray": "Kangding Ray",
    "model500": "Model 500", "vladislavdelay": "Vladislav Delay",
    "freddiefresh": "Freddie Fresh", "brendonmoeller": "Brendon Moeller",
    "giorgiogigli": "Giorgio Gigli", "anthonyshakir": "Anthony Shakir",
    "anthonyshakeshakir": "Anthony Shakir", "terencefixmer": "Terence Fixmer",
    "abdullarashim": "Abdulla Rashim", "jeroensearch": "Jeroen Search",
    "spacedjz": "Space DJZ", "deleteeverything": "Delete Everything",
    "tinman": "Tin Man", "ciodor": "Cio D'Or",
    "porterricks": "Porter Ricks", "basicchannel": "Basic Channel",
    "stephenbrown": "Stephen Brown", "speedyj": "Speedy J",
    "paulsthilaire": "Paul St Hilaire", "britishmurderboys": "British Murder Boys",
    "paperclippeople": "Paperclip People", "samulikemppi": "Samuli Kemppi",
    "stevenporter": "Steven Porter", "convextion": "Convextion",
    "djsurgeles": "DJ Surgeles", "luigitozzi": "Luigi Tozzi",
    "ryojiikeda": "Ryoji Ikeda", "daxj": "Dax J",
    "the65dmavericks": "The 65D Mavericks", "anthonylinell": "Anthony Linell",
    "jonaskopp": "Jonas Kopp", "alvanoto": "Alva Noto",
    "skeemask": "Skee Mask", "millsart": "Millsart",
    "blawan": "Blawan", "marcusadam": "Marcus Adam",
    "conradvanorton": "Conrad Van Orton", "marcolenzi": "Marco Lenzi",
    "caterinabarbieri": "Caterina Barbieri",
    "theotherpeopleplace": "The Other People Place",
    "theadvent": "The Advent", "pansonic": "Pan Sonic",
    "hiroakiiizuka": "Hiroaki Iizuka", "jesperdahlb": "Jesper Dahlbäck",
    "paulbirken": "Paul Birken", "iesopedrift": "Iesope Drift",
    "christianbor": "Christian Bor", "roiseux": "Roiseux",
    "kerrichandler": "Kerri Chandler", "model600": "Model 600",
    "adamx": "Adam X", "neillandstrumm": "Neil Landstrumm",
    "stevepoindexter": "Steve Poindexter", "kenishii": "Ken Ishii",
    "suburbanknight": "Suburban Knight", "gherkinjerks": "Gherkin Jerks",
    "forwardstrategygroup": "Forward Strategy Group",
    "claudioprc": "Claudio PRC", "markbroom": "Mark Broom",
    "zenkerbrothers": "Zenker Brothers", "theoparrish": "Theo Parrish",
    "setaocmass": "Setaoc Mass", "benklock": "Ben Klock",
    "hectoroaks": "Hector Oaks", "byetone": "Byetone",
    "woodymcbride": "Woody McBride",
    "voicesfromthelake": "Voices From The Lake",
    "sandwelldistrict": "Sandwell District",
    "taylordeupree": "Taylor Deupree",
    "jenseninterceptor": "Jensen Interceptor",
    "lossofbalance": "Loss Of Balance",
    "fixmer": "Fixmer/McCarthy",
    "brotherfromanotherplanet": "Brother From Another Planet",
    "davidgnuoy": "David Gnuoy", "psykoffuk": "Psykofuk",
    "skynet313": "Skynet 313", "stevereich": "Steve Reich",
    "nastiareigel": "Nastia Reigel",
    "palicavonzvreca": "Palica Von Zvreca",
    "djstingray": "DJ Stingray",
    "portionreform": "Portion Reform",
    "leiras": "Leiras", "wladimirm": "Wladimir M",
    "kerridge": "Kerridge",
    "digitalprincezz": "Digital Princezz",
    "lawilliams": "LA Williams",
    "christianbloch": "Christian Bloch",
    "etappkyle": "Etapp Kyle",
}

# ── Scene assignment ─────────────────────────────────────────────────
ARTIST_SCENES = {
    "jeffmills": "Detroit", "roberthood": "Detroit", "drexciya": "Detroit",
    "millsart": "Detroit", "populationone": "Detroit", "anthonyshakir": "Detroit",
    "anthonyshakeshakir": "Detroit",
    "claudeyoung": "Detroit", "keithtucker": "Detroit", "paperclippeople": "Detroit",
    "jaydenham": "Detroit", "terrencedixon": "Detroit", "deepchord": "Detroit",
    "theotherpeopleplace": "Detroit", "spacedjz": "Detroit", "convextion": "Detroit",
    "woodymcbride": "Detroit", "thebluntedboywonder": "Detroit", "model500": "Detroit",
    "juanatkins": "Detroit", "dopplereffekt": "Detroit", "cybotron": "Detroit",
    "thesuburbanknight": "Detroit", "suburbanknight": "Detroit", "infiniti": "Detroit",
    "danielbell": "Detroit", "model600": "Detroit", "thevision": "Detroit",
    "parallel9": "Detroit", "garymartin": "Detroit",
    "surgeon": "London", "regis": "London", "britishmurderboys": "London",
    "bmb": "London", "perc": "London", "silentservant": "London", "blawan": "London",
    "female": "London", "sigha": "London", "inigokennedy": "London",
    "jamesruskin": "London", "oliverho": "London", "the65dmavericks": "London",
    "sunil": "London", "charlton": "London", "stevebicknell": "London",
    "daxj": "London", "renewise": "London", "timeblind": "London",
    "killawatt": "London", "daveclarke": "London", "kerridge": "London",
    "makaton": "London", "babyford": "London", "lukeslater": "London",
    "donatodozzy": "Italy", "luigitozzi": "Italy", "marcoshuttle": "Italy",
    "neel": "Italy", "ciodor": "Italy", "caterinabarbieri": "Italy",
    "claudioprc": "Italy", "marcolenzi": "Italy", "dleria": "Italy",
    "rinocerrone": "Italy", "raiz": "Italy", "dc11": "Italy", "pearl": "Italy",
    "voicesfromthelake": "Italy",
    "leiras": "Spain",
    "takaakiitoh": "Japan", "fumiyatanaka": "Japan", "djshufflemaster": "Japan",
    "djnobu": "Japan", "wataigarashi": "Japan", "hiroakiiizuka": "Japan",
    "ryojiikeda": "Japan", "chesterbeatty": "Japan", "kenishii": "Japan",
    "petervanhoesen": "Ghent / Brussels",
    "shxcxchcxsh": "Sweden", "nihadtule": "Sweden", "abdullarashim": "Sweden",
    "anthonylinell": "Sweden", "jesperdahlb": "Sweden", "tilliander": "Sweden",
    "carilekebusch": "Sweden", "adambeyer": "Sweden",
    "stanislavtolkachev": "Georgia / Eastern Europe",
    "stanislvtolkachev": "Georgia / Eastern Europe",
    "pacou": "Berlin", "marceldettmann": "Berlin", "basicchannel": "Berlin",
    "porterricks": "Berlin", "monolake": "Berlin",
    "sandwelldistrict": "Berlin", "maurizio": "Berlin", "sleeparchive": "Berlin",
    "developer": "Berlin", "shifted": "Berlin", "cassegrain": "Berlin",
    "planetaryassaultsystems": "Berlin", "answercoderequest": "Berlin",
    "paulsthilaire": "Berlin", "fluxion": "Berlin", "etappkyle": "Berlin",
    "samulikemppi": "Berlin", "jonaskopp": "Berlin", "brendonmoeller": "Berlin",
    "troy": "Berlin", "shed": "Berlin", "benklock": "Berlin",
    "hectoroaks": "Berlin", "rrose": "Berlin", "arthurrobert": "Berlin",
    "vril": "Berlin", "helenahauff": "Berlin", "heikolaux": "Berlin",
    "temudo": "Berlin", "zenkerbrothers": "Berlin", "stenny": "Berlin",
    "forwardstrategygroup": "Berlin", "setaocmass": "Berlin", "amotik": "Berlin",
    "rod": "Berlin", "fadimohem": "Germany",
    "oscarmulero": "Spain", "reeko": "Spain", "svreca": "Spain",
    "eduardodelacalle": "Spain", "kwartz": "Spain",
    "orbe": "Spain", "vsk": "Spain", "conradvanorton": "Spain",
    "exium": "Spain", "psyk": "Spain", "lossofbalance": "Spain",
    "aiken": "Spain", "djesp": "Spain", "lewisfautzi": "Spain",
    "function": "New York", "mikeparker": "New York", "marcusadam": "New York",
    "stevestoll": "New York", "damonwild": "New York", "truncate": "New York",
    "dasharush": "New York", "adamx": "New York",
    "richiehawtin": "Canada", "plastikman": "Canada", "orphx": "Canada",
    "speedyj": "Netherlands", "sterac": "Netherlands", "steverachmad": "Netherlands",
    "damcase": "Netherlands", "dimiang": "Netherlands", "missdjax": "Netherlands",
    "djskull": "Chicago", "deeon": "Chicago", "phuture": "Chicago",
    "gherkinjerks": "Chicago", "joeybeltram": "Ghent / Brussels",
    "francoisx": "France", "zadig": "France", "terencefixmer": "France",
    "fixmer": "France",
    "alvanoto": "Chemnitz / Dresden", "byetone": "Chemnitz / Dresden",
    "kangdingray": "Chemnitz / Dresden",
    "efdemin": "Hamburg", "skeemask": "Munich", "hell": "Munich",
    "anthonyrother": "Germany", "thomasbrinkmann": "Germany",
    "christianmorgenstern": "Germany",
    "biosphere": "Scandinavia", "pansonic": "Scandinavia",
    "vladislavdelay": "Scandinavia",
    "nas": "New York", "charlesmingus": "New York", "stevereich": "New York",
    "aphextwin": "Sheffield / Leeds", "afx": "Sheffield / Leeds",
    "andystott": "Manchester", "theoparrish": "Detroit",
    "fanonflowers": "Berlin", "monrella": "Berlin",
    "stewartswalker": "Berlin", "oliverrosemann": "Berlin",
    "giorgiogigli": "Italy", "basmooy": "Netherlands",
    "theadvent": "Germany", "bandulu": "Berlin",
    "kerrichandler": "New York", "taylordeupree": "New York",
}

LABEL_SCENES = {
    "tresor": "Berlin", "ostgut": "Berlin", "basicchannel": "Berlin",
    "chainreaction": "Berlin", "stroboscopic": "Berlin",
    "avian": "Berlin", "sandwell": "Berlin", "marceldettmann": "Berlin",
    "klockworks": "Berlin", "raummusik": "Berlin", "monnom": "Berlin",
    "figur": "Berlin", "dynamicreflection": "Berlin", "modularz": "Berlin",
    "connwax": "Berlin", "50weapons": "Berlin", "mord": "Berlin",
    "token": "Berlin", "jealousgod": "Berlin", "imbalance": "Berlin",
    "blueprint": "London", "downwards": "London", "counterbalance": "London",
    "dynamictension": "London", "perctrax": "London", "moteevolver": "London",
    "nonplus": "London", "missile": "London", "cosmicrecords": "London",
    "tarhallow": "London", "asymmetric": "London", "novamute": "London",
    "contort": "London", "enemy": "London",
    "mplant": "Detroit", "axis": "Detroit", "purposemaker": "Detroit",
    "shockwave": "Detroit", "fxhe": "Detroit", "metroplex": "Detroit",
    "undergroundresistance": "Detroit",
    "peacefrog": "London",
    "geophone": "New York", "infrastructure": "New York",
    "sonicgroove": "New York", "synewave": "New York", "propernycrecords": "New York",
    "nonseries": "Italy", "hypnus": "Italy", "prologue": "Italy",
    "spaziodisponibile": "Italy", "fallingethics": "Italy",
    "electricdeluxe": "Netherlands", "bunker": "Netherlands",
    "djax": "Netherlands", "delsin": "Netherlands",
    "stockholmltd": "Sweden", "stockholmlimited": "Sweden",
    "norrlands": "Sweden", "northernelectronics": "Sweden",
    "kontramusik": "Sweden", "drumcode": "Sweden", "sloboda": "Sweden",
    "wols": "Japan", "planetrhythm": "Japan", "subvoice": "Japan",
    "torema": "Japan", "clonedvinyl": "Japan",
    "illiantape": "Munich", "giegling": "Germany",
    "noton": "Chemnitz / Dresden", "rasternoton": "Chemnitz / Dresden",
    "editionsmego": "Germany", "kanzleramt": "Germany",
    "mentaldisorder": "Spain", "polegroup": "Spain", "warmup": "Spain",
    "semantica": "Spain", "fautsection": "Spain",
    "eartoground": "Spain", "analogsolutions": "Spain",
    "plus8": "Canada", "turbo": "Canada",
    "warp": "Sheffield / Leeds", "rephlex": "Sheffield / Leeds",
    "planete": "France", "childrenoftomorrow": "France",
    "nechto": "Georgia / Eastern Europe",
    "forceincmusicworks": "Frankfurt", "forceinc": "Frankfurt",
    "columbia": "New York",
}

GEO = {
    "Detroit": [42.3314, -83.0458], "Berlin": [52.5200, 13.4050],
    "London": [51.5074, -0.1278], "Cologne": [50.9375, 6.9603],
    "Frankfurt": [50.1109, 8.6821], "Hamburg": [53.5511, 9.9937],
    "Munich": [48.1351, 11.5820], "Chemnitz / Dresden": [51.0504, 13.7373],
    "Sheffield / Leeds": [53.8008, -1.5491], "Manchester": [53.4808, -2.2426],
    "Ghent / Brussels": [50.8503, 4.3517], "Netherlands": [52.3676, 4.9041],
    "Chicago": [41.8781, -87.6298], "New York": [40.7128, -74.0060],
    "Japan": [35.6762, 139.6503], "Canada": [43.6532, -79.3832],
    "Italy": [41.9028, 12.4964], "Spain": [40.4168, -3.7038],
    "France": [48.8566, 2.3522], "Sweden": [59.3293, 18.0686],
    "Georgia / Eastern Europe": [41.7151, 44.8271],
    "Scandinavia": [59.9139, 10.7522], "Germany": [51.1657, 10.4515],
}


def parse_entry(line):
    """Parse: 'N. artist — title [FORMAT] (label)' → dict"""
    line = re.sub(r"^\d+\.\s*", "", line.strip())
    if " — " not in line:
        return None
    artist_raw, rest = line.split(" — ", 1)
    label_raw = ""
    m = re.search(r"\(([^)]+)\)", rest)
    if m:
        label_raw = m.group(1).strip()
        rest = rest[: m.start()].strip()
    fmt = ""
    m2 = re.search(r"\[([^\]]+)\]", rest)
    if m2:
        fmt = m2.group(1)
        rest = rest[: m2.start()].strip() + " " + rest[m2.end() :].strip()
        rest = rest.strip()
    title_clean = re.sub(r"\s+episode\s+.*", "", rest).strip()

    a = artist_raw.strip().lower()
    artist = ARTIST_MAP.get(a, artist_raw.strip().title())
    label = re.sub(r"records?$", "", label_raw, flags=re.IGNORECASE).strip()

    return {
        "artist_raw": artist_raw.strip(),
        "artist": artist,
        "title": title_clean or rest,
        "label": label or "Unknown",
        "format": fmt or "Vinyl",
    }


def get_scene(artist_raw, label_raw):
    a = artist_raw.lower().strip()
    if a in ARTIST_SCENES:
        return ARTIST_SCENES[a]
    l = label_raw.lower().replace(" ", "")
    for key, scene in LABEL_SCENES.items():
        if key in l:
            return scene
    return "Berlin"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    seen = set()
    with open(SOURCE_FILE) as f:
        for line in f:
            line = line.strip()
            if not re.match(r"^\d+\.\s+", line):
                continue
            parsed = parse_entry(line)
            if not parsed:
                continue
            key = f"{parsed['artist_raw']}|{parsed['title']}".lower()
            if key in seen:
                continue
            seen.add(key)
            entries.append(parsed)

    print(f"Parsed {len(entries)} unique entries")

    releases = []
    for i, entry in enumerate(entries):
        scene = get_scene(entry["artist_raw"], entry["label"])
        release = {
            "id": i + 1,
            "title": entry["title"],
            "artist": entry["artist"],
            "year": 0,
            "catno": "",
            "thumb": "",
            "format": entry["format"],
            "label": entry["label"],
            "label_id": 0,
            "scene": scene,
            "discogs_url": "",
            "image": "",
            "color": "#1a1a1a",
            "colors": ["#1a1a1a", "#0a0a0a", "#2a2a2a"],
        }
        releases.append(release)

    scenes_used = sorted(set(r["scene"] for r in releases))

    data = {
        "meta": {
            "total": len(releases),
            "labels": len(set(r["label"] for r in releases)),
            "scenes": scenes_used,
            "year_range": [0, 0],
        },
        "geo": {k: v for k, v in GEO.items() if k in scenes_used},
        "releases": releases,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Done: {len(releases)} releases written to {OUTPUT_FILE}")
    print(f"Labels: {data['meta']['labels']}, Scenes: {len(scenes_used)}")


if __name__ == "__main__":
    main()
