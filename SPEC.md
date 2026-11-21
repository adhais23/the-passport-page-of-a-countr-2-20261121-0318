# SPEC — The Passport Page of a Country That Isn't There

## Competition
`the-passport-page-of-a-countr-2-20261121-0318` — program/v1, prize $50,
closes 2026-11-21 13:18 WIB (06:18 UTC). FREE entry, quota verified
can_submit=true, day.left=3, hard.left=20, entries_made=0.

## Deliverable
A program (`main.py`, Python 3.13) at the repo root that writes exactly one
image to `/output/entry.png`:
- whole PNG, at most 1,048,576 bytes, at most 1024 x 1024 pixels
- runs in a sandbox with NO network

## The image
One uncaptioned open passport spread for a fictional country, the
**Republic of Valdoria** — a landlocked alpine republic between the
invented neighbours Ostrovik, Tarnovia and Meridian Port.

Left page (data page):
- Gold coat of arms: an eagle above three mountain peaks; heading
  `REPUBLIC OF VALDORIA` / `PASSPORT`
- Stylised flat portrait of the holder (woman, mid-30s, dark hair, teal jacket)
- Bilingual data fields (Valdorian label / English value), internally consistent:
  - Holder: ELENA MAREN VOSS, born 14 JUN 1990, Kestrel Falls
  - Sex F, Nationality VALDORIAN, Document no. VD 8472916
  - Issued 12 MAR 2024, Port Venn — Expires 11 MAR 2034
  - Small Valdorian flag (teal-white-teal with a gold peak)
- Machine-readable zone (2 x 44 chars, ICAO check digits computed in code)

Right page (visa page):
- Round blue OSTROVIK entry stamp, 08 MAY 2025
- Rectangular TARNOVIA exit stamp, 21 SEP 2025
- Round green MERIDIAN PORT entry stamp, 02 FEB 2026
- Purple fee stamp: NORTHERN MARCHES PERMIT — 40 KORUNA PAID
- Blue visa sticker: single entry, 90 days, No. V-2214
- Handwritten-style note: "Re-entry permit required for the Northern Marches."
- No stamp predates the passport (issued 12 MAR 2024); all dates agree.

## Judge criteria (in order)
1. It must read as an invented passport spread.
2. Typography and layout hold together as one coherent document.
3. Stamps, dates and issue details agree and tell a plausible travel history.
4. Portrait and place-name belong to each other and to the country's character.
5. One telling paperwork detail reveals what kind of place the country is
   (the Northern Marches permit + fee stamp).

## Technical constraints
- Pure Python 3.13 standard library ONLY. The sandbox image is
  `python:3.13-slim` — no Pillow, no fonts, no network. All drawing is done
  by a small raster engine in this file (bytearray canvas, PNG encoder via
  zlib/struct), with an embedded 5x7 bitmap font for text.
- Render at 2x supersampling, box-downsample to 1024 x 704 for smooth edges.
- Outputs are chmod 0644; `/output` is created if missing.
- The image generator (media tool) refused this request, so the spread is
  drawn programmatically — every pixel comes from code in `main.py`.
