#!/usr/bin/env python3
"""Rebuild archive from expanded @guestsixonetwo list (662 entries)."""

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
SOURCE_FILE = Path("/Users/humbertomacbook/Downloads/guestsixonetwo_posts.md")

# ── Artist name cleanup ──────────────────────────────────────────────
ARTIST_MAP = {
    "keithtucker": "Keith Tucker",
    "dopplereffekt": "Dopplereffekt",
    "missdjax": "Miss Djax",
    "jeffmills": "Jeff Mills",
    "juanatkins": "Juan Atkins",
    "stevestoll": "Steve Stoll",
    "helenahauff": "Helena Hauff",
    "stanislavtolkachev": "Stanislav Tolkachev",
    "stanislvtolkachev": "Stanislav Tolkachev",
    "mikeparker": "Mike Parker",
    "marcoshuttle": "Marco Shuttle",
    "thewisecaucasian": "The Wise Caucasian",
    "theevader": "The Evader",
    "rhythmandsound": "Rhythm & Sound",
    "psykoffuk": "Psykofuk",
    "planetaryassaultsystems": "Planetary Assault Systems",
    "djskull": "DJ Skull",
    "jamiebissmire": "Jamie Bissmire",
    "djesp": "DJ ESP",
    "damonwild": "Damon Wild",
    "silentservant": "Silent Servant",
    "christianw": "Christian Wunsch",
    "oliverrosemann": "Oliver Rosemann",
    "nihadtule": "Nihad Tule",
    "claudeyoung": "Claude Young",
    "terrencedixon": "Terrence Dixon",
    "marceldettmann": "Marcel Dettmann",
    "fadimohem": "Fadi Mohem",
    "anthonyrother": "Anthony Rother",
    "donatodozzy": "Donato Dozzy",
    "aphextwin": "Aphex Twin",
    "dasharush": "Dasha Rush",
    "wataigarashi": "Wata Igarashi",
    "eduardodelacalle": "Eduardo De La Calle",
    "oscarmulero": "Oscar Mulero",
    "dimiang": "Dimi Angelis",
    "heikolaux": "Heiko Laux",
    "djslip": "DJ Slip",
    "alexcortex": "Alex Cortex",
    "steveosullivan": "Steve O'Sullivan",
    "chesterbeatty": "Chester Beatty",
    "albertvanabbe": "Albert Van Abbe",
    "shxcxchcxsh": "SHXCXCHCXSH",
    "daveclarke": "Dave Clarke",
    "jamesruskin": "James Ruskin",
    "stewartswalker": "Stewart Walker",
    "oliverho": "Oliver Ho",
    "stevebicknell": "Steve Bicknell",
    "rinocerrone": "Rino Cerrone",
    "djshufflemaster": "DJ Shufflemaster",
    "richiehawtin": "Richie Hawtin",
    "christianmorgenstern": "Christian Morgenstern",
    "babyford": "Baby Ford",
    "plastikman": "Plastikman",
    "djt1000": "DJ T-1000",
    "arthurrobert": "Arthur Robert",
    "fanonflowers": "Fanon Flowers",
    "roberthood": "Robert Hood",
    "atomtm": "Atom TM",
    "benssims": "Ben Sims",
    "charlesming": "Charles Mingus",
    "charlesmingus": "Charles Mingus",
    "andystott": "Andy Stott",
    "takaakiitoh": "Takaaki Itoh",
    "petervanhoesen": "Peter Van Hoesen",
    "inigokennedy": "Inigo Kennedy",
    "thesuburbanknight": "The Suburban Knight",
    "jaydenham": "Jay Denham",
    "joeybeltram": "Joey Beltram",
    "djstingray313": "DJ Stingray 313",
    "renewise": "Rene Wise",
    "lewisfautzi": "Lewis Fautzi",
    "fumiyatanaka": "Fumiya Tanaka",
    "carilekebusch": "Cari Lekebusch",
    "thomasbrinkmann": "Thomas Brinkmann",
    "danielbell": "Daniel Bell",
    "davidgnuoy": "David Gnuoy",
    "thebluntedboywonder": "The Blunted Boy Wonder",
    "garymartin": "Gary Martin",
    "adambeyer": "Adam Beyer",
    "basmooy": "Bas Mooy",
    "populationone": "Population One",
    "deepchord": "DeepChord",
    "answercoderequest": "Answer Code Request",
    "lukeslater": "Luke Slater",
    "kangdingray": "Kangding Ray",
    "model500": "Model 500",
    "vladislavdelay": "Vladislav Delay",
    "benales": "Ben Ales",
    "freddiefresh": "Freddie Fresh",
    "hieroglyphicbeing": "Hieroglyphic Being",
    "brendonmoeller": "Brendon Moeller",
    "giorgiogigli": "Giorgio Gigli",
    "anthonyshakir": "Anthony Shakir",
    "anthonyshakeshakir": "Anthony Shakir",
    "terencefixmer": "Terence Fixmer",
    "abdullarashim": "Abdulla Rashim",
    "jeroensearch": "Jeroen Search",
    "spacedjz": "Space DJZ",
    "deleteeverything": "Delete Everything",
    "tinman": "Tin Man",
    "ciodor": "Cio D'Or",
    "porterricks": "Porter Ricks",
    "basicchannel": "Basic Channel",
    "stephenbrown": "Stephen Brown",
    "speedyj": "Speedy J",
    "paulsthilaire": "Paul St Hilaire",
    "britishmurderboys": "British Murder Boys",
    "paperclippeople": "Paperclip People",
    "samulikemppi": "Samuli Kemppi",
    "stevenporter": "Steven Porter",
    "convextion": "Convextion",
    "djsurgeles": "DJ Surgeles",
    "luigitozzi": "Luigi Tozzi",
    "ryojiikeda": "Ryoji Ikeda",
    "daxj": "Dax J",
    "the65dmavericks": "The 65D Mavericks",
    "anthonylinell": "Anthony Linell",
    "jonaskopp": "Jonas Kopp",
    "alvanoto": "Alva Noto",
    "skeemask": "Skee Mask",
    "millsart": "Millsart",
    "blawan": "Blawan",
    "marcusadam": "Marcus Adam",
    "conradvanorton": "Conrad Van Orton",
    "marcolenzi": "Marco Lenzi",
    "caterinabarbieri": "Caterina Barbieri",
    "theotherpeopleplace": "The Other People Place",
    "theadvent": "The Advent",
    "pansonic": "Pan Sonic",
    "hiroakiiizuka": "Hiroaki Iizuka",
    "jesperdahlb": "Jesper Dahlback",
    "paulbirken": "Paul Birken",
    "iesopedrift": "Iesope Drift",
    "christianbor": "Christian Bor",
    "stevestoll": "Steve Stoll",
    "roiseux": "Roiseux",
    "kerrichandler": "Kerri Chandler",
    "model600": "Model 600",
    "adamx": "Adam X",
    "neillandstrumm": "Neil Landstrumm",
    "stevepoindexter": "Steve Poindexter",
    "portionreform": "Portion Reform",
    "kenishii": "Ken Ishii",
    "suburbanknight": "Suburban Knight",
    "gherkinjerks": "Gherkin Jerks",
    "forwardstrategygroup": "Forward Strategy Group",
    "claudioprc": "Claudio PRC",
    "markbroom": "Mark Broom",
    "zenkerbrothers": "Zenker Brothers",
    "theoparrish": "Theo Parrish",
    "setaocmass": "Setaoc Mass",
    "benklock": "Ben Klock",
    "hectoroaks": "Hector Oaks",
    "byetone": "Byetone",
    "woodymcbride": "Woody McBride",
    "voicesfromthelake": "Voices From The Lake",
    "sandwelldistrict": "Sandwell District",
    "palicavonzvreca": "Palica Von Zvreca",
    "freddiefresh": "Freddie Fresh",
    "skynet313": "Skynet 313",
    "stevereich": "Steve Reich",
    "nastiareigel": "Nastia Reigel",
    "taylordeupree": "Taylor Deupree",
    "jenseninterceptor": "Jensen Interceptor",
    "lossofbalance": "Loss Of Balance",
    "digitalprincezz": "Digital Princezz",
    "christianbloch": "Christian Bloch",
    "lawilliams": "LA Williams",
    "brotherfromanotherplanet": "Brother From Another Planet",
    "fixmer": "Fixmer",
    "mccarthy": "McCarthy",
}

