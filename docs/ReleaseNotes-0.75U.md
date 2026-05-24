# Release Notes — Sui 0.75U

**Branch:** `Sui0.75T` → `Sui0.75U`  
**Base:** `Sui 0.75T` (no-wrap fix, named diff presets, alias in window title)  
**Date:** 2026-05-24  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Cross-Connection Broadcast | New feature | Run one SQL against multiple connections in one step — tick target connections, set optional per-connection schema override, get one result window per target |
| Cross-Connection Broadcast | New feature | Vendor-aware `SET SCHEMA` injection before each query (DB2, Oracle, PostgreSQL, SQL Server, MySQL/MariaDB) |
| Cross-Connection Broadcast | New feature | Named target groups — save, load and delete groups of connections+schemas to `BroadcastGroups.pro` |
| Cross-Connection Broadcast | New feature | Accessible from main menu ("Cross-Connection Broadcast…") and right-click popup ("Broadcast to connections…") |
| Performance | Optimization | `ExpCSV` — row builder switched from `String.concat` chain to `StringBuilder` (per-row was O(n²)); large CSV exports now run in linear time and produce far less GC pressure |
| Performance | Optimization | `ExpXLS` / `ExpXLSRS` — cell styles + fonts configured once instead of mutated per cell (was hundreds of thousands of redundant setter calls on large exports); SXSSF auto-sizing now tracked *before* rows are written so it actually measures all data instead of only the last 100 rows in the streaming window; `BIGINT` values no longer fall back to string — `Long`/`Double` parse path covers them |
| Performance | Optimization | `formatJSON` — character-by-character accumulator switched from `ret += c` to `StringBuilder`; eliminates the O(n²) string-copy blow-up on large JSON payloads |
| Performance | Optimization | `FormatXML` — output accumulator switched from static `String` concatenation to a local `StringBuilder`; the method is also re-entrant now (no shared static state between calls) |
| Transpose window | Bug fix | `IllegalArgumentException: Row index out of range` eliminated — F8 in the transpose window's row-header column no longer crashes when no row is selected |
| Transpose window | New feature | **F7/F8 row navigation** — press F8 for next row's transpose, F7 for previous row; works in both free-floating and tabbed modes |
| Transpose window | Enhancement | Old transpose is removed (tab or window) when F7/F8 opens the replacement — no orphan windows or tabs accumulate |
| Transpose window | Bug fix | Transpose window captures keyboard focus on open — F7/F8 fires on the first keypress, not the second |
| Version | Bump | `0.75T` → `0.75U` |

---

## Detail

### Cross-Connection Broadcast (`Broadcast.java`)

A new dialog accessible from two entry points:
- **Main menu → Tools → Cross-Connection Broadcast…** — pre-loads the current query editor text
- **Right-click popup → Broadcast to connections…** — pre-loads the selected/full query text

The dialog shows every URL that has been connected in this session (from `ConnHistory`).
Tick the target rows, optionally fill in a schema override per connection, then click
**Run broadcast**. A multi-statement script is assembled using the existing `#URL=` directive
to retarget between SELECTs; a vendor-appropriate `SET SCHEMA` statement is injected after
each `#URL=` when a schema is specified and the vendor is known (DB2, Oracle, PostgreSQL,
SQL Server, MySQL/MariaDB). The script is handed to `RunSql`/`RunIt` as a single batch,
producing one `QueryRep` result window per target.

**Named groups** — tick a set of connections, click **Save group…**, give it a name.
Groups persist to `BroadcastGroups.pro` in the Sui home directory and reload automatically.
Per-alias default schemas are also written to `SUI.CONN.<alias>.SCHEMA` in `ConnProp`
so they pre-fill the dialog on subsequent opens.

### Performance optimizations

Three classic O(n²) string-concatenation hot spots were replaced with `StringBuilder`,
mirroring the sort-algorithm replacement in earlier releases. None of these change behaviour
— only allocation patterns and runtime on large inputs.

