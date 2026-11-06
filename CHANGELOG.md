# Changelog

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
- Print-start mapping dialog rebuilt on the resolved identities
  with an enriched filament table (68 entries: the 50 stock entries
  kept at their numbers, catalogue IDs/vendors added, missing
  catalogue filaments appended as fila51–fila68).
- `multi_color_controller` partial status deltas are merged in the
  store instead of replacing sub-objects.
- Patcher verifies the stock bundle by SHA-256 and refuses any
  other input. Not yet smoke-tested on a real Q2.
