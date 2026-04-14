#!/usr/bin/env python3
"""Add user-supplied canon list with year + country hints for better matching."""

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
OUTPUT_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")

# Country -> scene mapping used in the archive
COUNTRY_TO_SCENE = {
    "US": "Detroit",  # default for US techno; overridden where obvious
    "DE": "Berlin",
    "UK": "London",
    "FR": "France",
    "ES": "Spain",
    "SE": "Sweden",
    "JP": "Japan",
    "CA": "Canada",
    "NL": "Netherlands",
    "NL/DE": "Berlin",
    "UK/US": "London",
    "UA": "Georgia / Eastern Europe",
    "UA/DE": "Berlin",
    "GR": "Georgia / Eastern Europe",
    "BG": "Georgia / Eastern Europe",
    "PL": "Georgia / Eastern Europe",
    "AR": "Georgia / Eastern Europe",
}

# (artist, title, year, country)
RELEASES = [
    ("Cybotron", "Alleys of Your Mind", 1981, "US"),
    ("Cybotron", "Clear", 1983, "US"),
    ("Model 500", "No UFOs", 1985, "US"),
    ("Phuture", "Acid Tracks", 1987, "US"),
    ("Derrick May", "Strings of Life", 1987, "US"),
    ("Rhythim Is Rhythim", "Nude Photo", 1987, "US"),
    ("Kevin Saunderson", "Big Fun", 1988, "US"),
    ("Inner City", "Good Life", 1988, "US"),
    ("Blake Baxter", "Ride 'Em Boy", 1987, "US"),
    ("Eddie Fowlkes", "Goodbye Kiss", 1986, "US"),
    ("Derrick May", "Icon", 1988, "US"),
    ("Joey Beltram", "Energy Flash", 1990, "US"),
    ("Joey Beltram", "Mentasm", 1991, "US"),
    ("Underground Resistance", "Transition", 1990, "US"),
    ("Underground Resistance", "Jupiter Jazz", 1991, "US"),
    ("Jeff Mills", "The Bells", 1991, "US"),
    ("Carl Craig", "Bug in the Bassbin", 1992, "US"),
    ("Robert Hood", "Minimal Nation", 1992, "US"),
    ("Basic Channel", "Phylyps Trak II", 1993, "DE"),
    ("Basic Channel", "Quadrant Dub", 1994, "DE"),
    ("Maurizio", "Ploy", 1993, "DE"),
    ("Hardfloor", "Acperience 1", 1992, "DE"),
    ("Plastikman", "Spastik", 1993, "CA"),
    ("Plastikman", "Helikopter", 1994, "CA"),
    ("Robert Hood", "Minus", 1994, "US"),
    ("Daniel Bell", "Losing Control", 1994, "US"),
    ("Jeff Mills", "Waveform Transmission Vol. 3", 1994, "US"),
    ("Dave Clarke", "Red Three", 1994, "UK"),
    ("Surgeon", "Magneze", 1994, "UK"),
    ("Laurent Garnier", "Flashback", 1994, "FR"),
    ("Robert Armani", "Circus Bells", 1993, "US"),
    ("Green Velvet", "Flash", 1995, "US"),
    ("Surgeon", "Badger Bite", 1996, "UK"),
    ("Stacey Pullen", "Sweat", 1996, "US"),
    ("Adam Beyer", "Drumcode 01", 1996, "SE"),
    ("Regis", "Speak to Me", 1997, "UK"),
    ("Fumiya Tanaka", "You Find the Way", 1997, "JP"),
    ("Oliver Ho", "The Shadow", 1999, "UK"),
    ("Luke Slater", "Love", 1999, "UK"),
    ("Ben Sims", "Manipulated", 1998, "UK"),
    ("Oscar Mulero", "Grey Fades to Green", 2001, "ES"),
    ("Surgeon", "Force + Form", 2000, "UK"),
    ("Cari Lekebusch", "Hypnotized", 1999, "SE"),
    ("Monolake", "Avalanche", 2001, "DE"),
    ("Shed", "Boom Room", 2008, "DE"),
    ("Marcel Dettmann", "Corrosion", 2009, "DE"),
    ("Ben Klock", "Subzero", 2009, "DE"),
    ("Ben Klock", "Compression Session", 2006, "DE"),
    ("Len Faki", "Mekong Delta", 2007, "DE"),
    ("Norman Nodge", "Embodiment of the Mind", 2011, "DE"),
    ("Shed", "The Traveller", 2010, "DE"),
    ("Steffi", "Yours", 2011, "NL/DE"),
    ("Dettmann & Klock", "Dawning", 2009, "DE"),
    ("nd_baumecker", "Follow the Wires", 2012, "DE"),
    ("Sandwell District", "Feed-Forward", 2010, "UK/US"),
    ("Function", "Incubation", 2011, "US"),
    ("Silent Servant", "Violencia", 2012, "US"),
    ("Vatican Shadow", "Cairo Is a Haunted City", 2012, "US"),
    ("Blawan", "Getting Me Down", 2012, "UK"),
    ("DVS1", "Black Russian", 2012, "US"),
    ("Objekt", "Cactus", 2012, "UK"),
    ("Perc", "Look What Your Love Has Done to Me", 2011, "UK"),
    ("Ancient Methods", "Drop Out", 2012, "DE"),
    ("Rødhåd", "Anxious", 2014, "DE"),
    ("Phase", "Autonomy", 2014, "UK"),
    ("Cassegrain", "Centre of Mass", 2014, "DE"),
    ("Terence Fixmer", "Force", 2013, "FR"),
    ("Marcel Dettmann", "Terrain", 2013, "DE"),
    ("Kobosil", "73", 2016, "DE"),
    ("Etapp Kyle", "Nolya", 2016, "UA/DE"),
    ("Helena Hauff", "Lex", 2015, "DE"),
    ("Paula Temple", "Colonized", 2013, "UK"),
    ("Ansome", "Stained", 2015, "UK"),
    ("Rebekah", "Code Black", 2015, "UK"),
    ("Oscar Mulero", "Shifting Signals", 2015, "ES"),
    ("Dax J", "Offending Public Morality", 2017, "UK"),
    ("I Hate Models", "Daydream", 2017, "FR"),
    ("FJAAK", "Laser", 2016, "DE"),
    ("Hector Oaks", "Broken Promises", 2019, "DE"),
    ("Clouds", "Chained to a Dead Camel", 2013, "UK"),
    ("KiNK", "Perth", 2012, "BG"),
    ("Barker & Baumecker", "Turnhalle", 2012, "DE"),
    ("Vril", "Torus VI", 2014, "DE"),
    ("Answer Code Request", "Silhouettes", 2014, "DE"),
    ("Pfirter", "Magnitude", 2013, "AR"),
    ("Stanislav Tolkachev", "Zakat", 2016, "UA"),
    ("SPFDJ", "Crumble", 2019, "NL/DE"),
    ("Stef Mendesidis", "Kleisoura", 2019, "GR"),
    ("Hadone", "Excess Body", 2021, "FR"),
    ("VTSS", "Toxic", 2020, "PL"),
    ("Anetha", "Panorama", 2019, "FR"),
    ("Alignment", "Deprivation", 2020, "DE"),
    ("Introversion", "Dystopian Love", 2021, "UK"),
    ("AIROD", "Acid Attack", 2019, "FR"),
    ("Rosa Anschütz", "Radical Rituals", 2021, "DE"),
    ("TRYM", "Karmic Debt", 2022, "SE"),
    ("Regal", "Two Decades of Silence", 2019, "ES"),
    ("UVB", "Disfigure", 2018, "UK"),
    ("P.E.A.R.L.", "Shaman Works", 1993, "DE"),
    ("Thomas P. Heckmann", "Body Music", 1993, "DE"),
]

