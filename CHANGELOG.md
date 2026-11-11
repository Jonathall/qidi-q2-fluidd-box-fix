# Changelog

## V1.0.1 — 2026-11-10

Filament table only; bundle unchanged. Five `[colordict]` entries
copied verbatim from the stock table did not match the hex codes
the printer firmware itself writes when a color is set on the
printer screen (#4 `#5CF30F` → `#5CF30E`, #7 `#FE98FE` → `#FF98FE`,
#13 `#CADE4B` → `#CADF4B`, #17 `#FE717A` → `#FF7174`,
#20 `#898F9B` → `#898F8B`); the panel resolves a screen-set color
by exact hex match against `[colordict]`, so those five colors
never appeared in Fluidd. Same correction as the Plus 5 fix V9.3
(contributed by mayrthom via a fork, entry #20 verified against a
real printer). Filament table SHA-256:
`8df162da18b247d2ddaceebd5a5f2fc8c6e019042a2170a072753b847c343a93`

## V1.0.0 — 2026-11-06 (bench-tested beta)

Initial release for the QIDI Q2 on firmware 01.01.03.01+
(Fluidd v1.30.5 bundle `index-DlFvHGAh.js`).

- Panel slot identities read from the firmware's resolved data
  (`box_extras.boxes[].filament_info`, `multi_color_controller.extra`),
  live in both directions with the printer screen.
- Vendor/filament lists from the printer's own filament database
  (read-only symlink), built-in 56-filament / 6-vendor catalogue as
  fallback.
- Edits sent as a single `UPDATE_FILAMENT_INFORMATION`; slots whose
  identity is not representable in the database are protected — no
  edit is emitted for them, so a partial edit can never silently
  rewrite a spool's vendor or filament.
- Load / Unload / Eject / RFID send the current firmware commands;
  the panel operating lock is fed from the multi-color controller
  state; Unload enable logic reads the endstops where this
  firmware publishes them.
- Print-start mapping dialog rebuilt on the resolved identities,
  with a filament table that mirrors the printer's own database:
  the 56 database filaments with the printer's names and QF codes
  (stock numbering preserved, the 18 the stock table lacks appended
  as fila51–fila68; stock sections that are not in the printer's
  database stay as unnamed placeholders).
- `multi_color_controller` partial status deltas are merged in the
  store instead of replacing sub-objects.
- Patcher verifies the stock bundle by SHA-256 and refuses any
  other input. Not yet smoke-tested on a real Q2.
