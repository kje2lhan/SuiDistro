# Release Notes — Sui 0.75Q

**Branch:** `Sui0.75P` → `Sui0.75Q`  
**Base:** `Sui 0.75P` (Result Set Compare, System Log, Split-pane one-touch buttons)  
**Date:** 2026-05-15  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Result Set Compare | Enhancement | Row filter toggle buttons: All / Left only / Right only / Differ — instantly hide rows that do not match the selected category |
| Result Set Compare | Enhancement | Filter respects "Open in Query View" and Export CSV — only the currently visible (filtered) rows are included |
| Result Set Compare | Enhancement | Compare directly from another open QueryRep window (in-memory, no SQL re-execution) via the Diff popup menu |
| Result Set Compare | Enhancement | Closed QueryRep windows excluded from the diff picker list (`isDisplayable()` check) |
| Result Set Compare | Bug fix | Extra `?` column appeared when comparing two QueryRep windows directly — right-side column count now uses null-stop loop matching the left-side logic |
| Result Set Compare | Enhancement | Numeric value comparison uses `BigDecimal` arithmetic based on actual JDBC column type — trailing zeros, different scales, and different integer types (e.g. DB2 SMALLINT vs BigQuery INT64) no longer produce false diffs |
| Result Set Compare | Enhancement | Numeric key matching uses `BigDecimal.stripTrailingZeros()` so `42`, `42.0` and `42.00` all map to the same key — rows match correctly across databases with different numeric precision |
| Result Set Compare | Bug fix | Unicode block-drawing characters in column headers and legend replaced with plain ASCII (`< COL` / `COL >`, `...`) — eliminates garbled characters on Windows terminals and some fonts |
| Query Report | New feature | **Trim** checkbox in toolbar — when checked, trailing whitespace is stripped from every cell value and from each copied line (applies to toolbar Copy and right-click Copy selected data) |
| Query Report | Bug fix | "Apply Filter" was missing from the column header right-click popup menu — `pop.add(Filt)` was never called; now appears as the first item |
| Query Report | Bug fix | Apply Filter blocked for numeric columns (INTEGER, DECIMAL) with large DB-reported display size (e.g. BigQuery INT64) — the length guard `tcLn > 500` has been removed for non-String columns |
| Query Report | Enhancement | Filter dialog uses a **numeric text field** for INTEGER, BIGINT, SMALLINT, TINYINT, DECIMAL and NUMERIC columns; `FltTp=2` (numeric) now also covers `BigDecimal` and `Long` column classes |
| Preferences — Start Up | Enhancement | "Start up" tab in Preferences restructured into five titled sub-panels: Window layout, Query sheets, Show at startup, SQL Object Tree content, Miscellaneous — replaces a single flat grid |
| Preferences — Export | Enhancement | "Export" tab in Preferences restructured into three titled sub-panels: General, CSV, Excel (XLS) — groups related settings and eliminates visual clutter |
| Documentation | New | `docs/ResultSetCompare.md` — comprehensive guide to the Result Set Compare feature (compare modes, colour coding, key matching, numeric normalisation, filters, export) |
| Documentation | Update | `docs/QueryRepWindow.md` — updated for Trim checkbox, corrected Apply Filter section (numeric columns, filter dialog behaviour) |
| Version | Bump | `0.75P` → `0.75Q` in `Sui.java`, `pom.xml`, About dialog |

---

## Detailed Changes by Area

---

### Result Set Compare — Row Filters (`DiffRep.java`)

Four **Show:** toggle buttons are now displayed in the bottom-right legend bar:

| Button | Rows shown |
|---|---|
| **All** | Every row (default) |
| **Left only** | Rows that exist only in the left result set |
| **Right only** | Rows that exist only in the right result set |
| **Differ** | Matched rows where at least one cell value differs |

Switching the filter is instant. The summary counts always reflect the complete diff.
**Open in Query View** and **Export CSV** include only the currently visible rows.

---

### Result Set Compare — Direct In-Memory Compare (`DiffRep.java`, `QueryRep.java`)

The **Diff** popup on a QueryRep window now has two sections:

