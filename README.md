# Fluidd Box / Filament Panel Fix — QIDI Q2

A patch for the Fluidd **Control Box** panel (and the print-start
slot-mapping dialog) on the **QIDI Q2**, for firmware **01.01.03.01
and later** (the line that moved the multi-color subsystem to its
current data structure; QIDI's own changelog for 01.01.03.01 says
filament management through Fluidd is not supported — this patch
makes it work again, properly).

> **Status: bench-tested beta.** Developed and tested on a simulated
> bench reproducing the Q2 firmware's published data (real
> Klipper/Moonraker, simulated Box extras, two-way Fluidd ↔ screen
> tests). **Not yet smoke-tested on a real Q2** — reports from owners
> are welcome, good or bad. GPL-3.0.

> ---
> ## ⚠️ READ FIRST — Where the files go
>
> The install replaces exactly **TWO files**, at these exact
> locations, with these exact names:
>
> - ✅ **The patched Fluidd bundle goes here, and only here:**
>   `/home/qidi/fluidd/assets/index-DlFvHGAh.js`
> - ✅ **The filament table goes here, and only here:**
>   `/home/qidi/printer_data/config/officiall_filas_list.cfg`
>
> Keep the original names (a browser download may append ` (1)`,
> remove it). Do not create subfolders and do not leave the old file
> next to the new one under another name.
>
> - 🔄 **Last step, do not skip it: hard-refresh Fluidd** in your
>   browser (**Ctrl+F5**, or **Cmd+Shift+R** on Mac). Fluidd's
>   service worker can keep serving the old bundle from your
>   browser's cache — a perfectly correct install can look
>   completely unchanged until you hard-refresh.
>
> Two files, two exact locations, exact names. If a step below seems
> to say otherwise, this box wins.
> ---

## What is broken on the stock firmware

Since 01.01.03.01 the printer screen and QIDI Studio work with
resolved filament identities (profile IDs such as `QFA00`, vendor
names, hex colors) published by the firmware, while the Fluidd build
shipped on the printer still reads and writes the legacy numeric
world (the 50-entry `officiall_filas_list.cfg` and `save_variables`
indices) and sends commands the firmware no longer registers. In
practice: the panel shows wrong or empty slot identities, edits from
Fluidd don't stick or desynchronize the screen, Load / Unload / RFID
buttons send dead commands, and the print-start mapping dialog works
from stale numbers.

## What this patch does

1. **Truthful display.** Slot identities are read from
   `box_extras.boxes[].filament_info`, and the external spool from
   `multi_color_controller.extra.filament_info` — the same resolved
   data the screen shows, updated live in both directions.
2. **Live firmware database.** Vendor and filament lists come from
   the printer's own filament database
   (`QIDI_Client/resource/filament_config/filament-<nozzle>.json`,
   exposed to Fluidd through a read-only symlink, see Install), with
   a built-in 56-filament / 6-vendor catalogue as fallback.
3. **One native write.** Edits are sent as a single
   `UPDATE_FILAMENT_INFORMATION` — the command QIDI Studio uses —
   with vendor, filament and color consistent in the same write.
4. **No silent rewrites.** If a slot's current identity is not
   representable in the database (for example set by the screen or
   RFID with a filament the database doesn't list), the panel shows
   it, restricts its edit lists to that identity, and **refuses to
   emit any edit for it** — a color-only change can never quietly
   turn your spool into a different brand and product.
5. **Working controls, locked while busy.** Load / Unload / Eject /
   RFID send the current commands (`LOAD_FILAMENT_CONTROL`,
   `UNLOAD_FILAMENT_CONTROL`, `EJECT_FILAMENT_CONTROL`, `READ_RFID`),
   and the panel's own operating lock — dead on this firmware
   because `box_extras.box_button_state` is no longer published —
   is fed again from the multi-color controller's state, so buttons
   stay disabled while a Box operation runs.
6. **Print-start dialog reads the truth too.** The slot-mapping
   dialog's slots are built from the same resolved identities, with
   indices into the filament table below, instead of the
   legacy `save_variables` numbers. Its confirmation write is left
   exactly as stock (the effective print-start mapping remains
   driven by the firmware / QIDI Studio).
7. **Filament table that mirrors the printer.** The bundled
   `officiall_filas_list.cfg` contains exactly the printer's own
   filament database — the 56 filaments / 6 vendors the HMI
   offers, with the printer's current names and QF codes, nothing
   invented on the Fluidd side. Stock entry numbers are preserved
   (the 18 database filaments the stock table lacks are appended
   as fila51–fila68); stock sections that are not in the printer's
   database stay as unnamed placeholders so legacy numeric
   references cannot dangle.
8. **Partial updates merged.** `multi_color_controller` status
   deltas (the firmware publishes changed fields only) are merged
   into the store instead of replacing whole sub-objects, so a
   one-field update no longer blanks its siblings (endstops
   included — the print dialog's check reads them with a fallback
   to `multi_color_controller.box`, where this firmware keeps them).

The patcher verifies the stock bundle by SHA-256 and refuses
anything else, including an already-patched bundle.

## Connecting to the printer

You need to copy two files to the printer. Any SFTP client works
(WinSCP, Cyberduck, FileZilla…), or SSH + `scp`.

1. Find the printer's IP address on its touchscreen (network /
   Wi-Fi settings).
