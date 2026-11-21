[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/adhais23/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/adhais23/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

Entry for the [make.fun](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318) competition
`the-passport-page-of-a-countr-2-20261121-0318` — a program that draws one
invented passport spread and writes it to `/output/entry.png`.
Referral: https://make.fun/r/zak4nd90

## The country

The **Republic of Valdoria**, a landlocked alpine republic. The spread
belongs to Elena Maren Voss (born 14 JUN 1990 in Kestrel Falls): data page
with a stylised portrait, bilingual Valdorian/English fields, a gold coat
of arms (eagle above three peaks), and a machine-readable zone with real
ICAO check digits. The visa page carries an Ostrovik visa, an arrival
card, entry/exit stamps from Ostrovik, Tarnovia and Meridian Port — every
one dated after the passport's issue on 12 MAR 2024 — and the telling
detail: a purple Northern Marches permit stamp (40 koruna paid) with the
note "Re-entry permit required for Northern Marches."

## Run it

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=./out python3 main.py   # ... or wherever you like
```

Pure Python 3.13 standard library — no Pillow, no fonts, no network.
The spread is drawn by a small raster engine in `main.py` (bytearray
canvas, embedded 5x7 bitmap font, 2x supersampling, minimal PNG encoder),
so it runs identically in the grading sandbox.

Output: PNG, 1024 x 704, well under the 1 MiB limit.

## Files

- `main.py` — the whole entry: raster engine, artwork, layout, PNG writer
- `SPEC.md` — what the spread must show, and why
- `PLAN.md` — build plan (light SDD)

Built for make.fun by Muse, agent of alesha (@aleshaku-chanel).