1. **Open result windows** — lists every other currently open SELECT result window
   (closed/disposed windows are excluded via `isDisplayable()`). Choosing one compares
   the two in-memory result sets directly without any SQL re-execution or password prompt.

2. **Re-run against connection** — the existing behaviour: select a session connection,
   edit the SQL, enter a password if required, run in background.

The `diffDirectFromQueryRep(QueryRep other)` method handles path 1, passing both windows'
`tcD` / `tcL` / `tcCT` arrays directly to `DiffRep`.

---

### Result Set Compare — Numeric Comparison (`DiffRep.java`)

#### Cell value comparison

`valsEqual(String a, String b, int mergedCol)` first tries a normalised string comparison.
If that fails, and the column's JDBC type is numeric (`isNumericType(sqlType)` returns true
for TINYINT, SMALLINT, INTEGER, BIGINT, FLOAT, REAL, DOUBLE, NUMERIC, DECIMAL), the values
are parsed as `BigDecimal` and compared with `compareTo`. This means:

- `123` == `123.000` (different scales)
- `1.5E2` == `150` (exponent notation)
- DB2 SMALLINT `42` == BigQuery INT64 `42` (different JDBC type codes)

The JDBC type is taken from the left-side column metadata (`mergedColTypes[]`).

#### Key normalisation

`normKeyVal(String s, int mergedCol)` normalises key values for HashMap lookup.
For numeric columns, it parses to `BigDecimal`, calls `stripTrailingZeros()`, and returns
`toPlainString()`. This ensures `42`, `42.0`, and `42.00` all produce the same HashMap key
so rows are matched correctly when the two databases use different precision settings.

---

### Query Report — Trim Checkbox (`QueryRep.java`)

A **Trim** checkbox was added to the toolbar immediately after the Copy button.

- When checked, `copyTrim(String s)` strips trailing whitespace (all chars `<= ' '`) from
  each cell value before appending it.
- After assembling a line, a second pass strips any trailing whitespace from the full line
  (including the trailing space added between cells).
- The flag `trimCopyTrailing` applies to all three copy paths: toolbar CopyRow(), the column
  header popup "Copy Selected data", and the row area popup "Copy Selected data".

---

### Query Report — Apply Filter Fix (`QueryRep.java`)

Two bugs were fixed:

1. **Menu item missing**: `pop.add(Filt)` was never called, so "Apply Filter" never appeared
   in the column header right-click popup. It now appears as the first item, followed by a
   separator before "Column Information".

2. **Length guard blocked numeric columns**: The previous guard condition
   `|| (Tp != String.class && tcLn[ix] > 500 && tcLn[ix] != 0)` incorrectly blocked
   INTEGER and BigDecimal columns when the JDBC driver reported a large display size
   (BigQuery reports very large values for INT64 and NUMERIC). The length guard has been
   removed entirely for non-String columns — only the type check remains.

The `FltTp` assignment was also extended to cover `Long.class` and `BigDecimal.class`
(both now map to `FltTp = 2`, numeric filter mode).

---

### Preferences Restructuring (`PropmLogin.java`, `PropmExp.java`)

#### Start Up tab (`PropmLogin.java`)

The flat grid layout was replaced with five titled sub-panels using `BoxLayout.Y_AXIS`:

| Panel | Contents |
|---|---|
| **Window layout** | Initial size: vertical %, horizontal %, tree width |
| **Query sheets** | Number of sheets, Connection vars per sheet |
| **Show at startup** | Toolbar (FavBar / SheetList), Left panel (FileTree / SQLTree), Row numbers |
| **SQL Object Tree content** | Include routines, Include indexes |
| **Miscellaneous** | Wrap query text, Load all JDBC drivers |

The FavBar/SheetList pair and FileTree/SQLTree pair are each made mutually exclusive
(selecting one deselects the other) within their respective labelled rows.

#### Export tab (`PropmExp.java`)

The flat grid layout was replaced with three titled sub-panels:

| Panel | Contents |
|---|---|
| **General** | Export data path, Delete command, Delete temp files at startup |
| **CSV** | File suffix, Delimiter char, Character delimiter, First row empty |
| **Excel (XLS)** | Launch XLS file, Launch command, Font, Integer format, Decimal format |