# ── Word splitting dictionary ────────────────────────────────────────
# Common words found in techno release titles
WORDS = set("""
the of a in from to for and on at by is it no my we you all are was his her she
he not but or can if so up do go me us our let its has had did get got run cut
set put hit bit sat hot man men new old big red low raw two one six ten day way
end own out off back down into over come here more some time take make give look
find work part last long great first after before still every never under above
light dark night black white sound music deep acid bass soul love life mind body
dead live real true full fast hard soft high slow free pure cold warm fire water
earth star moon sun space world city street house room door side hand head face
eye heart blood bone skin hell angel ghost demon dream sleep wake dance move
drive ride walk swim fly fall rise turn break burn build change close open play
stop start stand stay sit step talk tell think feel hear see know want need fear
hope wish wait watch call ask answer try keep hold read write send bring buy sell
pay draw pull push throw catch pick drop hang lay lead leave lose win beat fight
kill die born grow seem become begin continue follow return balance archive
assault digital dimension drum dub echo electric electronic entropy filter flux
force form frequency function future groove industrial inversion iron kick laser
linear loop machine magnetic master matter metal micro minimal mix mode modular
mono morph motor movement mute nerve neural noise nuclear orbit organic oscillate
output parallel pattern phase physical planet plasma point pole pressure process
program protocol pulse quantum radar raw reactor record reflect reform resonance
rhythm robot rotate sample satellite scan sequence shadow shift signal silent
sonic spiral state static steel storm stream string structure sub surface surge
sustain sweep synth system techno tempo tension terminal tone track trans
transmission trap tremor trigger tunnel turbo ultra unit valve vector velocity
version vertical vibrate void voltage volume vortex wave weight wire zone
regenerative circuits ground prospect faith quadrant invincible afterlife trails
prospect district application language body request sharper sounds vapors
everyday microscopic preview spacetime entropic cosmic entropy decay inversions
momentum sonic cipher form function angeli tuareg frictionless under
diversity electronica modular collabs porter surgeon dettmann shifted
basic channel murder boys planetary assault blueprint semantic prologue
architectural infrastructure geophone avian klockworks mote evolver club
golden ratio prophecy sacred presents remixes untitled episode original
borderland divine ritual katmoda infophysix sessions darkness invincible
recent actioreactio hardmatter warmcurrents transport solarlimb shellwave
dweller icons empire desires flauto synthetico nightfever hats required
carrier seem miyah rawfromanger regiment nature basketball heroes
subtractive synthesis strike doremifasola history survivors evil planete
everything ruined allies oktoberfest phantasma labyrinth livefrom
somewhere security masterside hallucination nocomment tradebeliefs
curators klockworks qqqo noonesdriving huyendo telic teensonfire
mannella bleaching agent starkit imagery keeper moah zylacanth train
thought metaphor lostrecordings howcanweknow redefined dbgii fastsequence
applications remixes mingus ahum contrasto backward improvement
elektronique remixes callitwhatyouwant acidtracks firsttrip bleepazoid
gemclub normalre substation talleric jetset lovelife hydrostatic
equilibrium aboveustoday apex activeline coalescence perception
kronotop nothingproduces stark slowhand beatbox crossinthemadmoon
lunemex undoground soundtrack special edition tangent excavations
inkblots gameone thinkquick floorshow covert operations dopplershift
posttraumatic transcendence comes darkness vilna hagagatan drained
frontier firstcontact fallofbecause walkalonethebottom disciplina
mitologem focux bendyourears nocturbulouss anomie objective
cosmopolitan startitup carrier justcloseyoureyes soliton nullphysics
bloodofourking anotherone luckynumber7 gravitywontholdme presents
humanpattern teensfire wearedtroit therogue blaktony
""".split())


