# Release Notes — Sui 0.75Y

**Branch:** `Sui-0.75Y`  
**Base:** `Sui 0.75X` (CSV compare, test report, query stats, export tracking)  
**Date:** 2026-06-17  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Compare | New feature | **CSV File Compare.** New *Tools → Compare CSV Files…* wizard streams two CSV files of any size, computing full totals (matched / changed / left-only / right-only) while capturing only up to `SUI.CSVDIFFMAX` (default 20 000) differing rows. The captured sample is shown in the familiar DiffRep side-by-side view with the correct totals reflected in the summary and column summary |
| DiffRep | New feature | **Test Report tab.** A new *Test report* tab auto-generates a Markdown document covering: verdict (PASS / DIFFERENCES FOUND), sources, key columns, row summary, per-column summary, and the SQL used on each side. The report can be saved as `.md` or copied to the clipboard |
| DiffRep | Enhancement | **Column summary → Open in query view.** A new button on the *Column summary* tab opens the summary table as a full QueryRep result window (sortable, filterable, XLS-exportable) |
| DiffRep | Enhancement | **SQL passthrough to report.** When comparing two QueryRep windows directly (`diffDirectFromQueryRep`) or via *Re-run on another connection*, the SQL for each side is now forwarded to DiffRep and included in the test report |
| Main window | Enhancement | **Query stats in status bar.** The bottom status bar now shows the row count, status message, and duration of the most recently completed query run, alongside the existing cursor-position indicator |
| QueryBox | Enhancement | **Run stats in history navigator.** The info line in the QueryBox history navigator now includes the duration, row count, and status of the selected history entry in addition to the timestamp and connection URL |
| Query Monitor | Enhancement | **Export file tracking.** Each CSV and XLS export now records the output file path in the Query Monitor. A new *Exported File* column appears in the monitor window. `QryMon` also gains `getSqlForExportFile()` so CSV Compare can recover the originating SQL when the two files were exported from Sui in the same session |
| Query Monitor | Enhancement | **Buffer increased 100 → 500.** The ring buffer now holds the last 500 executed queries. The hardcoded `100` literal is replaced by a `QryMon.MAX` constant throughout |
| Compare / DiffRep | Bug fix | **Closed tabbed result windows no longer appear in the diff picker.** Tabbed `QueryRep` instances that were closed kept `isTabbed = true` and remained in `openSelectWindows`, surfacing as live candidates in the F7/F8 diff picker. A new `QueryRep.unregister()` method clears the flag and removes the entry; dead instances are also purged defensively during picker population |
| QueryBox | Bug fix | **Null-pointer guard in QueryBox navigation.** `getSQLStmt()` could return `null` for an uninitialized slot; calling `.isEmpty()` on it threw `NullPointerException`. Added an explicit `null` check before the test |

---

## Details

### CSV File Compare (`CsvCompare.java`, `Sui.java`)

Accessible via *Tools → Compare CSV Files…*. The wizard prompts for two CSV files
(defaulting to the configured export directory), then shows the common columns for
key selection (or whole-row matching if no keys are ticked).

The comparison runs off the EDT behind a modal progress dialog (`SwingWorker`):

- **Phase 1** — the right file is indexed in memory as `key → queue of rows`.
- **Phase 2** — the left file is streamed; each row is looked up in the index and
  classified as *matched*, *changed*, or *left-only*.
- **Phase 3** — any rows left in the index are *right-only*.

Only differing rows (up to `SUI.CSVDIFFMAX`) are forwarded to `DiffRep`.
`DiffRep.setBaseIdenticalRows(n)` is called with the full matched count so the
summary, column summary, and test report all reflect the true file-wide totals —
not just the captured sample.

The column metadata arrays sent to DiffRep are derived from the left-file header;
right-file columns are remapped into left-column order via `mapBtoA()` so the
side-by-side view aligns correctly even when the two files have different column
orders.

### Test Report tab (`DiffRep.java`, `HelpDialog.java`)

A new *Test report* tab is added next to *Column summary* in every `DiffRep`
window. It contains:

- A free-text *Test description / notes* area (persists while the window is open).
- A rendered Markdown preview (reuses `HelpDialog.renderPane()`) that regenerates
  on focus-loss and via an explicit **Refresh** button.
