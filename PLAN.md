# PLAN — Valdoria passport spread (light SDD)

1. Raster engine (`main.py` part 1): bytearray RGB canvas, pixel/rect/line/
   circle/ellipse/polygon fills, 5x7 bitmap font with scaling, rotated
   stamp layers with alpha compositing, 2x supersample + box downsample,
   minimal PNG encoder (zlib + struct, filter 0).
2. Document artwork (part 2): coat of arms, stylised portrait, Valdorian
   flag, guilloche arcs, MRZ with ICAO check digits.
3. Layout (part 3): two-page spread on a dark surface, data page left,
   visa/stamp page right, stamps + visa sticker + permit note; write
   `/output/entry.png`, chmod 0644.
4. Run locally, view the PNG, fix layout/text defects, re-run.
5. Revise the entrypoint in a later message (real line changes).
6. Commit, OCR delegate review, fix critical/high findings.
7. Export muse usage rows, bundle, check, submit, verify, write submit log.