def split_smashed(text):
    """Try to add spaces to smashedtogether words."""
    if len(text) < 5 or " " in text:
        return text
    # Try greedy longest match from dictionary
    result = []
    i = 0
    while i < len(text):
        best = 1
        for end in range(min(i + 20, len(text)), i, -1):
            candidate = text[i:end].lower()
            if candidate in WORDS and len(candidate) > 2:
                best = end - i
                break
        result.append(text[i : i + best])
        i += best
    split = " ".join(result)
    # If splitting didn't help much, return original
    if len(split.split()) <= 1:
        return text
    return split


# ── Scene assignment ─────────────────────────────────────────────────
ARTIST_SCENES = {
    "jeffmills": "Detroit", "roberthood": "Detroit", "drexciya": "Detroit",
    "millsart": "Detroit", "populationone": "Detroit", "anthonyshakir": "Detroit",
    "claudeyoung": "Detroit", "keithtucker": "Detroit", "paperclippeople": "Detroit",
    "jaydenham": "Detroit", "terrencedixon": "Detroit", "deepchord": "Detroit",
    "theotherpeopleplace": "Detroit", "spacedjz": "Detroit", "convextion": "Detroit",
    "woodymcbride": "Detroit", "thebluntedboywonder": "Detroit", "model500": "Detroit",
    "juanatkins": "Detroit", "dopplereffekt": "Detroit", "cybotron": "Detroit",
    "thesuburbanknight": "Detroit", "suburbanknight": "Detroit", "infiniti": "Detroit",
    "danielbell": "Detroit", "joeybeltram": "Detroit", "stevepoindexter": "Detroit",
    "gherkinjerks": "Chicago", "genehunt": "Detroit", "djt1000": "Detroit",
    "lukehess": "Detroit", "model600": "Detroit", "djbone": "Detroit",
    "omars": "Detroit", "thevision": "Detroit", "vice": "Detroit",
    "kerrichandler": "New York", "skynet313": "Detroit",
    "surgeon": "London", "regis": "London", "britishmurderboys": "London",
    "bmb": "London", "perc": "London", "silentservant": "London", "blawan": "London",
    "female": "London", "sigha": "London", "inigokennedy": "London",
    "jamesruskin": "London", "oliverho": "London", "the65dmavericks": "London",
    "thefearratio": "London", "sunil": "London", "charlton": "London",
    "stevebicknell": "London", "daxj": "London", "renewise": "London",
    "timeblind": "London", "killawatt": "London", "daveclarke": "London",
    "kerridge": "London", "makaton": "London", "marcal": "London",
    "positivecentre": "London", "benlong": "London", "portionreform": "London",
    "neillandstrumm": "London", "ovr": "London", "mannella": "London",
    "mylesserg": "London", "lukeslater": "London",
    "donatodozzy": "Italy", "luigitozzi": "Italy", "marcoshuttle": "Italy",
    "neel": "Italy", "ciodor": "Italy", "caterinabarbieri": "Italy",
    "claudioprc": "Italy", "marcolenzi": "Italy", "dleria": "Italy",
    "rinocerrone": "Italy", "raiz": "Italy", "dc11": "Italy", "pearl": "Italy",
    "voicesfromthelake": "Italy", "leiras": "Italy",
    "takaakiitoh": "Japan", "fumiyatanaka": "Japan", "djshufflemaster": "Japan",
    "djnobu": "Japan", "wataigarashi": "Japan", "hiroakiiizuka": "Japan",
    "ryojiikeda": "Japan", "chesterbeatty": "Japan", "kenishii": "Japan",
    "petervanhoesen": "Ghent / Brussels",
    "shxcxchcxsh": "Sweden", "nihadtule": "Sweden", "abdullarashim": "Sweden",
    "anthonylinell": "Sweden", "joelinder": "Sweden", "jesperdahlb": "Sweden",
    "grovskopa": "Sweden", "tm404": "Sweden", "ulwhednar": "Sweden",
    "tilliander": "Sweden", "carilekebusch": "Sweden",
    "stanislavtolkachev": "Georgia / Eastern Europe",
    "stanislvtolkachev": "Georgia / Eastern Europe",
    "pacou": "Berlin", "marceldettmann": "Berlin", "basicchannel": "Berlin",
    "porterricks": "Berlin", "monolake": "Berlin", "sandwell": "Berlin",
    "sandwelldistrict": "Berlin", "maurizio": "Berlin", "sleeparchive": "Berlin",
    "developer": "Berlin", "developr": "Berlin", "shifted": "Berlin",
    "cassegrain": "Berlin", "planetaryassaultsystems": "Berlin",
    "answercoderequest": "Berlin", "paulsthilaire": "Berlin", "fluxion": "Berlin",
    "etappkyle": "Berlin", "samulikemppi": "Berlin", "jonaskopp": "Berlin",
    "christianbor": "Berlin", "brendonmoeller": "Berlin", "troy": "Berlin",
    "shed": "Berlin", "benklock": "Berlin", "hectoroaks": "Berlin",
    "rrose": "Berlin", "arthurrobert": "Berlin", "vril": "Berlin",
    "helenahauff": "Berlin", "rodhad": "Berlin", "phasefatale": "Berlin",
    "benssims": "Berlin", "rod": "Berlin", "setaocmass": "Berlin",
    "amotik": "Berlin", "heikolaux": "Berlin", "temudo": "Berlin",
    "zenkerbrothers": "Berlin", "stenny": "Berlin", "forwardstrategygroup": "Berlin",
    "oscarmulero": "Spain", "reeko": "Spain", "svreca": "Spain",
    "eduardodelacalle": "Spain", "kwartz": "Spain", "adrianalopez": "Spain",
    "orbe": "Spain", "vsk": "Spain", "conradvanorton": "Spain",
    "exium": "Spain", "reus": "Spain", "cadency": "Spain", "psyk": "Spain",
    "lossofbalance": "Spain", "aiken": "Spain", "djesp": "Spain",
    "function": "New York", "mikeparker": "New York", "marcusadam": "New York",
    "stevestoll": "New York", "damonwild": "New York", "truncate": "New York",
    "dasharush": "New York",
    "richiehawtin": "Canada", "plastikman": "Canada", "orphx": "Canada",
    "speedyj": "Netherlands", "sterac": "Netherlands", "steverachmad": "Netherlands",
    "damcase": "Netherlands", "dimiang": "Netherlands", "dimi": "Netherlands",
    "stephenbrown": "Netherlands", "klankman": "Netherlands", "missdjax": "Netherlands",
    "djskull": "Chicago", "deeon": "Chicago", "phuture": "Chicago",
    "francoisx": "France", "zadig": "France", "terencefixmer": "France",
    "fixmer": "France", "cerrone": "France",
    "alvanoto": "Chemnitz / Dresden", "byetone": "Chemnitz / Dresden",
    "kangdingray": "Chemnitz / Dresden",
    "efdemin": "Hamburg", "skeemask": "Munich", "hell": "Munich", "djhell": "Munich",
    "anthonyrother": "Germany", "thomasbrinkmann": "Germany",
    "biosphere": "Scandinavia", "pansonic": "Scandinavia",
    "nas": "New York", "blacksabbath": "London",
    "aguycalledgerald": "Manchester", "andystott": "Manchester",
    "aphextwin": "Sheffield / Leeds", "afx": "Sheffield / Leeds",
    "stevereich": "New York", "charlesmingus": "New York",
    "vladislavdelay": "Scandinavia", "taylordeupree": "New York",
    "adambeyer": "Sweden", "basmooy": "Netherlands",
    "fadimohem": "Germany", "fanonflowers": "Berlin",
    "monrella": "Berlin", "stewartswalker": "Berlin",
    "psykoffuk": "London", "babyford": "London",
    "adamx": "New York", "giorgiogigli": "Italy",
    "theoparrish": "Detroit", "lewisfautzi": "Spain",
}

