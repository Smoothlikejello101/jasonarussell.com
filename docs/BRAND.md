# Brand

## JR monogram
Jason's original Gabriola-based monogram, traced to vector and refined (November 2026):
- The J's stem doubles as the R's stem. The R's two strokes taper to points and stop about 1.6px (at 259px scale) short of the J, like a pen lifting ("pen lift" joins).
- Weight is slightly heavier than the original. Leans about 6°.

| File | Use |
| --- | --- |
| `public/brand/jr-mark.svg` | Light backgrounds (black J, goldenrod R) |
| `public/brand/jr-mark-on-dark.svg` | Dark backgrounds (paper-white J, goldenrod R) |
| `public/brand/jr-mark-black.svg` / `jr-mark-white.svg` | One-color uses (stamps, embossing). In one color the mark reads more like an R, so prefer two-tone. |
| `public/favicon.svg` | Browser tab; switches the J to light in dark mode |
| `public/apple-touch-icon.png` | Phone home-screen icon |
| `public/watermark.png` | Photo watermark: white J, gold R over "Jason A Russell.com" (EB Garamond Italic, half spaces around the A), soft shadow |

## Colors
- Black `#141414`, goldenrod `#E2AE0E` (the mark)
- Site: paper `#EDEFEA`, ink `#1E2A26`, violet `#5E3F86`, leaf `#3D5832`

## Regenerating
`tools/logo/` has the original artwork and the Python scripts used to trace and refine it (`joins3.py` → `build()` with default arguments is the final mark). Requires `potracer`, `numpy`, `Pillow`, `fontTools`.
