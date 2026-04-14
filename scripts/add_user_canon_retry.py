#!/usr/bin/env python3
"""Retry the not-found titles with simpler/alternate queries."""
import json, os, time, collections
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_FILE = DATA_DIR / "releases.json"
TOKEN = os.environ.get("DISCOGS_TOKEN", "")

# (artist, title, country, alt_queries, scene)
MISSES = [
    ("Fumiya Tanaka", "You Find The Way", "JP", ["Fumiya Tanaka Find The Way", "Fumiya Tanaka Sundance"], "Japan"),
    ("Marcel Dettmann", "Corrosion", "DE", ["Marcel Dettmann Corrosion OSTGUT", "Dettmann Corrosion"], "Berlin"),
    ("nd_baumecker", "Follow The Wires", "DE", ["nd baumecker Follow Wires", "Nick Baumecker Follow Wires Ostgut"], "Berlin"),
    ("Cassegrain", "Centre Of Mass", "DE", ["Cassegrain Centre Mass", "Cassegrain Prologue"], "Berlin"),
    ("Marcel Dettmann", "Terrain", "DE", ["Marcel Dettmann Terrain Ostgut", "Dettmann II Terrain"], "Berlin"),
    ("Etapp Kyle", "Nolya", "UA/DE", ["Etapp Kyle Nolya", "Etapp Kyle Ostgut"], "Berlin"),
    ("Ansome", "Stained", "UK", ["Ansome Stained Perc Trax", "Ansome Perc"], "London"),
    ("Oscar Mulero", "Shifting Signals", "ES", ["Oscar Mulero Shifting Signals", "Mulero Shifting"], "Spain"),
    ("Hector Oaks", "Broken Promises", "DE", ["Hector Oaks Broken Promises Kaos", "Hector Oaks Kaos"], "Berlin"),
    ("Answer Code Request", "Silhouettes", "DE", ["Answer Code Request Silhouettes", "ACR Silhouettes Ostgut"], "Berlin"),
    ("Pfirter", "Magnitude", "AR", ["Pfirter Magnitude MindTrip", "Pfirter MindTrip"], "Georgia / Eastern Europe"),
    ("Stanislav Tolkachev", "Zakat", "UA", ["Stanislav Tolkachev Zakat"], "Georgia / Eastern Europe"),
    ("SPFDJ", "Crumble", "NL/DE", ["SPFDJ Crumble", "Sarah Farina SPFDJ"], "Berlin"),
    ("Stef Mendesidis", "Kleisoura", "GR", ["Stef Mendesidis Kleisoura"], "Georgia / Eastern Europe"),
    ("Hadone", "Excess Body", "FR", ["Hadone Excess Body", "Hadone Possession"], "France"),
    ("Anetha", "Panorama", "FR", ["Anetha Panorama", "Anetha Mama Told Ya"], "France"),
    ("Introversion", "Dystopian Love", "UK", ["Introversion Dystopian Love"], "London"),
    ("AIROD", "Acid Attack", "FR", ["AIROD Acid Attack", "AIROD Arts"], "France"),
    ("Rosa Anschütz", "Radical Rituals", "DE", ["Rosa Anschutz Radical Rituals", "Rosa Anschutz"], "Berlin"),
    ("TRYM", "Karmic Debt", "SE", ["TRYM Karmic Debt"], "Sweden"),
    ("Regal", "Two Decades Of Silence", "ES", ["Regal Two Decades Silence Involve"], "Spain"),
    ("UVB", "Disfigure", "UK", ["UVB Disfigure", "UVB non series"], "London"),
    ("P.E.A.R.L.", "Shaman Works", "DE", ["PEARL Shaman Works", "P.E.A.R.L. Shaman"], "Berlin"),
]