LABEL_SCENES = {
    "tresor": "Berlin", "ostgut": "Berlin", "basicchannel": "Berlin",
    "chainreaction": "Berlin", "raster": "Berlin", "stroboscopic": "Berlin",
    "avian": "Berlin", "sandwell": "Berlin", "marceldettmann": "Berlin",
    "klockworks": "Berlin", "raummusik": "Berlin", "monnom": "Berlin",
    "figur": "Berlin", "dynamicreflection": "Berlin", "rawraw": "Berlin",
    "modularz": "Berlin", "falsetuned": "Berlin", "connwax": "Berlin",
    "50weapons": "Berlin", "mordrecords": "Berlin",
    "blueprint": "London", "downwards": "London", "counterbalance": "London",
    "dynamictension": "London", "perctrax": "London", "moteevolver": "London",
    "nonplus": "London", "missile": "London", "badsector": "London",
    "cosmicrecords": "London", "tarhallow": "London", "asymmetric": "London",
    "novamute": "London", "enemy": "London", "contort": "London",
    "mplant": "Detroit", "axis": "Detroit", "purposemaker": "Detroit",
    "shockwave": "Detroit", "fxhe": "Detroit", "metroplex": "Detroit",
    "undergroundresistance": "Detroit", "7thcity": "Detroit",
    "peacefrog": "London", "blacknation": "Detroit",
    "geophone": "New York", "infrastructure": "New York",
    "sonicgroove": "New York", "hospitalproductions": "New York",
    "synewave": "New York", "propernycrecords": "New York",
    "nonseries": "Italy", "hypnus": "Italy", "prologue": "Italy",
    "dynavision": "Italy", "fineaudio": "Italy", "lofi": "Italy",
    "spaziodisponibile": "Italy", "fallingethics": "Italy",
    "elettronicaromana": "Italy",
    "electricdeluxe": "Netherlands", "bunker": "Netherlands",
    "search": "Netherlands", "djax": "Netherlands", "rachmad": "Netherlands",
    "dekmantel": "Netherlands", "keysoflife": "Netherlands",
    "speakerattack": "Netherlands", "delsin": "Netherlands",
    "stockholmltd": "Sweden", "stockholmlimited": "Sweden",
    "norrlands": "Sweden", "northernelectronics": "Sweden",
    "kontramusik": "Sweden", "abdullarashim": "Sweden", "skudge": "Sweden",
    "drumcode": "Sweden", "sloboda": "Sweden",
    "wols": "Japan", "planetrhythm": "Japan", "subvoice": "Japan",
    "futurenoise": "Japan", "torema": "Japan", "counterpulse": "Japan",
    "accelerate": "Japan", "clonedvinyl": "Japan",
    "illiantape": "Munich", "giegling": "Germany",
    "noton": "Chemnitz / Dresden", "rasternoton": "Chemnitz / Dresden",
    "editionsmego": "Germany",
    "mentaldisorder": "Spain", "polegroup": "Spain", "warmup": "Spain",
    "semantica": "Spain", "fautsection": "Spain", "apm": "Spain",
    "eartoground": "Spain", "analogsolutions": "Spain",
    "finalmusik": "Spain", "suba": "Spain", "cabrera": "Spain",
    "rhod": "Spain", "historiayviolencia": "Spain",
    "plus8": "Canada", "turbo": "Canada",
    "warp": "Sheffield / Leeds",
    "planete": "France", "childrenoftomorrow": "France",
    "nechto": "Georgia / Eastern Europe", "24h": "Georgia / Eastern Europe",
    "rephlexrecords": "Sheffield / Leeds", "rephlex": "Sheffield / Leeds",
    "kanzleramt": "Germany", "ernstrecords": "Germany",
    "combinationresearch": "Germany", "kombination": "Germany",
    "timetoexpress": "Ghent / Brussels", "archivesinteriures": "Ghent / Brussels",
    "columbia": "New York", "disko": "Munich",
    "token": "Berlin", "jealousgod": "Berlin", "keyviny": "Berlin",
    "ground": "London", "imbalance": "Berlin",
    "forceincmusicworks": "Frankfurt", "forceinc": "Frankfurt",
    "din": "Germany", "echocord": "Berlin",
    "mord": "Berlin",
}