2. Connect with SFTP (port **22**): user **`mks`**, default
   password **`makerbase`** (unless you changed it).
   The first connection shows a host-key prompt — accept it.
3. Before replacing anything, rename the two original files on the
   printer to `index-DlFvHGAh.js.stock-backup` and
   `officiall_filas_list.cfg.stock-backup`. That backup is your
   rollback.
4. Upload the two files from this repo's `drop-in/` folder to the
   exact locations in the READ FIRST box above, keeping the exact
   names (remove any ` (1)` the browser added).
5. Optional but recommended, for the live filament database
   (over SSH):
   `ln -s /home/qidi/QIDI_Client/resource/filament_config ~/printer_data/config/.qidi_filaments`
   Without it, the patch uses its built-in fallback catalogue.
6. Hard-refresh Fluidd (**Ctrl+F5**).

## Install

**Path A — drop-in (recommended).** Follow "Connecting to the
printer" above: back up, upload the two `drop-in/` files, done.

**Path B — patch your own bundle.** Copy your printer's stock
`/home/qidi/fluidd/assets/index-DlFvHGAh.js` to your computer, run

```
python3 patcher/qidi_q2_fluidd_fix.py index-DlFvHGAh.js index-DlFvHGAh.patched.js
```

The patcher checks the SHA-256 first and stops without writing if
the file is not the exact stock bundle. Upload the result under the
original name, plus the `drop-in/` filament table.

## Verify the install

- **Hash the file you actually installed:** download
  `/home/qidi/fluidd/assets/index-DlFvHGAh.js` back from the printer
  and hash it — it must match the patched hash below, not the stock
  one.
- **Or check the stamp:** open Fluidd, press F12 (developer
  console), and type `window.__qidiQ2Fix` — it must answer
  `"1.0.0"`. If it answers `undefined`, your browser is still
  serving the old bundle: hard-refresh (Ctrl+F5), or clear the
  site's data and reload.

| File | SHA-256 |
|---|---|
| stock bundle | `178b2e076d3a75716819ee13f9ea1f0c92e536546c8b2adafde8632f6723710c` |
| patched bundle | `f353ed201b84397dfa1eb19a1488e73b3efff5c1c2658e17bbb6877b72390821` |
| filament table | `1b0331a6c0efb5749053d3afdc421bfafb954a45ae0530ff06abd22d09b19e5b` |

(MD5 of the stock bundle, as shipped on the printer:
`b9bc4faaf367d0603d92d7217476c57a` — note this is the same Fluidd
build QIDI ships on the Plus 5; the patches are **not**
interchangeable, each model has its own firmware data contract and
its own filament table numbering.)

## Uninstall / rollback

Restore the two `.stock-backup` files to their original names and
locations, remove `~/printer_data/config/.qidi_filaments` if you
created it, and hard-refresh Fluidd. Nothing else on the printer is
modified by this fix.

## Differences from Greg-LFT's Q2 patch

Another Q2 patch exists (Greg-LFT/Qidi-Q2-Fluidd-widget-box-repair,
GPL-3.0, hardware-tested by its author) and gets the basics right.
This fix differs on points that were reproduced on the bench
(`docs/testing.md`):

- Editing a slot whose identity is outside the database: his
  patcher-side logic coerces the write to the database (a color-only
  edit re-emitted the slot as a different vendor and filament);
  this fix emits nothing and protects the slot.
- His patch leaves the panel's operating lock dead (buttons stay
  enabled during Box operations); this fix feeds the lock from the
  multi-color controller state.
- His patch does not touch the print-start mapping dialog (his
  README lists it as a known limitation); this fix rebuilds the
  dialog's slot data from the resolved identities.
- His patch's print-check substitutes the filament switch sensor
  for a missing endstop state; this fix reads the endstops where
  this firmware actually publishes them and keeps the stock
  semantics otherwise.

## Known limitations

- **Beta until a real Q2 smoke test.** The bench reproduces the
  firmware's published contract; only a physical printer proves the
  last mile (notably whether the firmware publishes an operation
  state for the panel lock — the lock engages when it is present
  and falls back to stock behaviour when it is not).
- A resolved identity may carry the vendor form « Bambu Lab »
  where the printer's database says « Bambu »; the patch
  canonicalizes known aliases before comparing and writes the
  database form.
- A QIDI firmware update will replace Fluidd and the table; reapply
  the fix afterwards (the patcher will refuse a changed bundle
  rather than guess).

## License

GPL-3.0 — same license as Fluidd and the QIDI firmware components
it patches. Filament catalogue data is QIDI's own (printer screen /
QIDI Studio / the on-printer database).
