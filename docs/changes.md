# Changes — what the patcher edits, and why

Target: stock `index-DlFvHGAh.js` (Fluidd v1.30.5 as shipped on the
QIDI Q2, firmware 01.01.03.01+), SHA-256
`178b2e076d3a75716819ee13f9ea1f0c92e536546c8b2adafde8632f6723710c`.
Every edit is anchor-verified with an expected occurrence count; the
patcher stops if any anchor does not match exactly. Output carries
the stamp `window.__qidiQ2Fix="1.0.0"`.

## Panel component

1. **Stock `items` getter renamed** to `q2RawItems` (kept intact as
   the base list the override decorates).
2. **Members injected + DB load on creation**: `q2Info` (resolved
   identity per slot from `box_extras.boxes[].filament_info`, slot
   16 from `multi_color_controller.extra.filament_info`), an `items`
   override that overlays those identities on present slots,
   `q2Canon` (vendor alias canonicalization), `q2Db` / `q2LoadDb`
   (live firmware database via the `.qidi_filaments` link, built-in
   56/6 catalogue as fallback), `q2Protected` (current identity not
   representable in the database), `q2Edit` (single
   `UPDATE_FILAMENT_INFORMATION` write; refuses protected slots;
   vendor switches remap the filament inside the same write; an
   invalid color keeps the current one instead of inventing one).
3. **`vendorItems`**: database vendors; on a protected slot, only
   the slot's current vendor.
4. **`filamentItems`**: the selected vendor's database list; on a
   protected slot, only the current filament.
5–7. **`selectedVendor` / `selectedFilament` / `selectedColor`
   setters** route through `q2Edit` first and return when it handled
   the edit (new firmware); the stock path below them is preserved
   for legacy firmware states.
8. **Action commands**: `E_BOX/E_LOAD/E_UNLOAD slot=<n>` replaced
   by `EJECT_FILAMENT_CONTROL / LOAD_FILAMENT_CONTROL /
   UNLOAD_FILAMENT_CONTROL SLOT=<n>` — the commands this firmware
   registers.
9. **RFID**: `RFID_READ SLOT=slot<n>` replaced by
   `READ_RFID SLOT=<n>`.
10. **`buttonStatus`** (×2 occurrences): the `b_endstop_state` read
    falls back to `multi_color_controller.box` when `box_extras`
    doesn't publish it (this firmware) — repairs the Unload enable
    logic without touching its semantics.
11. **`isOperating`**: true when the multi-color controller reports
    a non-idle state, in addition to the stock
    `box_extras.box_button_state` source — the panel's Load /
    Unload / slot buttons bind to this getter, so the operating
    lock works again on this firmware.

## Store

12. **Status mutation merge**: for `multi_color_controller`,
    object-valued fields are shallow-merged on delta updates
    instead of replaced — the firmware publishes changed fields
    only, and replacement silently dropped sibling fields
    (e.g. one endstop of `box` while the other changed).

## Print-start dialog component

13. **Resolved-identity helpers injected** (`q2Info`, `q2Canon`,
    `q2FilaIndex` — the latter maps vendor + filament name to the
    enriched table's fila number).
14. **`isOkPrinter`**: the `e_endstop_state` / `b_endstop_state`
    reads fall back to `multi_color_controller.box`; no other
    change (stock semantics kept — no sensor substitution).
15. **`items` rebuilt from resolved identities**: label and color
    from the firmware's data, `filaIndex` through `q2FilaIndex`
    with the legacy `filament_slot` number as fallback — so the
    type-based auto-matching (`valueSlot`) works on real data.

## Filament table (`drop-in/officiall_filas_list.cfg`)

The design rule: Fluidd mirrors the printer. What the HMI offers
and reports is the truth; this table contains exactly the
printer's own filament database — 56 filaments, 6 vendors — with
the printer's current names, vendor forms and QF codes, and
nothing else. The 56 database entries (transcribed in Greg-LFT's
published fallback database, taken from a real printer's
`filament-*.json`) join 56/56 onto the QF catalogue (screen /
QIDI Studio data) once vendor aliases are accounted for (the
database says "Bambu", the Studio catalogue says "Bambu Lab";
Polymaker's database names are the short forms of its "PolyLite"
catalogue names).

Numbering preserves the stock table of a real Q2 (public config
dump, elliotboney/my_qidi_2): where a stock entry is one of the
56, it keeps its `fila` number and its stock temperatures, but is
**named as the printer names it today**. Six are documented
legacy renames (the stock file carries the pre-rename names):
PLA Metal → PLA Rapido Metal (QFA04), PLA-Wood → WOOD Rapido
(QFA16), ABS-Metal → ABS Rapido Metal (QFB55), ASA-CF →
ASA-CF20 Core (QFB51), PA-CF → PA6-CF (QFN05, by elimination in
the CF-polyamide family), PEBA → PEBA 95A (QFU03). 38 of the 56
sit at stock numbers; the remaining 18 are appended as
fila51–fila68.

The 12 stock sections that are **not** in the printer's database
(7 blank placeholders in QIDI's own file, plus 5 legacy names —
PLA Matte, Support For PLA, TPEE, PVA, TPU-AERO 64D — that the
current firmware does not know) are kept as unnamed placeholder
sections carrying only their stock temperatures and type, so
legacy numeric references cannot point at a missing entry. They
claim no name, no vendor and no QF code: Fluidd does not invent
filaments the printer does not have.