def parse_entry(line):
    """Parse: 'N. artist — title [FORMAT] (label)' → (artist_raw, title_raw, label_raw)"""
    line = re.sub(r"^\d+\.\s*", "", line.strip())
    if " — " not in line:
        return None
    artist_raw, rest = line.split(" — ", 1)
    label_raw = ""
    m = re.search(r"\(([^)]+)\)", rest)
    if m:
        label_raw = m.group(1).strip()
        rest = rest[: m.start()].strip()
    rest = re.sub(r"\s*\[(?:EP|ALBUM|LP|COMPILATION|REMIX|SINGLE)\]\s*", " ", rest).strip()
    rest = re.sub(r"\s+episode\s+.*", "", rest).strip()
    title_raw = rest
    return artist_raw.strip(), title_raw.strip(), label_raw


def get_scene(artist_raw, label_raw):
    a = artist_raw.lower().strip()
    if a in ARTIST_SCENES:
        return ARTIST_SCENES[a]
    l = label_raw.lower().replace(" ", "")
    for key, scene in LABEL_SCENES.items():
        if key in l:
            return scene
    return "Berlin"


def build_query(artist_raw, title_raw, label_raw):
    a = artist_raw.lower().strip()
    artist = ARTIST_MAP.get(a, artist_raw)
    title = split_smashed(title_raw)
    # Clean label for search hint
    label_hint = re.sub(r"records?$", "", label_raw).strip()
    label_hint = split_smashed(label_hint) if label_hint else ""
    # Skip "vs" or single-char titles
    if title.lower() in ("vs", "s", "a", "p", "r", "ep", "cd", "m", "h", "n"):
        return f"{artist} {label_hint}".strip()
    if not title or title.lower() == artist.lower():
        return f"{artist} {label_hint}".strip()
    # For very short queries, add label
    query = f"{artist} {title}"
    if len(query) < 15 and label_hint:
        query = f"{query} {label_hint}"
    return query.strip()


