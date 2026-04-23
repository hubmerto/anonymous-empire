# Legal pages — change log

This file is the authoritative history of legal text changes for
[anonymousempire.art](https://anonymousempire.art/). Every entry below
corresponds to a commit in this repository, so the commit date and
diff constitute independent proof of when a clause was in effect.

---

## 2026-04-23 — Datenschutz v1.1

**Datenschutzerklärung**
- Removed Google Fonts (fonts.googleapis.com, fonts.gstatic.com) disclosure — the CDN is no longer loaded. Site now uses system-installed fonts (Arial Black, Helvetica Neue fallback; Megatron Sans self-hosted for brand).
- Removed jsDelivr disclosure — no longer loaded.
- Only remaining third-party network resources: unpkg (Leaflet map library) and OpenStreetMap tile server.
- GDPR posture: eliminated the US data transfer for font delivery, closing the LG München I (2022) risk vector.

## 2026-04-22 — Impressum v1.1 / Datenschutz v1.0

**Impressum**
- Operator details filled (Humberto dos Anjos Gesser Neves, Steinstrasse 10, 10119 Berlin).
- Strengthened third-party content disclaimer: explicit non-ownership, no commercial interest in record-cover imagery.
- Stated legal basis for reproduction (§51 UrhG Zitatrecht, Art. 5(3) GG freedom of art/scholarship, non-commercial archival purpose, low-resolution editorial framing).
- Added **notice-and-takedown clause**: rights holders may request removal by email with URL + proof of ownership; response within 72 hours; no legal action required.
- Added non-endorsement statement.
- Dispute-resolution boilerplate removed (site is non-commercial, not a consumer-facing business).

**Datenschutzerklärung**
- Initial publication.
- Discloses: GitHub Pages hosting (USA), Google Fonts CDN, jsDelivr / unpkg CDNs, OpenStreetMap tile server.
- Confirms: **no cookies**, no analytics, no tracking, no forms, no advertising identifiers.
- `localStorage` used only for remembering the library view preference; stays on user device.
- GDPR rights and supervisory-authority address (Berliner Beauftragte für Datenschutz) included.

## 2026-04-22 — v1.0 (initial drafts)

- Impressum and Datenschutz templates first published with placeholder operator details.
- Footer links added to `index.html` and `library.html`.

---

## How to use this log

If ever contested (e.g. via an Abmahnung), the relevant commit in
`git log -- impressum.html datenschutz.html` shows the exact text in
effect on any given date, signed by the commit timestamp.