# Scene overrides — US releases that are Chicago/NY rather than Detroit
SCENE_OVERRIDE = {
    ("Phuture", "Acid Tracks"): "Chicago",
    ("Green Velvet", "Flash"): "Chicago",
    ("Robert Armani", "Circus Bells"): "Chicago",
    ("Daniel Bell", "Losing Control"): "Detroit",
    ("Vatican Shadow", "Cairo Is a Haunted City"): "New York",
    ("Silent Servant", "Violencia"): "New York",
    ("Function", "Incubation"): "New York",
    ("Sandwell District", "Feed-Forward"): "London",
    ("DVS1", "Black Russian"): "Detroit",
}


def search_discogs(artist, title, year):
    q = f"{artist} {title}"
    url = f"https://api.discogs.com/database/search?q={quote(q)}&type=release&per_page=5"
    if year:
        url += f"&year={year}"
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
            # Prefer a result whose title loosely matches artist + title
            artist_lo = artist.lower().split()[0]
            title_lo = title.lower()
            for r in results:
                t = (r.get("title") or "").lower()
                if artist_lo in t and title_lo.split()[0] in t:
                    return r
            if results:
                return results[0]
    except Exception as e:
        print(f"  ERR search {artist} - {title}: {e}")
    # retry without year
    if year:
        return search_discogs(artist, title, 0)
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
    except Exception as e:
        print(f"  ERR download: {e}")
    return False


