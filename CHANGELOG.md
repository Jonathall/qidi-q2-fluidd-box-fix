# Changelog

## V1.1.1 — 2026-11-25

Filament table only; bundles unchanged. The five `[colordict]`
entries changed in V1.0.1 (#4, #7, #13, #17, #20) came from the
Plus 5 fix's correction, verified against a Plus 5 printer. On
the Q2, the printer's own stock table — the firmware
01.01.03.03/.04 table and a real Q2's table agree byte for byte
on `[colordict]` — carries the original values, so the table
now follows the Q2 stock palette again (#4 `#5CF30E` →
`#5CF30F`, #7 `#FF98FE` → `#FE98FE`, #13 `#CADF4B` → `#CADE4B`,
#17 `#FF7174` → `#FE717A`, #20 `#898F8B` → `#898F9B`).
`[colordict]` only feeds the colour picker's swatches; filament
identities, temperatures and assignments are unchanged. Both
drop-in folders ship the same corrected table. Filament table
SHA-256:
`1b0331a6c0efb5749053d3afdc421bfafb954a45ae0530ff06abd22d09b19e5b`

## V1.1.0 — 2026-11-24

Port to firmware **01.01.03.04** (released 2026-11-23). That
firmware ships a rebuilt Fluidd bundle (`index-nyEzQB9T.js`,
byte-identical to the bundle on the Plus 5 firmware 01.01.02.02)
in which the Box dashboard card and the print-time filament
assignment dialog are no longer part of the UI (QIDI's changelog:
"Hid the filament editing page in Fluidd"). V1.0.2's patcher
refuses the new bundle by hash, and the firmware update replaces
a patched panel with the new stock one.

- New patcher `patcher/qidi_q2_fluidd_fix_01010304.py` and new
  drop-in folder `drop-in-01010304/` (patched bundle + the same
  filament table as V1.0.2). For firmware 01.01.03.01–.03 nothing
  changes — use V1.0.2 as before (the .03 bundle is
  byte-identical to the V1.0.2 reference bundle).
- All 15 fix steps ported. Two anchors needed re-anchoring on the
  new build, both pure renames: step 8 (the socket alias changed
  from `I.` to `R.` throughout the bundle; the injected `q2Edit`
  member is re-aliased the same way) and step 15 (local variable
  renames in the dialog's `items` getter). `q2San` and the deep
  merge from V1.0.2 are carried over unchanged.
- 10 additional restoration steps: the Box card's render function
  and dashboard registration are restored, the
  FileSystemSelectLineDialog's render function and its three
  component registrations are restored, and the dialog's four
  call branches in the file-system handlers are restored — all on
  top of the .04 code, so the .04 behaviour without a Box (direct
  print) is preserved as the fallback branch.
- Validation: `node --check` passes; undoing all 25 steps
  reproduces the stock .04 bundle byte for byte; regeneration
  from clean stock is byte-identical; the patcher refuses the
  .01–.03 bundle and an already-patched bundle; marker counts
  match the V1.0.2 patched bundle exactly (BoxCard registration
  1, dialog registrations 3, `getCanPrint` 5).
- Note for upgraders: the .04 update replaces
  `officiall_filas_list.cfg` with the stock table (the file is
  not in the update's keep list) — re-copy the filament table
  from `drop-in-01010304/` after updating.
- Known limitation: firmware .04 renamed six filaments in the
  printer's catalogue (ABS-GF → ABS-GF25, ABS Rapido Metal → ABS
  Metal Rapido, ABS Odorless → Odorless ABS, PLA Rapido Matte →
  PLA Matte Rapido, PLA Rapido Metal → PLA Metal Rapido, WOOD
  Rapido → PLA Wood Rapido). The panel reads the printer's live
  filament database and is unaffected; the dialog's fallback name
  map still carries the pre-.04 names, so a renamed filament
  falls back to the firmware's slot index in the dialog until
  the map is refreshed from a real .04 machine.
- **Not yet tested on a real Q2 — pre-release.** Still open on a
  physical printer: Box card and slot tiles, edit ↔ screen sync
  (including a renamed filament), load/unload under the
  recompiled Box modules and the new BOX485 / BUFFER firmwares,
  the assignment dialog from its three entry points, the .04
  nozzle validation, and a full print with a filament change.

Patched bundle SHA-256:
`03307e39ddb5edb789eda3ba12de8167eef0e9a79e3d0f6f250d789c9aa09184`
Stock .04 bundle SHA-256:
`dfd8fe36257c8d2ef76b95943cf338672c6ddebda6e3f79ade3ccfd194b3e7d6`

## V1.0.2 — 2026-11-24

- Security (issue #4): `q2Edit` interpolated the vendor and filament
  names into the single-quoted parameters of
  `UPDATE_FILAMENT_INFORMATION` verbatim. A name containing a quote,
  a backslash or a line break — for example from a crafted filament
  database — could break out of the quoted parameter and inject
  additional gcode into the script sent to the printer. The names
  are now stripped of those characters before interpolation
  (`q2San`); no name in the printer's own database contains them.
- The `multi_color_controller` merge is now a deep merge
  (PR #5, contributed by RussianPenguin): a partial status delta
  previously replaced the whole sub-object, dropping fields such
  as `vendor_str` and leaving the panel state inconsistent with
  the printer until a page reload.

Patched bundle SHA-256:
`9f1247107231b161a51df9ab3650181c5c6f3ee67ed841bfc9c74d048f9415ec`

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