- **Save .md…** — saves the report as a UTF-8 Markdown file.
- **Copy Markdown** — copies the raw Markdown to the system clipboard.

The generated document includes: title / verdict / key columns / generated
timestamp, test description, left and right sources, a row-level summary table,
a per-column summary table (identical/differ counts per column, accounting for
`baseIdenticalRows`), and fenced SQL blocks for both sides (falls back to
*"SQL not available"* when not supplied).

### Query stats in main status bar (`Sui.java`)

A `lastRunLabel` is added to the south status panel alongside the cursor-position
indicator. After every query completes, `updateLastRunLabel(durMs, rows, status)`
formats and pushes a string such as `1 234 rows  |  OK  |  450 ms`. It fires both
from the history-update path (when the query is found in `QryList`) and from the
unconditional fall-through path for queries that are not tracked in history.

### Export file tracking (`QryMon.java`, `ExpCSV.java`, `ExpXLS.java`, `ExpXLSRS.java`, `QueryRep.java`, `RunIt.java`)

Each export class now exposes a `savedPath` field (set after a successful write).
Call sites in `QueryRep` and `RunIt` capture the field and call
`QryMon.setExpFileByStart(start, path)`. Multiple exports from the same slot
accumulate as a `|`-separated string in `QryMon.expFile[]`.

`QryMon.getSqlForExportFile(path)` walks the ring buffer to find the slot whose
`expFile` contains the given path (exact match, then bare filename fallback) and
returns the originating SQL. `CsvCompare` calls this to populate the SQL blocks
in the test report.

### Closed tabbed windows in diff picker (`QueryRep.java`, `QueryRepTabbedFrame.java`)

`QueryRepTabbedFrame.disposeTab(QueryRep)` disposes the frame but bypasses the
regular `closeRep()` cleanup, leaving the `QueryRep` in `openSelectWindows` with
`isTabbed = true`. The new `QueryRep.unregister(qr)` method removes the instance
from the list and clears the flag; `disposeTab` now calls it. The diff-picker
collection loop also defensively removes any entry where
`!qr.isDisplayable() && !QueryRepTabbedFrame.getInstance().containsQR(qr)`.

---

## Files Changed

| File | Change |
|---|---|
| `src/CsvCompare.java` | New — CSV streaming compare engine, key-column dialog, DiffRep integration |
| `src/DiffRep.java` | Test report tab; `setBaseIdenticalRows()`; Column-summary *Open in query view*; `initialKeyCols` + `leftSql`/`rightSql` constructor params; `baseIdenticalRows` accounted in summary and column summary |
| `src/HelpDialog.java` | New `renderPane(Window, String)` static method for embedding rendered Markdown in other windows |
| `src/QryMon.java` | `MAX = 500`; `expFile[]` array; `findIdxByStart()`, `setExpFile()`, `setExpFileByStart()`, `getSqlForExportFile()`; *Exported File* column in monitor window; array-size fix (`cT`/`cTn`/`cLen`/`cL` now sized to column count, not row count) |
| `src/ExpCSV.java` | `savedPath` field |
| `src/ExpXLS.java` | `savedPath` field |
| `src/ExpXLSRS.java` | `savedPath` field |
| `src/QueryRep.java` | Export actions capture `savedPath` → `QryMon`; `unregister()`; dead-entry purge in diff-picker; `lSql`/`rSql` passed to `DiffRep` on direct diff |
| `src/RunIt.java` | Export file paths recorded in `QryMon` for XLS and CSV background exports |
| `src/RunItDiff.java` | `leftSql` constructor parameter forwarded to `DiffRep` |
| `src/Sui.java` | *Compare CSV Files…* menu item; `lastRunLabel` status bar; `updateLastRunLabel()`; `QryMon.MAX` constant used in `ConcQueries` |
| `src/ShowQryBox.java` | `buildInfoLine()` adds duration/rows/status to history navigator; null guard on `getSQLStmt()` result |
| `src/QueryRepTabbedFrame.java` | `containsQR()` check; calls `QueryRep.unregister()` on tab dispose |
