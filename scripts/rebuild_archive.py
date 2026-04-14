#!/usr/bin/env python3
"""Rebuild archive from scratch — ONLY @guestsixonetwo 374 titles."""

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

# ── All 374 entries as (search_query, scene) ─────────────────────────
# Manually cleaned for best Discogs search results
RELEASES = [
    # 1-10
    ("Reeko Exium Regenerative Circuits Mental Disorder", "Spain"),
    ("Atom TM Ground Loop Bunker New York", "Germany"),
    ("Delete Everything Untitled Sub Records", "London"),
    ("Neel The 808 Archive Non Series", "Italy"),
    ("Robert Hood Invincible M-Plant", "Detroit"),
    ("Stephen Brown Afterlife Djax Up Beats", "Netherlands"),
    ("Dimi Angelis NECH034 Nechto", "Georgia / Eastern Europe"),
    ("Speedy J Trails Electric Deluxe", "Netherlands"),
    ("Fluxion Prospect Chain Reaction", "Berlin"),
    ("Paul St Hilaire Ren Faith False Tuned", "Berlin"),
    # 11-20
    ("Basic Channel Quadrant Dub", "Berlin"),
    ("Steve Bicknell Lost Recordings 7 Cosmic", "London"),
    ("Silent Servant In Memoriam Tresor", "London"),
    ("Sterac Skreelah Nemec M-Plant", "Netherlands"),
    ("Dam Case Bunker 4008", "Netherlands"),
    ("Richie Hawtin Remixes Boot Sound America", "Canada"),
    ("Mike Parker Inversions Vol 2 Geophone", "New York"),
    ("Nas Illmatic Columbia", "New York"),
    ("Drexciya Deep Sea Dweller Shockwave", "Detroit"),
    ("British Murder Boys BMB6", "London"),
    # 21-30
    ("Richie Hawtin 006 Plus 8", "Canada"),
    ("Tin Man Love Sex Acid Keys Of Life", "Netherlands"),
    ("Cio D'Or Episode Prologue", "Italy"),
    ("Takaaki Itoh Things We've Made In Our Dreams WOLS", "Japan"),
    ("Nihad Tule Bauri 2 Stockholm LTD", "Sweden"),
    ("VSK APM Records", "Spain"),
    ("Sandwell District", "Berlin"),
    ("Regis Application Of Language 2 Downwards", "London"),
    ("Joel Inder Delusion Norrlands", "Sweden"),
    ("Surgeon Body Request Dynamic Tension", "London"),
    # 31-40
    ("Sub Records SUB016 compilation", "London"),
    ("Orbe Final Musik", "Spain"),
    ("Luigi Tozzi Bios Non Series", "Italy"),
    ("Developer Archive 09 Dynamic Reflection Korridor", "Berlin"),
    ("Sunil Sharper Sounds Blueprint", "London"),
    ("Charlton TAR20 Tar Hallow", "London"),
    ("Subvoice Electronic Music compilation", "Japan"),
    ("Marcel Dettmann Ostgut Ton album", "Berlin"),
    ("Donato Dozzy Vapors Dance Tresor", "Italy"),
    ("Jeff Mills Everyday Life Purpose Maker", "Detroit"),
    # 41-50
    ("Dimi Angelis Prologue Records", "Netherlands"),
    ("Surgeon BAW Bad Sector", "London"),
    ("Sule Tuareg Kultur Dekmantel", "Netherlands"),
    ("Anthony Shakir Frictionless FXHE", "Detroit"),
    ("Shifted Under Avian", "Berlin"),
    ("Francois X Blueprint Records", "France"),
    ("Diversity Of Electronica KL Records", "Berlin"),
    ("Modularz Modular 10", "Berlin"),
    ("Cassegrain Collabs 02 Arcing Seas", "Berlin"),
    ("Stanislav Tolkachev Mote Evolver", "Georgia / Eastern Europe"),
    # 51-60
    ("Charlton TAR17 Tar Hallow", "London"),
    ("Porter Ricks Porter Tresor", "Berlin"),
    ("Marcus Adam BKLYN 2 Infrastructure New York", "New York"),
    ("Reus Redefine Suba Records", "Spain"),
    ("Jeff Mills Microscopic Music Vol 2 Something", "Detroit"),
    ("Surgeon Tresor album", "London"),
    ("James Ruskin Form And Function Blueprint", "London"),
    ("Anton Pieete The News Rejected", "Berlin"),
    ("X100 Vol 3 100 Records compilation", "Berlin"),
    ("Modularz compilation", "Berlin"),
    # 61-70
    ("VSK Momentum Ear To Ground", "Spain"),
    ("Fadi Mohem Mohem 03", "Germany"),
    ("Jeff Mills Preview Axis", "Detroit"),
    ("Developer Archive 02 Developer Archive", "Berlin"),
    ("Oliver Rosemann Alexander Kowalski Muzzle Blast Recorded Things", "Berlin"),
    ("Cirkle Sonic Surge Sublunar", "Berlin"),
    ("Peter Van Hoesen Spacetime Time To Express", "Ghent / Brussels"),
    ("Inigo Kennedy Asymmetric 01", "London"),
    ("Blawan Bohm Ternesc", "London"),
    ("White Noise MXCLR 15", "Berlin"),
    # 71-80
    ("Stroboscopic Artefacts Monad Vol 1", "Berlin"),
    ("Pacou Radar", "Berlin"),
    ("Eduardo De La Calle Inter Elementary Forms Analog Solutions", "Spain"),
    ("Peter Van Hoesen Entropic Time To Express", "Ghent / Brussels"),
    ("Grovskopa Letvagen Avian", "Sweden"),
    ("SHXCXCHCXSH Linear S Avian", "Sweden"),
    ("Marbod 1", "Germany"),
    ("Rico Asylum Recordings", "London"),
    ("Takaaki Itoh WOLS 8 Landschaften Iori remix", "Japan"),
    ("CTSN Herdplatten", "Germany"),
    # 81-90
    ("Basic Channel BCD", "Berlin"),
    ("Steve Rachmad Balance", "Netherlands"),
    ("Mike Parker Inversion Geophone", "New York"),
    ("Subhead Volume 8", "Berlin"),
    ("DJ Surgeles Techum", "Spain"),
    ("Terence Fixmer Planete Rouge", "France"),
    ("Peter Van Hoesen Cosmic Entropy Archives Interieures", "Ghent / Brussels"),
    ("Raster Noton Various compilation", "Berlin"),
    ("Mike Parker Inversions Geophone", "New York"),
    ("Efdemin Decay Curle", "Hamburg"),
    # 91-100
    ("Jeroen Search Figures PCT", "Netherlands"),
    ("Truncate Untitled 78", "New York"),
    ("Oscar Mulero Cold Warm Up Recordings", "Spain"),
    ("Modularz 11", "Berlin"),
    ("KVNT Semantica Records", "Spain"),
    ("Jeff Mills If Tango Axis", "Detroit"),
    ("Jay Denham Shockwave Records", "Detroit"),
    ("Pan Sonic Panasonic Blast First", "Scandinavia"),
    ("Alva Noto Hybr:ID Noton", "Chemnitz / Dresden"),
    ("Truncate Untitled 72", "New York"),
    # 101-110
    ("Donato Dozzy Filo Loves The Acid Tresor", "Italy"),
    ("Kwartz Form And Void Polegroup Reeko remix", "Spain"),
    ("Terence Fixmer Le Terrible Electric Deluxe Marcel Dettmann", "France"),
    ("Eduardo De La Calle Rather Than Deep Semantica", "Spain"),
    ("Nihad Tule P Stockholm LTD", "Sweden"),
    ("Sleeparchive Tools & Sketches LP", "Berlin"),
    ("Plastikman Consumed In Key Chilly Gonzales Turbo", "Canada"),
    ("Steven Porter LR Wevil Neighbourhood", "London"),
    ("Takaaki Itoh WOLS 6 Oscar Mulero remix", "Japan"),
    ("Klankman Bunker Records", "Netherlands"),
    # 111-120
    ("Skee Mask 2012 Ilian Tape", "Munich"),
    ("Samuli Kemppi Dark Matter Mote Evolver", "Berlin"),
    ("Architectural 02", "Berlin"),
    ("Cassegrain Tin Man Infrastructure New York", "Berlin"),
    ("Vril 810 Giegling", "Germany"),
    ("Convextion album Down Low Music", "Detroit"),
    ("Regis In A Syrian Tongue Blackest Ever Black", "London"),
    ("Claude Young The Dexit Elypsia", "Detroit"),
    ("DJ Shufflemaster Elektronique Dweller Subvoice", "Japan"),
    ("Anthony Rother Omnitronic Omni Disc", "Germany"),
    # 121-130
    ("DJ Hell Totmacher Disko B", "Munich"),
    ("Robert Hood Moveable Parts Chapter 2 M-Plant", "Detroit"),
    ("Sigha I Am Apathy I Am Submission Blueprint", "London"),
    ("DJ Surgeles Cosmic Distance Markers Techum", "Spain"),
    ("Translated Various APM Records", "Spain"),
    ("Warzone Vol 1 compilation", "Berlin"),
    ("Developer Develop Dynamic Reflection", "Berlin"),
    ("Stockholm Limited P A", "Sweden"),
    ("Steve Rachmad Disturbance", "Netherlands"),
    ("Perc Vertigo Part 1 Perc Trax Forward Strategy Group", "London"),
    # 131-140
    ("Pacou State Of Mind Tresor album", "Berlin"),
    ("Iesope Drift S Element", "Japan"),
    ("Kilner Walk Type Avian", "Berlin"),
    ("1st Bass Slammed Down NovaMute", "London"),
    ("Steve Bicknell Several Streams Of Thought KR3", "London"),
    ("Female Pelotone Downwards", "London"),
    ("Paperclip People Basic Reshape Basic Channel", "Detroit"),
    ("Cassegrain Collabs 01 Arcing Seas", "Berlin"),
    ("Eduardo De La Calle Untitled Analog Solutions", "Spain"),
    ("RRR 012 Raw Raw Records", "Berlin"),
    # 141-150
    ("DJ Slip 808 To Nice Subvoice Healtz remix", "Japan"),
    ("Dis x3 Brothers In Mind Tresor Sender Berlin", "Berlin"),
    ("Function Untitled Infrastructure New York", "New York"),
    ("Steve Rachmad Cosmic Harmony", "Netherlands"),
    ("Stockholm LTD P Oto", "Sweden"),
    ("Developer Archive 05 Dynamic Reflection", "Berlin"),
    ("Abdulla Rashim Ecstasy", "Sweden"),
    ("Takaaki Itoh Planet Rhythm Group", "Japan"),
    ("Svreca AW02 Semantica", "Spain"),
    ("Mike Parker Inversion 3 Geophone", "New York"),
    # 151-160
    ("Oscar Mulero Reworked 01", "Spain"),
    ("Jeff Mills Chasing The Beat Axis", "Detroit"),
    ("Monolake Occam Imbalance Computer Music", "Berlin"),
    ("Porter Ricks Vol 1 Force Inc", "Berlin"),
    ("Maurizio M4.5", "Berlin"),
    ("Regis Asbestos Sleeparchive remix Infrastructure", "London"),
    ("Takaaki Itoh A Fancy Haircut Will Not Help You Planet Rhythm", "Japan"),
    ("Millsart Inner Life React", "Detroit"),
    ("Fumiya Tanaka Move Torema", "Japan"),
    ("Ryoji Ikeda Time And Space Staalplaat", "Japan"),
    # 161-170
    ("DJ Shufflemaster Chester Beatty Cloned Vinyl", "Japan"),
    ("Dax J Imperial Propaganda Monnom Black", "London"),
    ("Rene Wise Deprivation Enemy Records", "London"),
    ("Albert Van Abbe Raster Noton", "Berlin"),
    ("Psyk Lowdown", "Spain"),
    ("Samuli Kemppi New Iron Age Power Of Voltages", "Berlin"),
    ("Biosphere Novelty Waves Mark Bell remix Rands", "Scandinavia"),
    ("Luigi Tozzi Spiral Non Series", "Italy"),
    ("Abdulla Rashim Aksum", "Sweden"),
    ("Polson Ruskin Surface Records", "London"),
    # 171-180
    ("Various Concrete Lines compilation", "Berlin"),
    ("Astigmatic Vol 4 compilation", "Berlin"),
    ("Stanislav Tolkachev Nightshift Mote Evolver", "Georgia / Eastern Europe"),
    ("Surgeon Unnatural Blueprint", "London"),
    ("Subhead Volume 9", "Berlin"),
    ("Luigi Tozzi Meridians", "Italy"),
    ("Developer Archive 07 Dynamic Reflection", "Berlin"),
    ("Svreca Incubation Process Semantica", "Spain"),
    ("Tresor Darklight compilation", "Berlin"),
    ("Silent Servant Negative Fascination Hospital Productions", "London"),
    # 181-190
    ("Jeff Mills The Guardian Purpose Maker", "Detroit"),
    ("Monrella Report", "Berlin"),
    ("Superunknown", "Berlin"),
    ("Agony Forces Wild Innocence", "Berlin"),
    ("Subsoil Immaterial Archives compilation", "Berlin"),
    ("Terrence Dixon Minimalism Revision Tresor", "Detroit"),
    ("DJ Hell Meets R Records", "Munich"),
    ("Stanislav Tolkachev Walk Along The Bottom Mote Evolver", "Georgia / Eastern Europe"),
    ("426 Mono Middle", "Berlin"),
    ("Oliver Ho Film Non Plus", "London"),
    # 191-200
    ("James Ruskin Cipher Blueprint", "London"),
    ("Stockholm Limited Planets In Palm", "Sweden"),
    ("Woody McBride Basketball Heroes Peacefrog", "Detroit"),
    ("Chris Sattinger Think Less Thoughts", "Berlin"),
    ("DJ Slip Never Look Back Kid Subvoice", "Japan"),
    ("Steve Stoll Supernatural Synewave", "New York"),
    ("Regis Application Of Language Downwards", "London"),
    ("Takaaki Itoh Eleckee Electrique", "Japan"),
    ("65D Mavericks Defining The Symptom Blueprint", "London"),
    ("Anthony Linell Emerald Fluorescents Northern Electronics", "Sweden"),
    # 201-210
    ("Fumiya Tanaka Midnight Sundance", "Japan"),
    ("Jeff Mills The Other Day Axis", "Detroit"),
    ("Svreca Reinhaled AW08 Stanislav Tolkachev remix Semantica", "Spain"),
    ("Jonas Kopp HHH Figur", "Berlin"),
    ("SHXCXCHCXSH R Avian", "Sweden"),
    ("Mike Parker Vesuvio Tremors Geophone", "New York"),
    ("Black Sabbath Vertigo Records", "London"),
    ("Donato Dozzy Squadra Quadra VOS", "Italy"),
    ("Stanislav Tolkachev Edit 1", "Georgia / Eastern Europe"),
    ("British Murder Boys BMB Counterbalance", "London"),
    # 211-220
    ("Killawatt Reworked UK Red", "London"),
    ("Perc Modern Heads Perc Trax", "London"),
    ("Richie Hawtin DE9 NovaMute", "Canada"),
    ("Sleeparchive A Man Dies In The Street", "Berlin"),
    ("Scorp Atomitron", "Berlin"),
    ("Developer Archive 09 Dynamic Reflection", "Berlin"),
    ("Troy Northbound Dynamic Reflection Takaaki Itoh remix", "Berlin"),
    ("Fanon Flowers Hunt Patterns 2", "Berlin"),
    ("NTTR 909 TAR18 Tar Hallow", "London"),
    ("Mike Parker Vertebrae Waltz Geophone", "New York"),
    # 221-230
    ("Erosion 123", "Germany"),
    ("Biosphere Novelty Waves Rands Records", "Scandinavia"),
    ("Sleeparchive Recycle", "Berlin"),
    ("Damon Wild Synewave Records", "New York"),
    ("Blank Program We Need Input", "Germany"),
    ("Regis Divine Ritual Downwards", "London"),
    ("Surgeon Patience Dynamic Tension", "London"),
    ("Pacou Reel Techno Tresor", "Berlin"),
    ("Shifted AVN001 Avian", "Berlin"),
    ("Takaaki Itoh Nobody Can Take What Everybody Owns Planet Rhythm", "Japan"),
    # 231-240
    ("A Guy Called Gerald How Long Is Now Juice Box", "Manchester"),
    ("Chester Beatty Accelerate Records", "Japan"),
    ("Phil Barton Untitled Blueprint", "London"),
    ("Mike Parker Cyclic Intonations Geophone", "New York"),
    ("Outline Meets", "Berlin"),
    ("Morgan Wild Visionquest", "Berlin"),
    ("Steve Stoll Eldopa Synewave", "New York"),
    ("Philus PH", "Berlin"),
    ("Chance McDermott Return Of The Prophet 600", "Detroit"),
    ("Jay Denham Carjacker Shockwave", "Detroit"),
    # 241-250
    ("Cerrone Kluster DJ Hell Records", "France"),
    ("Jeff Rushin Irakli Records", "Georgia / Eastern Europe"),
    ("Spherical Coordinates Vector Projection", "Berlin"),
    ("Plastique 01 Night Vision", "Berlin"),
    ("Conrad Van Orton Autumn", "Spain"),
    ("Wata Igarashi Ciphers Midgar", "Japan"),
    ("Hallucinator Black Angel Chain Reaction", "Berlin"),
    ("SStrom Kiln VOAM", "Berlin"),
    ("Luigi Tozzi BLNDR Hypnus", "Italy"),
    ("Evigt Morker Helmet Of Bones Semantica", "Sweden"),
    # 251-260
    ("Maan Psyk Non Series", "Italy"),
    ("Christian Wunsch False Flag Pole Recordings", "Germany"),
    ("Terrence Dixon Point Of View Finest Blend", "Detroit"),
    ("Marco Lenzi Unfinished Business Fine Audio", "Italy"),
    ("Inigo Kennedy The Difficult Third Asymmetric", "London"),
    ("Cadency Gazing In A Social Hub Cabrera", "Spain"),
    ("Answer Code Request Main Mode Marcel Dettmann Records", "Berlin"),
    ("Brendon Moeller Work Ethics Electric Deluxe Ben Klock", "Berlin"),
    ("DeepChord Functional Extraits Soma", "Detroit"),
    ("Function Various Plates", "New York"),
    # 261-270
    ("Luigi Tozzi Bios 2 Non Series", "Italy"),
    ("Planetary Assault Systems Deep Bass Weight Ostgut Ton", "Berlin"),
    ("VSK Rawax APM", "Spain"),
    ("Vakula Svreca Semantica", "Spain"),
    ("Function Adjustments 3 Infrastructure New York", "New York"),
    ("Orphx Night Music Sonic Groove", "Canada"),
    ("Reeko Aletheia Polegroup", "Spain"),
    ("Svreca AW05 Semantica", "Spain"),
    ("Regis Speak Downwards", "London"),
    ("Surgeon Force And Form Dynamic Tension", "London"),
    # 271-280
    ("Fumiya Tanaka Unknown Perlon", "Japan"),
    ("Stanislav Tolkachev Looped Life Polegroup", "Georgia / Eastern Europe"),
    ("Modularz 13", "Berlin"),
    ("Klockworks Vol 1 compilation Ben Klock", "Berlin"),
    ("Charlton TAR16 Tar Hallow", "London"),
    ("Sliwinski Presents Speaker Attack", "Netherlands"),
    ("Planetary Assault Systems Planetary Funk Peacefrog", "Berlin"),
    ("Stanislav Tolkachev Acropolis 24H Marthial remix", "Georgia / Eastern Europe"),
    ("Skee Mask Serum Ilian Tape", "Munich"),
    ("Ulwhednar LP Northern Electronics", "Sweden"),
    # 281-290
    ("The Fear Ratio Skana Blueprint", "London"),
    ("British Murder Boys BMB5 Counterbalance", "London"),
    ("Timeblind Detelevised Missile Records", "London"),
    ("Pacou A Universal Movement Tresor", "Berlin"),
    ("Charlton TAR15 Tar Hallow", "London"),
    ("Sequential Circuits Soul Person", "Detroit"),
    ("Architectural Cubismo", "Berlin"),
    ("Jeroen Search Darknez", "Netherlands"),
    ("Zadig Londinium Children Of Tomorrow", "France"),
    ("Abdulla Rashim Axel Hallqvist Sorunda", "Sweden"),
    # 291-300
    ("Modular Side M Music", "Berlin"),
    ("Brendon Moeller Work Ethics Electric Deluxe", "Berlin"),
    ("Bandulu Bisness Basic Channel", "Berlin"),
    ("Eduardo De La Calle My Own Transition Analog Solutions", "Spain"),
    ("Caterina Barbieri Vertical Cassauna", "Italy"),
    ("SHXCXCHCXSH Strgths Rcnstrctns Avian", "Sweden"),
    ("TM404 Kontra Musik", "Sweden"),
    ("Kvantti Semantica", "Spain"),
    ("Exium Developer Nheoma", "Spain"),
    ("UUN Sacred Seven SI Modern Cathedrals", "Berlin"),
    # 301-310
    ("Various Futuristic Experiments Background Records", "Berlin"),
    ("Sleeparchive Paper Cup", "Berlin"),
    ("Stockholm Limited P Mnemosyne", "Sweden"),
    ("Oscar Mulero Elementary Geometry Faut Section Lewis Fautzi", "Spain"),
    ("The Other People Place Lifestyles Of The Laptop Cafe Warp", "Detroit"),
    ("Steve Stoll Damon Wild Synewave", "New York"),
    ("The Advent Monastic Kombination Research", "Germany"),
    ("Pacou Isomorphic Raw Raw Records", "Berlin"),
    ("Basic Channel Radiance", "Berlin"),
    ("Robert Hood Technatural M-Plant", "Detroit"),
    # 311-320
    ("Function Dielectric Coefficient Infrastructure New York", "New York"),
    ("Phil Kieran Jochem Paap Skudge", "London"),
    ("Oscar Mulero Black Propaganda Reconstructed Warm Up Lucy remix", "Spain"),
    ("Terrence Dixon Bionic Man Tresor", "Detroit"),
    ("Orbe Psyk Final Musik", "Spain"),
    ("Surgeon First Tresor", "London"),
    ("Conrad Van Orton VSK APM", "Spain"),
    ("Music From The Basement Part 1 Trautmuzik compilation", "Berlin"),
    ("Rumenige Numb 5 Raummusik", "Berlin"),
    ("Fanon Flowers Hunt Patterns", "Berlin"),
    # 321-330
    ("Adriana Lopez Embera Semantica", "Spain"),
    ("Claudio PRC Ness Figur", "Italy"),
    ("UVB What I've Learned", "Berlin"),
    ("Stockholm LTD P Remix 1 Shifted remix", "Sweden"),
    ("Jeroen Search Figures PCT Search Records", "Netherlands"),
    ("Echologist Records", "Berlin"),
    ("Various Spectrum 33 On The 5th Day", "Berlin"),
    ("DJ ESP Sick And Tired", "Spain"),
    ("Alex Cortex Bathyal", "Germany"),
    ("Semantica Non Native 04 compilation", "Spain"),
    # 331-340
    ("Jonas Kopp Echologist Figur", "Berlin"),
    ("Etapp Kyle Continuum Unterton", "Berlin"),
    ("DJ Nobu Extra Tools Future Noise", "Japan"),
    ("Geophone GPH 135 Mike Parker Donato Dozzy remix", "New York"),
    ("Stanislav Tolkachev The Fridge Mote Evolver", "Georgia / Eastern Europe"),
    ("Surgeon Convenience Trap Dynamic Tension", "London"),
    ("Cio D'Or Magnetfluss Prologue Silent Servant remix", "Italy"),
    ("Nihad Tule Bauri Stockholm LTD", "Sweden"),
    ("Jesper Dahlback Nima Khak Norrlands", "Sweden"),
    ("Troy Slow Burn Dynamic Reflection", "Berlin"),
    # 341-350
    ("Selected Edits 4 Giorgio Gigli Edit Select Cassegrain", "Berlin"),
    ("Orphx Other Voices Sonic Groove", "Canada"),
    ("KR 035 compilation KR Records", "Berlin"),
    ("Marco Shuttle Modula Dynavision", "Italy"),
    ("DC11 Stroboscopic Slow Motion", "Italy"),
    ("Abdulla Rashim Semi Enterara", "Sweden"),
    ("Linear System Minkowski Dokument Alarico remix", "Berlin"),
    ("Wata Igarashi Counter Pulse Series 8 Iori remix", "Japan"),
    ("LSD Second Process Accelerate", "Japan"),
    ("Reeko Architectural Mental Disorder", "Spain"),
    # 351-360
    ("Rene Wise Moving Pressure 02", "London"),
    ("Korridor Path Dynamic Reflection", "Germany"),
    ("Danza Nativa 5 Years Part 1 compilation", "Spain"),
    ("Developer DJ Surgeles Sound Works", "Berlin"),
    ("Hiroaki Iizuka The Run JTIJN remix", "Japan"),
    ("Raiz Curandero Lo-Fi Records", "Italy"),
    ("Jeroen Search Records", "Netherlands"),
    ("Pearl Four Cardinal Svreca remix Falling Ethics", "Italy"),
    ("Warsaw Admixture Series 2 Admiral Records", "Georgia / Eastern Europe"),
    ("DJ Shufflemaster Playback Part 3 Subvoice", "Japan"),
    # 361-374
    ("Population One The Return M-Plant", "Detroit"),
    ("Unhuman", "London"),
    ("Paul Birken Acid Youth Of Malibu Blawan remix Ear Wiggle", "London"),
    ("Space DJZ Side On Peacefrog", "Detroit"),
    ("The Blunted Boy Wonder Presents Alphabet Set", "Detroit"),
    ("Iesope Drift People Drift Element", "Japan"),
    ("Christian Bor Life Divine Tresor", "Berlin"),
    ("Keith Tucker Detroit Saved My Soul Synthetic", "Detroit"),
    ("Steve Bicknell Lost Recordings 2 Cosmic", "London"),
    ("Pacou Sound Device Tresor", "Berlin"),
    ("DeepChord DC12", "Detroit"),
    ("Steve O'Sullivan Une Moss Records", "London"),
    ("James Ruskin Into A Circle Blueprint", "London"),
    ("Roiseux Fred Editions Mego", "Germany"),
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
            colors = [
                f"#{(qr<<4)|8:02x}{(qg<<4)|8:02x}{(qb<<4)|8:02x}"
                for (qr, qg, qb), _ in top
            ]
            return colors[0], colors
    except:
        pass
    return None, []


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Start from empty
    data = {
        "meta": {"total": 0, "labels": 0, "scenes": [], "year_range": [0, 0]},
        "geo": {
            "Detroit": [42.3314, -83.0458],
            "Berlin": [52.5200, 13.4050],
            "London": [51.5074, -0.1278],
            "Cologne": [50.9375, 6.9603],
            "Frankfurt": [50.1109, 8.6821],
            "Hamburg": [53.5511, 9.9937],
            "Munich": [48.1351, 11.5820],
            "Chemnitz / Dresden": [51.0504, 13.7373],
            "Sheffield / Leeds": [53.8008, -1.5491],
            "Manchester": [53.4808, -2.2426],
            "Ghent / Brussels": [50.8503, 4.3517],
            "Netherlands": [52.3676, 4.9041],
            "Chicago": [41.8781, -87.6298],
            "New York": [40.7128, -74.0060],
            "Japan": [35.6762, 139.6503],
            "Canada": [43.6532, -79.3832],
            "Italy": [41.9028, 12.4964],
            "Spain": [40.4168, -3.7038],
            "France": [48.8566, 2.3522],
            "Sweden": [59.3293, 18.0686],
            "Georgia / Eastern Europe": [41.7151, 44.8271],
            "Scandinavia": [59.9139, 10.7522],
            "Germany": [51.1657, 10.4515],
            "São Paulo": [-23.5505, -46.6333],
        },
        "releases": [],
    }

    existing_ids = set()
    existing_titles = set()
    added = 0
    failed = 0
    fail_list = []

    for i, (query, scene) in enumerate(RELEASES):
        result = search_discogs(query)
        if not result:
            print(f"  NOT FOUND [{i+1}]: {query}")
            fail_list.append((i + 1, query))
            failed += 1
            continue

        if result["id"] in existing_ids:
            continue

        key = f"{result['artist'].lower()}|{result['title'].lower()}"
        if key in existing_titles:
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

        # Extract label hint from query
        words = query.split()
        label = words[-1] if len(words) > 2 else scene

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
            print(f"  [{i+1}/{len(RELEASES)}] +{added} added, {failed} failed")
            # Checkpoint
            if added % 50 == 0:
                _save(data)
                print(f"  (checkpoint: {added} releases saved)")

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

    _save(data)

    print(f"\n{'='*50}")
    print(f"Archive rebuilt: {added} releases from {len(RELEASES)} entries")
    print(f"Failed: {failed}")
    print(f"Final (after dedup): {data['meta']['total']} releases")
    if fail_list:
        print(f"\nNot found ({len(fail_list)}):")
        for num, q in fail_list:
            print(f"  [{num}] {q}")


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