def search_discogs(query, artist_hint=""):
    """Search Discogs with genre=Electronic filter and result validation."""
    url = (
        f"https://api.discogs.com/database/search?q={quote(query)}"
        f"&type=release&genre=Electronic&per_page=10"
    )
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
            if not results:
                return None

            # Build keywords from query for validation
            query_words = set(w.lower() for w in query.split() if len(w) > 2)
            hint_words = set(w.lower() for w in artist_hint.split() if len(w) > 2)
            check_words = query_words | hint_words

            # Find best matching result (not just first)
            for r in results:
                tf = r.get("title", "")
                result_words = set(w.lower() for w in re.split(r"[\s\-\(\),]+", tf) if len(w) > 2)
                # Also check label
                rlabel = (r.get("label") or [""])[0].lower() if isinstance(r.get("label"), list) else ""
                result_words.update(w for w in rlabel.split() if len(w) > 2)

                # Require at least one meaningful word overlap
                overlap = check_words & result_words
                if not overlap and check_words:
                    continue

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

            # No validated match found
            return None
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

    # Parse entries from markdown
    entries = []
    seen_raw = set()
    with open(SOURCE_FILE) as f:
        for line in f:
            line = line.strip()
            if re.match(r"^\d+\.\s+", line):
                parsed = parse_entry(line)
                if parsed:
                    raw_key = f"{parsed[0]}|{parsed[1]}".lower()
                    if raw_key not in seen_raw:
                        seen_raw.add(raw_key)
                        entries.append(parsed)

    print(f"Parsed {len(entries)} unique entries from source")

    # Start from empty
    data = {
        "meta": {"total": 0, "labels": 0, "scenes": [], "year_range": [0, 0]},
        "geo": {
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
        },
        "releases": [],
    }

    existing_ids = set()
    existing_titles = set()
    added = 0
    failed = 0
    fail_list = []

    for i, (artist_raw, title_raw, label_raw) in enumerate(entries):
        query = build_query(artist_raw, title_raw, label_raw)
        scene = get_scene(artist_raw, label_raw)
        artist_clean = ARTIST_MAP.get(artist_raw.lower().strip(), artist_raw)

        result = search_discogs(query, artist_hint=artist_clean)
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

        image_path = ""
        if result["thumb"]:
            dest = IMAGES_DIR / f"{result['id']}.jpg"
            if dest.exists() or download_image(result["thumb"], dest):
                image_path = f"images/{result['id']}.jpg"

        color, colors = None, []
        full_img = SCRIPT_DIR.parent / image_path if image_path else None
        if full_img and full_img.exists():
            color, colors = extract_color(full_img)

        label_clean = re.sub(r"records?$", "", label_raw, flags=re.IGNORECASE).strip()

        release = {
            "id": result["id"],
            "title": result["title"],
            "artist": result["artist"],
            "year": result["year"],
            "catno": result["catno"],
            "thumb": result["thumb"],
            "format": result["format"],
            "label": label_clean or scene,
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

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(entries)}] +{added} added, {failed} failed")
            _save(data)
            print(f"  (checkpoint: {data['meta']['total']} releases)")

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

    print(f"\n{'='*60}")
    print(f"Archive rebuilt: {added} found from {len(entries)} unique entries")
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