def extract_color(path):
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB").resize((32, 32))
        pixels = list(img.getdata())
        counts = collections.Counter()
        for pr, pg, pb in pixels:
            avg = (pr + pg + pb) / 3
            if avg < 10 or avg > 245:
                continue
            counts[(pr >> 4, pg >> 4, pb >> 4)] += 1
        if counts:
            top = counts.most_common(3)
            colors = [f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}" for (qr, qg, qb), _ in top]
            return colors[0], colors
    except Exception:
        pass
    return None, []


def main():
    if not TOKEN:
        print("Set DISCOGS_TOKEN env var")
        return

    with open(OUTPUT_FILE) as f:
        data = json.load(f)

    existing_ids = {r["id"] for r in data["releases"]}
    existing_keys = {
        f"{(r.get('artist') or '').lower().strip()}|{(r.get('title') or '').lower().strip()}"
        for r in data["releases"]
    }

    added = skipped = failed = 0
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    for i, (artist, title, year, country) in enumerate(RELEASES, 1):
        key = f"{artist.lower().strip()}|{title.lower().strip()}"
        if key in existing_keys:
            print(f"[{i}/{len(RELEASES)}] SKIP existing: {artist} - {title}")
            skipped += 1
            continue

        result = search_discogs(artist, title, year)
        if not result:
            print(f"[{i}/{len(RELEASES)}] NOT FOUND: {artist} - {title}")
            failed += 1
            continue

        if result.get("id") in existing_ids:
            print(f"[{i}/{len(RELEASES)}] SKIP (id exists): {artist} - {title}")
            skipped += 1
            continue

        thumb = result.get("cover_image") or result.get("thumb") or ""
        image_path = ""
        if thumb:
            dest = IMAGES_DIR / f"{result['id']}.jpg"
            if dest.exists() or download_image(thumb, str(dest)):
                image_path = f"images/{result['id']}.jpg"

        color, colors = (None, [])
        if image_path:
            full_path = SCRIPT_DIR.parent / image_path
            if full_path.exists():
                color, colors = extract_color(str(full_path))

        scene = SCENE_OVERRIDE.get((artist, title)) or COUNTRY_TO_SCENE.get(country, "Berlin")
        r_year = int(result.get("year") or 0) or year

        release = {
            "id": result["id"],
            "title": title,
            "artist": artist,
            "year": r_year,
            "catno": result.get("catno", ""),
            "thumb": thumb,
            "format": ", ".join(result.get("format", [])) if isinstance(result.get("format"), list) else str(result.get("format", "")),
            "label": (result.get("label") or [""])[0] if isinstance(result.get("label"), list) else (result.get("label") or ""),
            "label_id": 0,
            "scene": scene,
            "discogs_url": f"https://www.discogs.com/release/{result['id']}",
            "image": image_path,
            "color": color,
            "colors": colors,
            "country": country,
        }
        data["releases"].append(release)
        existing_ids.add(result["id"])
        existing_keys.add(key)
        added += 1
        print(f"[{i}/{len(RELEASES)}] + {artist} - {title} ({r_year}) -> {scene}")

    # Refresh meta
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r.get("label") or "" for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r.get("scene") or "" for r in data["releases"]))
    years = [r["year"] for r in data["releases"] if r.get("year", 0) > 0]
    if years:
        data["meta"]["year_range"] = [min(years), max(years)]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nDone: +{added} new, {skipped} existed, {failed} not found")
    print(f"Total archive: {data['meta']['total']} releases")


if __name__ == "__main__":
    main()
