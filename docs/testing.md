# Testing

No QIDI Q2 was available in the workshop, so — as with the Plus 4
fix — the patch was developed against a **simulated bench** that
reproduces the firmware's side of the contract, and is released as
**beta** until a Q2 owner smoke-tests it.

## The bench

- Real Klipper + Moonraker (the same open-source builds used for
  the Plus 4 bench), MCU simulated (simulavr), printer driven
  through the standard Moonraker API.
- Simulated extras implementing the Q2 firmware 01.01.03.01+
  contract as extracted from primary sources (QIDI's changelog,
  the on-printer database format and command set as documented by
  the hardware-tested community patch, a real Q2's config dump and
  the decompiled `box_extras` module analysis):
  `box_extras.boxes[].filament_info` resolved identities,
  `multi_color_controller.extra` / `.box` (endstops, partial
  deltas), `box_stepper slot<N>.runout_button` presence,
  `UPDATE_FILAMENT_INFORMATION`, `LOAD/UNLOAD/EJECT_FILAMENT_CONTROL`,
  `READ_RFID`, an operation state on the multi-color controller.
- The three Fluidd builds (stock, the other community patch
  applied with its own patcher, this fix) served side by side and
  driven in a headless browser through the real panels; every
  command a panel emitted was captured from the simulated
  firmware's command log.

## Reproduced failures of the other patch (bench evidence)

- Color-only edit of a slot whose identity is outside the database
  (set screen-side to eSun / PETG Pro) emitted
  `UPDATE_FILAMENT_INFORMATION … VENDOR=QIDI FILAMENT=PETG Basic` —
  brand and product silently rewritten.
- During a Box operation, all panel buttons stayed enabled.
- The print-start dialog component is untouched by that patch and
  reads only legacy `save_variables` numbers (its author lists this
  as a known limitation).

## This fix — results

- Display: all slots + external spool show resolved identities,
  live in both directions (screen-side change appears in Fluidd
  without reload, and vice versa).
- Color-only edit of a representable slot: exactly one
  `UPDATE_FILAMENT_INFORMATION`, vendor and filament preserved
  verbatim.
- Protected slot: edit lists reduced to the current identity;
  color edit emitted **no command at all**.
- Vendor switch: one coherent write with the remapped filament.
- Unload during an operation: command emitted once; while the
  operation ran, every slot and action button in the panel was
  disabled (`isOperating` true).
- Print-start dialog data (unit evaluation of the patched getter
  with the same helpers proven live in the panel): catalogue slots
  map to their filament-table indices (QIDI PLA Basic → fila7,
  PETG Basic → fila39, Overture ABS → fila66), an out-of-catalogue
  slot keeps its legacy index as fallback, colors are the resolved
  hex values.
- Patcher: refuses the patched bundle itself and any other
  non-stock input by SHA-256; output passes a JS syntax check.

## What the bench cannot prove

Behaviour of the real `.so` firmware modules (exact published
field set — in particular an operation-state field for the panel
lock, which the patch uses only when present), the real database
file's full contents per nozzle size, and the dialog's live
instantiation flow. Those are the smoke test's job on a real Q2.
