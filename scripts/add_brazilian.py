#!/usr/bin/env python3
"""
Add Brazilian techno releases to releases.json.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RELEASES_FILE = DATA_DIR / "releases.json"

BRAZILIAN_RELEASES = [
    {"artist": "Various", "title": "Maumau Alive", "label": "Fieldzz", "year": 1995, "format": "Vinyl"},
    {"artist": "DJ Mau Mau / Space Cake", "title": "Hell's Club By DJ Mau Mau", "label": "Fieldzz", "year": 1996, "format": "Vinyl"},
    {"artist": "Various", "title": "Hell's Club Vol. 1", "label": "Fieldzz", "year": 1996, "format": "Vinyl"},
    {"artist": "Various", "title": "Anderson Noise", "label": "Fieldzz", "year": 1996, "format": "Vinyl"},
    {"artist": "Currupyo, Friendtronik", "title": "Eletronic Music Brasil Disco 1", "label": "Mundo Mix Music", "year": 1997, "format": "Vinyl"},
    {"artist": "Dr. Alem / Bid", "title": "Eletronic Music Brasil Disco 2", "label": "Mundo Mix Music", "year": 1997, "format": "Vinyl"},
    {"artist": "Lopes e Dr. Alem / Loop B", "title": "Eletronic Music Brasil Disco 5", "label": "Mundo Mix Music", "year": 1997, "format": "Vinyl"},
    {"artist": "Anderson Noise / DJ Mau Mau", "title": "Eletronic Music Brasil Disco 7", "label": "Mundo Mix Music", "year": 1997, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Level 202", "label": "Self-Released", "year": 1997, "format": "Cassette"},
    {"artist": "Level 202", "title": "São Paulo EP", "label": "4x4 Recordings", "year": 1999, "format": "EP"},
    {"artist": "Level 202", "title": "Funk", "label": "Noise Music", "year": 1999, "format": "Vinyl"},
    {"artist": "Level 202", "title": "#1", "label": "Screw Records", "year": 2000, "format": "Vinyl"},
    {"artist": "Various", "title": "Noise Music 002", "label": "Noise Music", "year": 2000, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Outubro", "label": "Trama", "year": 2000, "format": "ALBUM"},
    {"artist": "Renato Cohen", "title": "Pontapé", "label": "Noise Music", "year": 2001, "format": "EP"},
    {"artist": "Renato Cohen & DJ Mau Mau", "title": "Two Bass", "label": "Noise Music", "year": 2001, "format": "Vinyl"},
    {"artist": "Various", "title": "Comp_01|02 Orgânico | Sintético", "label": "Muquifo Records", "year": 2001, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Pontapé", "label": "Intec Records", "year": 2002, "format": "EP"},
    {"artist": "Anderson Noise", "title": "Noise Music Compilation — 100% Mix", "label": "Noise Music", "year": 2002, "format": "ALBUM"},
    {"artist": "Erik Caramelo", "title": "Archive", "label": "Muquifo Records", "year": 2002, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Abelhas", "label": "Noise Music", "year": 2003, "format": "EP"},
    {"artist": "Renato Cohen", "title": "Spank / Step Back", "label": "Noise Music", "year": 2003, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Copacabana", "label": "Noise Music", "year": 2003, "format": "EP"},
    {"artist": "Anderson Noise", "title": "DJ World Series: Tech-House From Brazil", "label": "DJ Magazine", "year": 2003, "format": "ALBUM"},
    {"artist": "Anderson Noise", "title": "Playblack / Copacabana (Remixes)", "label": "Noise Music", "year": 2004, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Just Kick! (Carl Cox Mix)", "label": "Noise Music", "year": 2004, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Caipirinha / Rodizio", "label": "Noise Music", "year": 2005, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Noiser", "label": "Noise Music", "year": 2005, "format": "ALBUM"},
    {"artist": "Anderson Noise", "title": "Homem Cachorro / Rádio Noise", "label": "Noise Music", "year": 2005, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Nova / Vodu", "label": "Noise Music", "year": 2005, "format": "Vinyl"},
    {"artist": "Gui Boratto", "title": "Arquipélago", "label": "Kompakt", "year": 2005, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Seu Cabelo", "label": "Noise Music", "year": 2006, "format": "Vinyl"},
    {"artist": "Ken Ishii & Anderson Noise", "title": "Vale Tudo", "label": "Noise Music", "year": 2006, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "I Can Do That / Crazy Future", "label": "Noise Music", "year": 2006, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Guimba / Noia", "label": "Noise Music", "year": 2007, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Detroit To Torino", "label": "Noise Music", "year": 2007, "format": "Vinyl"},
    {"artist": "Gui Boratto", "title": "Chromophobia", "label": "Kompakt", "year": 2007, "format": "ALBUM"},
    {"artist": "Anderson Noise", "title": "Londrina", "label": "Harthouse Digital", "year": 2008, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Shibuya", "label": "Harthouse Digital", "year": 2008, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Mágica / Power", "label": "Noise Music", "year": 2008, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Deputamadre", "label": "Sleaze Records", "year": 2009, "format": "Vinyl"},
    {"artist": "Anderson Noise", "title": "Parana", "label": "Sleaze Records", "year": 2009, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Sixteen Billion Drum Kicks", "label": "Sino / ST2", "year": 2009, "format": "Vinyl"},
    {"artist": "Teto Preto", "title": "Gasolina", "label": "Mamba Rec", "year": 2016, "format": "Vinyl"},
    {"artist": "EXZ", "title": "Serra", "label": "Mamba Rec", "year": 2016, "format": "Vinyl"},
    {"artist": "Entropia-Entalpia", "title": "Demolição", "label": "Mamba Rec", "year": 2017, "format": "Vinyl"},
    {"artist": "Teto Preto", "title": "Bate Mais", "label": "Mamba Rec", "year": 2018, "format": "Vinyl"},
    {"artist": "Teto Preto", "title": "Pedra Preta", "label": "Mamba Rec", "year": 2018, "format": "ALBUM"},
    {"artist": "L_cio feat. Massumi", "title": "Contaminasssão", "label": "Mamba Rec", "year": 2018, "format": "Vinyl"},
    {"artist": "Martinelli", "title": "Sem Sono", "label": "Mamba Rec", "year": 2019, "format": "Vinyl"},
    {"artist": "Valesuchi", "title": "Tragicomic", "label": "Mamba Rec", "year": 2019, "format": "Vinyl"},
    {"artist": "Trypas Corassão", "title": "Beleza Como Vingança", "label": "Mamba Rec", "year": 2022, "format": "ALBUM"},
    {"artist": "BADSISTA", "title": "Na Madruga", "label": "Beatwise Recordings", "year": 2015, "format": "Vinyl"},
    {"artist": "BADSISTA", "title": "Gueto Elegance", "label": "Self-Released", "year": 2021, "format": "Vinyl"},
    {"artist": "BADSISTA", "title": "ZL Club Music Pt. II", "label": "Self-Released", "year": 2021, "format": "Vinyl"},
    {"artist": "BADSISTA", "title": "Gueto Club", "label": "Tra Tra Trax", "year": 2023, "format": "Vinyl"},
    {"artist": "Lyzza", "title": "Mosquito", "label": "Big Dada / Ninja Tune", "year": 2022, "format": "Vinyl"},
    {"artist": "Lyzza", "title": "Powerplay", "label": "Club Lyzza", "year": 2022, "format": "Vinyl"},
    {"artist": "Amanda Mussi", "title": "Keyboard Cats EP", "label": "Massa Records", "year": 2019, "format": "EP"},
    {"artist": "Amanda Mussi", "title": "Keyboard Cats Remixes", "label": "Massa Records", "year": 2020, "format": "Vinyl"},
    {"artist": "The Lady Machine / Amanda Mussi", "title": "Unterwegs II", "label": "Unterwegs Records", "year": 2019, "format": "Vinyl"},
    {"artist": "L_cio", "title": "Plants", "label": "D.O.C. / Kompakt", "year": 2023, "format": "ALBUM"},
    {"artist": "L_cio & Ney Faustini", "title": "Free Your Mind", "label": "Cardume Records", "year": 2025, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Party Jam", "label": "Gop Tun", "year": 2018, "format": "Vinyl"},
    {"artist": "Wehbba", "title": "Straight Lines and Sharp Corners", "label": "Drumcode", "year": 2020, "format": "ALBUM"},
    {"artist": "ANNA", "title": "Forever Ravers", "label": "Kompakt", "year": 2020, "format": "Vinyl"},
    {"artist": "Vinicius Honorio", "title": "Through The Darkness", "label": "Drumcode", "year": 2019, "format": "Vinyl"},
    {"artist": "Vinicius Honorio", "title": "Loops Vol. 01", "label": "Liberta Records", "year": 2018, "format": "Vinyl"},
    {"artist": "Vinicius Honorio", "title": "Loops Vol. 02", "label": "Liberta Records", "year": 2019, "format": "Vinyl"},
    {"artist": "Vinicius Honorio", "title": "RMX Part One", "label": "Liberta Records", "year": 2019, "format": "Vinyl"},
    {"artist": "The Lady Machine", "title": "Magnify EP", "label": "Mote-Evolver", "year": 2019, "format": "EP"},
    {"artist": "Renato Cohen", "title": "Proibidão", "label": "Massa Records", "year": 2019, "format": "Vinyl"},
    {"artist": "Renato Cohen", "title": "Força EP", "label": "Suara", "year": 2018, "format": "EP"},
    {"artist": "Renato Cohen", "title": "Roaring EP", "label": "Skylax", "year": 2025, "format": "EP"},
    {"artist": "Various", "title": "20 Years of Noise Music", "label": "Noise Music", "year": 2019, "format": "ALBUM"},
]


def main():
    with open(RELEASES_FILE) as f:
        data = json.load(f)

    # Get next ID
    max_id = max(r["id"] for r in data["releases"])
    next_id = max_id + 1

    # Add Brazil to geo if missing
    if "Brazil" not in data.get("geo", {}):
        data["geo"]["Brazil"] = [-23.5505, -46.6333]  # São Paulo

    added = 0
    for entry in BRAZILIAN_RELEASES:
        release = {
            "id": next_id,
            "title": entry["title"],
            "artist": entry["artist"],
            "year": entry["year"],
            "catno": "",
            "thumb": "",
            "format": entry["format"],
            "label": entry["label"],
            "label_id": 0,
            "scene": "Brazil",
            "country": "Brazil",
            "discogs_url": "",
            "image": "",
            "color": "#1a1a1a",
            "colors": ["#1a1a1a", "#0a0a0a", "#2a2a2a"],
            "hsl": {"hex": "#1a1a1a", "h": 0, "s": 0, "l": 10.2},
            "sort_hue": -0.9,
            "palette": [{"hex": "#1a1a1a", "h": 0, "s": 0, "l": 10.2}],
        }
        data["releases"].append(release)
        next_id += 1
        added += 1

    # Update meta
    years = [r["year"] for r in data["releases"] if r.get("year")]
    data["meta"]["total"] = len(data["releases"])
    data["meta"]["labels"] = len(set(r["label"] for r in data["releases"]))
    data["meta"]["scenes"] = sorted(set(r["scene"] for r in data["releases"]))
    data["meta"]["year_range"] = [min(years), max(years)] if years else [0, 0]

    with open(RELEASES_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Added {added} Brazilian releases (IDs {max_id+1}–{next_id-1})")
    print(f"Total releases: {data['meta']['total']}")
    print(f"Scenes: {data['meta']['scenes']}")


if __name__ == "__main__":
    main()