def search(q):
    url = f"https://api.discogs.com/database/search?q={quote(q)}&type=release&per_page=5"
    headers = {"User-Agent":"TVA/1.0","Authorization":f"Discogs token={TOKEN}","Accept":"application/json"}
    try:
        with urlopen(Request(url, headers=headers), timeout=15) as resp:
            time.sleep(1.1)
            return json.loads(resp.read().decode("utf-8")).get("results", [])
    except Exception as e:
        print(f"  ERR: {e}")
        return []

def dl(url, dest):
    try:
        with urlopen(Request(url, headers={"User-Agent":"TVA/1.0"}), timeout=15) as r:
            d = r.read()
            if len(d) > 500:
                open(dest,"wb").write(d); return True
    except: pass
    return False

def color_of(path):
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB").resize((32,32))
        c = collections.Counter()
        for pr,pg,pb in list(img.getdata()):
            a=(pr+pg+pb)/3
            if a<10 or a>245: continue
            c[(pr>>4,pg>>4,pb>>4)]+=1
        if c:
            top=c.most_common(3)
            cs=[f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}" for (qr,qg,qb),_ in top]
            return cs[0], cs
    except: pass
    return None, []

def main():
    data = json.load(open(OUTPUT_FILE))
    existing_ids = {r["id"] for r in data["releases"]}
    existing_keys = {f"{(r.get('artist') or '').lower().strip()}|{(r.get('title') or '').lower().strip()}" for r in data["releases"]}

    added=failed=0
    for artist, title, country, queries, scene in MISSES:
        key = f"{artist.lower().strip()}|{title.lower().strip()}"
        if key in existing_keys:
            print(f"SKIP {artist} - {title}"); continue

        found = None
        tried = [f"{artist} {title}"] + queries
        for q in tried:
            results = search(q)
            # Loose match: artist word OR title first word in result
            a_first = artist.lower().split()[0]
            t_first = title.lower().split()[0]
            for r in results:
                t = (r.get("title") or "").lower()
                if (a_first in t) and (t_first in t):
                    found = r; break
            if found: break
            # Accept first result whose title contains either artist OR title token
            for r in results:
                t = (r.get("title") or "").lower()
                if a_first in t or t_first in t:
                    found = r; break
            if found: break
            if results:
                found = results[0]; break

        if not found:
            print(f"MISS: {artist} - {title}")
            failed += 1
            continue

        if found["id"] in existing_ids:
            print(f"DUP id for {artist} - {title}"); continue

        thumb = found.get("cover_image") or found.get("thumb") or ""
        image_path = ""
        if thumb:
            dest = IMAGES_DIR / f"{found['id']}.jpg"
            if dest.exists() or dl(thumb, str(dest)):
                image_path = f"images/{found['id']}.jpg"

        color, colors = (None, [])
        if image_path:
            fp = SCRIPT_DIR.parent / image_path
            if fp.exists():
                color, colors = color_of(str(fp))

        y = int(found.get("year") or 0)
        data["releases"].append({
            "id": found["id"], "title": title, "artist": artist, "year": y,
            "catno": found.get("catno",""), "thumb": thumb,
            "format": ", ".join(found.get("format",[])) if isinstance(found.get("format"),list) else str(found.get("format","")),
            "label": (found.get("label") or [""])[0] if isinstance(found.get("label"),list) else (found.get("label") or ""),
            "label_id": 0, "scene": scene,
            "discogs_url": f"https://www.discogs.com/release/{found['id']}",
            "image": image_path, "color": color, "colors": colors, "country": country,
        })
        existing_ids.add(found["id"]); existing_keys.add(key); added += 1
        print(f"+ {artist} - {title} ({y}) -> {scene}")

    data["meta"]["total"] = len(data["releases"])
    years = [r["year"] for r in data["releases"] if r.get("year",0) > 0]
    if years: data["meta"]["year_range"] = [min(years), max(years)]
    data["meta"]["scenes"] = sorted(set(r.get("scene") or "" for r in data["releases"]))
    json.dump(data, open(OUTPUT_FILE,"w"), separators=(",",":"))
    print(f"\n+{added} new, {failed} still missing — total {data['meta']['total']}")

if __name__ == "__main__":
    main()