- **`ExpCSV`** — the inner cell loop built each row via `Data = Data.concat(…)` and the outer
  row loop reset and rebuilt the buffer per row. For a 10 000 × 50 cell export this meant
  ~500 000 intermediate `String` copies. Now a single `StringBuilder` is reused with
  `setLength(0)` between rows. Behaviour preserved: header `.trim()` semantics, the
  `SUI.CSVEMPTY` blank-line prefix, and the per-column `String`-class quoting branch.
- **`ExpXLS` / `ExpXLSRS`** — three POI-specific issues fixed:
  1. *Cell styles and fonts mutated per cell.* The old `createCell` called
     `cs.setVerticalAlignment(…)`, `cs.setAlignment(…)`, `cs.setDataFormat(…)`,
     `cs.setFont(…)` and `f1.setFontHeightInPoints(…)` on every single cell, even though
     the values are constant. For a 10 000 × 50 cell export that’s ~500 000 redundant POI
     setter calls on five shared `CellStyle` objects. Now the styles and fonts are
     configured **once** in the constructor and `createCell` only writes the value and
     assigns the pre-built style. POI's golden rule: configure `CellStyle`/`Font` once,
     reuse the reference.
  2. *Auto-sizing was effectively a no-op on big result sets.* SXSSF flushes rows out of
     its 100-row window to disk; once flushed they are invisible to `autoSizeColumn`. The
     old code called `trackColumnForAutoSizing` **after** all rows were written, so the
     auto-size only ever saw the last 100 rows (and was still expensive because of POI's
     font-metric measurement). Tracking is now hoisted to `trackAllColumnsForAutoSizing()`
     before any row is created, and the post-write loop just calls `autoSizeColumn` once
     per column. Both correct *and* faster.
  3. *Long integers fell back to string.* `Integer.valueOf(x.trim())` threw for any value
     outside the `int` range (every `BIGINT`, every long-ish identifier). The catch wrote
     the raw string, defeating Excel's numeric handling. The parse chain is now
     `Long.parseLong` → `Double.parseDouble` → string, so 64-bit integers stay numeric.
  Also removed the deprecated `cell.setCellType(CellType.NUMERIC)` call —
  `setCellValue(long/double)` already establishes the cell type.
- **`formatJSON`** — character-loop accumulator changed from `String ret = ""; ret += c…`
  to `StringBuilder ret`. Indent runs that previously called `String.format("%Ns", "")`
  to manufacture spaces are now plain `append(' ')` loops (no formatter allocation,
  no width-parsing). The backslash-lookahead `chars[++i]` is preserved.
- **`FormatXML`** — dropped the shared `private static String utXML` accumulator and the
  `SkrivRad()` helper; the output is built into a local `StringBuilder` and returned.
  Side benefit: the method is now re-entrant (the old static state would corrupt output
  if two threads ever called `FormatXML` concurrently).

### F8 crash fix (`QueryRep` — row-header key listener)

`table.addRowSelectionInterval(-1, -1)` was called when `tablef.getSelectedRow()` returned `-1`
(no row selected in the row-header column).  A `sel >= 0` guard was added so the interval
is only set when a valid row is selected.

### F7/F8 row navigation

`mainPanel` input-map bindings (using `WHEN_ANCESTOR_OF_FOCUSED_COMPONENT` for child windows,
`WHEN_IN_FOCUSED_WINDOW` for the parent) replace the old menu-accelerator approach, which
stopped working once a panel was moved into `QueryRepTabbedFrame`.

- **Parent window** — F8 opens a transpose for the currently selected row in the main data
  table (`table.getSelectedRow()`).
- **Child (transpose) window** — F8 calls `MyParent.PosRows(true)` (next row) then disposes
  or removes the current child; F7 calls `PosRows(false)` (previous row).
- **Tabbed child** — `QueryRepTabbedFrame.disposeTab(QueryRep)` removes the tab entry *and*
  disposes the backing JFrame in one step, preventing orphan tabs.
- **Free-floating child** — `showOrTab` now calls `qr.toFront()` after `qr.show()` so the
  new window comes in front of the parent.

### Focus fix (`showOrTab`)

`qr.table.requestFocusInWindow()` is called after the new child is shown or added to the
tabbed frame.  This satisfies the `WHEN_ANCESTOR_OF_FOCUSED_COMPONENT` condition immediately,
so the first F7/F8 keypress navigates rather than just moving focus.
