# Release Notes — Sui 0.75O

**Branch:** `Sui0.75O`  
**Base:** `Sui 0.75N` (SQL Dialect Converter, Syntax Highlighting, Inline Directives)  
**Date:** 2026-05-13  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| SQL Dialect Converter | New feature | New `ConvertSqlDialog` — DB2-to-BigQuery SQL conversion with warnings panel |
| SQL Dialect Converter | New feature | `DECIMAL(expr, p, s)` → `ROUND(CAST(expr AS NUMERIC), s)` + warning |
| SQL Dialect Converter | New feature | `DECIMAL(expr, p)` → `CAST(expr AS NUMERIC)` + warning |
| SQL Dialect Converter | New feature | `VARCHAR_FORMAT(expr, fmt)` → `FORMAT_TIMESTAMP` / `FORMAT_DATE` with DB2-to-BigQuery format-string conversion |
| SQL Dialect Converter | New feature | `MERGE INTO` → `MERGE`; target-alias stripped from `UPDATE SET` blocks |
| SQL Dialect Converter | New feature | CTE `SELECT *` body: column header list stripped and warned instead of left as invalid syntax |
| SQL Dialect Converter | New feature | NVL, NVL2, ZEROIFNULL, NULLIFZERO, DECODE, ADD_MONTHS, CHR, ASCII, TRUNCATE, MINUS→EXCEPT DISTINCT, LISTAGG→STRING_AGG, VALUE→COALESCE, UCASE/LCASE, DATE/TIMESTAMP/TIME casts |
| SQL Dialect Converter | New feature | `convertCastTypes()` — maps data types inside CAST() (BIGINT↔INT64, VARCHAR↔STRING, etc.) for both directions |
| SQL Dialect Converter | New feature | DB2 query-control clauses stripped silently: `FOR FETCH ONLY`, `OPTIMIZE FOR n ROWS`, `WITH NC` |
| SQL Dialect Converter | New feature | New warnings: RAISE_ERROR, TRANSLATE, TIMESTAMP_FORMAT, XML functions, MONTHS_BETWEEN, GENERATE_UNIQUE, STDDEV/VARIANCE, DAYS, MIDNIGHT_SECONDS, SOUNDEX, TIMESTAMPDIFF |
| SQL Dialect Converter | Bug fix | Warning bullet character rendered as `â€¢` — fixed to `\u2022` |
| Options menu | New feature | "Convert SQL Dialect…" added to the Options menu |
| QryPop menu | Enhancement | Right-click menu reorganised — Format/Validate/Convert at top; file/table ops grouped; Edit ops at bottom |
| QryPop menu | Enhancement | "Sheet Preferences" item removed |
| Inline directives | New feature | `#URL=` directive — switches JDBC connection mid-script without changing the URL box |
| Inline directives | New feature | `#SET KEY=VALUE` alternative syntax (previously only `#SET= KEY VALUE`) |
| Inline directives | Bug fix | Query Report title now shows the `#URL=` override URL instead of the URL-box URL |
| Syntax highlighting | Enhancement | ~25 new SQL keywords added (JOIN, ON, NULL, IS, LIKE, BETWEEN, DISTINCT, WITH, OVER, PARTITION, MERGE, LIMIT, EXCEPT, INTERSECT, MINUS, FETCH, ROWS, ONLY, NEXT, OFFSET, CROSS) |
| Syntax highlighting | Enhancement | ~15 new DDL keywords added (INDEX, VIEW, UNIQUE, PRIMARY, KEY, FOREIGN, REFERENCES, CONSTRAINT, DEFAULT, COLUMN, PROCEDURE, FUNCTION, TRIGGER, SEQUENCE, SCHEMA) |
| Syntax highlighting | Enhancement | ~20 new function keywords added (TRIM, CONVERT, EXTRACT, NVL, LPAD, RPAD, LISTAGG, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, FIRST_VALUE, LAST_VALUE, NTILE, CUME_DIST, PERCENT_RANK, CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP, NUMERIC, INTERVAL, BOOLEAN, NVARCHAR, BIGINT) |
| Syntax highlighting | Bug fix | `/*` comment inside a `--` single-line comment no longer incorrectly coloured the rest of the document |
| Syntax highlighting | Performance | Syntax scanning skipped when document exceeds 5 000 characters; styles reset on every change to prevent colour bleeding |
| Syntax highlighting | Performance | `bulkLoadingSQL` guard in `Highlighter.processChangedLines` — all processing skipped during bulk `setText()` calls |
| SQL Tree | Enhancement | Schema node now groups objects into **Tables / Views / Aliases / Synonyms** sub-folders; only non-empty groups shown |
| SQL Tree | Enhancement | "Include routines" checkbox adds a lazy **Routines** group alongside the object-type groups |
| Excel export | Enhancement | Numeric columns written as Excel numeric cells; integers and decimals use separate configurable formats |
| Excel export | Enhancement | `BigDecimal` columns formatted as decimals; all others attempted as integers with fallback to string |
| Excel export | Enhancement | Meta sheet now includes "Result set status" (full / partial) and row count |
| Excel export | Enhancement | Font, integer format, and decimal format configurable in Preferences → Export |
| Excel export | Bug fix | SQL truncation bug in `ExpXLSRS`: `qry.substring(0,32000)` result was discarded — now assigned |
| Preferences → Export | New feature | New fields: XLS font name (dropdown of installed fonts), XLS integer format, XLS decimal format |
| ConnDB | Bug fix | `sanitizeUrl` negative lookahead prevents stripping `://` from BigQuery `https://` embedded URLs |
| Toolbar | Enhancement | Connection Manager toolbar button tooltip updated; action wired to `ConnManager` dialog |
| URL box | Enhancement | Improved userid/password resolution on URL change — session cache takes priority; profile fallback always applied |
| URL box | Enhancement | `resolveLocPaths()` now expands `&suihome` and `&user.home` placeholders in JDBC URL and driver paths |
| Ctrl+Enter | New feature | Ctrl+Enter is now an alias for Ctrl+R (Run Query), consistent with other SQL tools |
| Query Sheet Overview | New feature | New right-side panel (`QuerySheetListPanel`) showing all query sheets with last-run timestamps |
| Query Sheet Overview | New feature | Sortable `JTable` — both Sheet name and Last Run columns are clickable sort headers |
| Query Sheet Overview | New feature | AND/OR/IN find bar — highlights matching rows in yellow; plain text search as fallback |
| Query Sheet Overview | New feature | Double-click or "Open selected tab" context menu item switches to the tab |
| Query Sheet Overview | New feature | "Show content in query box" context menu item opens SQL of any sheet in `ShowQryBox` |
| Query Sheet Overview | New feature | Drag-and-drop row reordering — moves the physical tab and all associated `SheetProp` data |
| Query Sheet Overview | New feature | Reset button restores list order to current tab order and clears search highlights |
| Query Sheet Overview | New feature | Close button hides the panel; re-opened via **Options → Query Sheet Overview** |
| Query Sheet Overview | New feature | Tooltip on each TabbedPane tab shows "Last run: yyyy-MM-dd HH:mm:ss" |
| Right-panel layout | Enhancement | Right panel now uses a `JSplitPane` — gives a drag handle for manual width adjustment |
| Right-panel layout | Enhancement | Divider hidden (size=0) when no right panel is visible; restored when any panel is shown |
| Startup | Performance | `SUI.QUERYONCLOSE` no longer written to `SuiSys.pro` — eliminates slow startup from escaped multi-line SQL |
| Startup | Enhancement | Initial SQL loaded from `SuiSheetProp.pro` key `SQLQUERY.1`; falls back to `QUERYONCLOSE` for one-time upgrade migration |
| Startup | Enhancement | New "Show Query Sheet List at startup" checkbox in General Startup Preferences (`SUI.SHOWSHEETLIST`) |
| Report window sort | Performance | `SuiSortAdapter` — O(n²) selection sort replaced with `Arrays.sort` (timsort, O(n log n)); string values pre-cached before sort; `Double.parseDouble()` replaces deprecated `new Double()` |
| Connection Manager | Enhancement | ▲ Up / ▼ Down buttons added alongside drag for keyboard-friendly reordering |
| Connection Status Bar | New feature | Full-width status bar between toolbar and query tabs — light green when connected, grey when not |
| Connection Status Bar | New feature | Right-click the status bar for a popup of all in-session connections; selecting one fills credentials and connects |
| Connection Status Bar | Enhancement | History entries formatted as `HH:mm:ss - user - url` (plain dashes) |
| Main window layout | Enhancement | Connection status bar moved above query tabs (below toolbar); cursor position label moved to bottom of window |
| Query Sheet Overview | Enhancement | Colour swatch column (col 0) — left-click to assign tab colour via `JColorChooser`; right-click to clear |
| Query Sheet Overview | Enhancement | Sheet name column — double-click to rename in-place; propagated to the `JTabbedPane` tab title |
| Query Sheet Overview | Enhancement | Tab colours saved as `SUI.TABCOLOR.N` (`R,G,B`) in `SuiSys.pro` and restored at startup |
| Query Report | New feature | Row count status bar at the bottom — "Rows: N" or "Rows: N (of M)" when a filter is active |
| Version | Bump | `0.75N` → `0.75O` in `Sui.java`, `pom.xml`, About dialog |

---

## Detailed Changes by Area

---

### SQL Dialect Converter (`SqlDialectConverter.java`, `ConvertSqlDialog.java`)

A new **Convert SQL Dialect…** dialog is available from the **Options** menu and from the
right-click menu in the query editor. It converts DB2 SQL to BigQuery-compatible SQL and
collects warnings about constructs that were changed or need manual review.

#### Function conversions (DB2 → BigQuery)

| DB2 construct | BigQuery equivalent | Notes |
|---|---|---|
| `DECIMAL(expr, p, s)` | `ROUND(CAST(expr AS NUMERIC), s)` | Warning generated |
| `DECIMAL(expr, p)` | `CAST(expr AS NUMERIC)` | Warning generated |
| `VARCHAR_FORMAT(expr, fmt)` | `FORMAT_TIMESTAMP(bq_fmt, expr)` or `FORMAT_DATE(…)` | DB2 format tokens mapped to BigQuery strftime tokens |
| `NVL(a, b)` | `IFNULL(a, b)` | |
| `NVL2(a, b, c)` | `IF(a IS NOT NULL, b, c)` | |
| `ZEROIFNULL(a)` | `IFNULL(a, 0)` | |
| `NULLIFZERO(a)` | `NULLIF(a, 0)` | |
| `VALUE(a, b, …)` | `COALESCE(a, b, …)` | DB2 synonym for COALESCE |
| `DECODE(e, v1, r1, …)` | `CASE WHEN e = v1 THEN r1 … END` | |
| `ADD_MONTHS(d, n)` | `DATE_ADD(d, INTERVAL n MONTH)` | |
| `CHR(n)` | `CODE_POINTS_TO_STRING([n])` | |
| `ASCII(s)` | `TO_CODE_POINTS(s)[OFFSET(0)]` | |
| `TRUNCATE(n, s)` | `TRUNC(n, s)` | |
| `UCASE(s)` | `UPPER(s)` | |
| `LCASE(s)` | `LOWER(s)` | |
| `LISTAGG(col, sep) WITHIN GROUP (ORDER BY …)` | `STRING_AGG(col, sep ORDER BY …)` | |
| `MINUS` (set operator) | `EXCEPT DISTINCT` | |
| `MERGE INTO tgt t …` | `MERGE tgt AS t …` | `INTO` removed; target alias in `UPDATE SET` blocks de-qualified |
| `DATE(expr)` | `CAST(expr AS DATE)` | 1-arg form |
| `TIMESTAMP(expr)` | `CAST(expr AS TIMESTAMP)` | 1-arg form |
| `TIME(expr)` | `CAST(expr AS TIME)` | 1-arg form |

#### CAST type mapping (`convertCastTypes`)

| DB2 type (inside CAST) | BigQuery type |
|---|---|
| `DECIMAL`, `NUMERIC` | `NUMERIC` |
| `BIGINT`, `INTEGER`, `INT`, `SMALLINT`, `TINYINT` | `INT64` |
| `FLOAT`, `DOUBLE`, `DOUBLE PRECISION`, `REAL` | `FLOAT64` |
| `CHAR`, `VARCHAR`, `NCHAR`, `NVARCHAR`, `CHARACTER`, `CLOB` | `STRING` |
| `BLOB` | `BYTES` |
| `BOOLEAN` | `BOOL` |

Reverse mapping (BigQuery → DB2) is also applied when converting in the opposite direction.

#### DB2 query-control clauses stripped silently

The following DB2-only clauses have no BigQuery equivalent and are removed without a warning:

- `FOR FETCH ONLY` / `FOR READ ONLY`
- `OPTIMIZE FOR n ROWS`
- `WITH NC` / `WITHOUT NC`

#### New warnings

The converter now generates warnings for constructs that need manual review:
`RAISE_ERROR()`, `TRANSLATE()`, `TIMESTAMP_FORMAT()`, XML functions
(`XMLTABLE`, `XMLELEMENT`, `XMLAGG`, `XMLQUERY`, `XMLPARSE`),
`MONTHS_BETWEEN()`, `GENERATE_UNIQUE()`, `STDDEV()`/`VARIANCE()` (population vs sample),
`DAYS()`, `MIDNIGHT_SECONDS()`, `SOUNDEX()`, `TIMESTAMPDIFF()`.

#### Date format mapping (`convertDb2DateFmt`)

| DB2 token | BigQuery token |
|---|---|
| `YYYY` | `%Y` |
| `YY` | `%y` |
| `MONTH` | `%B` |
| `MON` | `%b` |
| `MM` | `%m` |
| `DD` | `%d` |
| `DAY` | `%A` |
| `DY` | `%a` |
| `HH24` | `%H` |
| `HH12`, `HH` | `%I` |
| `MI` | `%M` |
| `SS` | `%S` |
| `SSSSSS` | `%f` (microseconds) |
| `DDD` | `%j` |
| `IW` | `%V` (ISO week) |
| `WW` | `%U` (week of year) |
| `AM`, `PM` | `%p` |

---

### Inline Directives (`nonSQL.java`, `RunIt.java`)

#### `#URL=` — per-statement connection override

A SQL script can now switch JDBC connections mid-execution:

```sql
SELECT * FROM table1;

#URL= jdbc:db2://otherhost:50000/OTHERDB;

SELECT * FROM table2;
```

The target database must have been connected to during the current session so that
credentials are available in the session-only memory store. If the connection fails,
an error message is shown and execution stops. The override is reset at the start of
each Run.

The Query Report window title reflects the overriding URL, not the URL-box URL.

#### `#SET` — new syntax

In addition to the original `#SET= KEY VALUE` form, the natural `KEY=VALUE` form is
now also accepted:

```sql
#SET MYSCHEMA=REPORTING;

SELECT * FROM &&MYSCHEMA..ORDERS;
```

See [InlineDirectives.md](InlineDirectives.md) for full documentation.

---

### Syntax Highlighting (`Highlighter.java`)

- Approximately 60 additional SQL keywords are now recognised and coloured.
- **Performance cap**: when the editor document exceeds 5 000 characters, keyword
  scanning is skipped entirely. The `HighLightOn` preference is not changed.
- **Bulk-load guard**: the `bulkLoadingSQL` flag in `Sui` is set during `setSQL()` calls;
  `processChangedLines` returns immediately when it is set, preventing the
  `setCharacterAttributes(0, fullLength)` sweep from running thousands of times during
  a large `setText()`.
- **Comment fix**: a `/*` token appearing after `--` on the same line no longer
  triggers multi-line comment colouring for the rest of the document.
- Styles are reset on every keystroke to prevent colour bleeding when highlighting
  is toggled off mid-session.

---

### SQL Object Tree (`SQLTreePanel.java`)

When a schema node is expanded, objects are now placed into typed sub-folders:

| Sub-folder | TABLE_TYPE values |
|---|---|
| **Tables** | TABLE, SYSTEM TABLE, GLOBAL TEMPORARY, LOCAL TEMPORARY, and any unrecognised type |
| **Views** | VIEW, SYSTEM VIEW |
| **Aliases** | ALIAS |
| **Synonyms** | SYNONYM |

Empty sub-folders are not shown. If "Include routines" is checked, a **Routines**
lazy-load group is appended after the object-type groups.

---

### Excel Export (`ExpXLS.java`, `ExpXLSRS.java`, `PropmExp.java`, `QueryRep.java`)

#### Numeric cell handling

- Columns are classified using the JDBC `java.sql.Types` column-type array.
- `DECIMAL`/`NUMERIC` columns are formatted as decimal numbers using `BigDecimal` and
  a configurable decimal format string.
- Integer-type columns are written as `int` values with a separate configurable format string.
- Non-numeric columns remain as strings.

#### Bug fix — SQL truncation in ExpXLSRS

The statement `qry.substring(0, 32000)` was called without assigning the result back to `qry`,
so the full (potentially very long) string was written to the meta sheet. Fixed.

#### Meta sheet additions

Two new rows are written to the `Sui-Meta` sheet:

| Row | Content |
|---|---|
| Result set status | "full result set" or "partial result set" (when row limit was hit) |
| Report rows | Number of rows in the export |

#### Preferences

Three new fields appear in **Preferences → Export**:

| Preference | Property key | Default |
|---|---|---|
| XLS font name | `SUI.XLS.FONT` | `Courier` |
| XLS integer format | `SUI.XLS.INTFMT` | `0` |
| XLS decimal format | `SUI.XLS.DECFMT` | `# ##0.000` |

The font name is selected from a dropdown populated with all fonts installed on the local system.

---

### ConnDB — BigQuery URL fix (`ConnDB.java`)

The `sanitizeUrl` helper that strips empty port colons from JDBC URLs
(e.g. `jdbc:mysql://host:/db` → `jdbc:mysql://host/db`) now uses a negative
lookahead to avoid matching the embedded `https://` in BigQuery JDBC URLs.

---

### QryPop Right-click Menu (`QryPop.java`)

The right-click context menu in the query editor has been reorganised:

1. Format SQL
2. Ext Format SQL
3. Syntax Validate / Syntax Validate by Prepare
4. ───────────────
5. Convert SQL Dialect…
6. Remove Initial numerics… / InList / TextIns
7. ───────────────
8. Del CSV / Del XLS / Del tmp
9. ───────────────
10. Highlighting / ParenHig / HideQ·ShowQ / LineNo / QueryToolbar / SQLTree
11. ───────────────
12. Box / SheetBox / Imp
13. ───────────────
14. Copy / Cut / Paste / Trim Trailing Whitespace / Copy Columns from Selection…

"Sheet Preferences" has been removed.

---

### Options Menu / Keyboard (`Sui.java`)

- **"Convert SQL Dialect…"** has been added at the bottom of the **Options** menu.
- **Ctrl+Enter** is now registered as an alias for **Ctrl+R** (Run Query), consistent
  with how most other SQL tools work.

---

### URL Box — Credential Resolution (`Sui.java`)

When the user selects a different URL in the URL dropdown, userid and password are now
resolved in a stricter priority order:

1. **Userid** — session cache (`SUI.USERID.<url>`) → connection profile in `SuiConnProp.pro`
2. **Password** — session cache (`SUI.PW.<uid>.<url>`) → blank if `SUI.SETPWBLANK=Y` → AutoLogin saved password

`resolveLocPaths()` now expands `&suihome` and `&user.home` placeholders before globbing,
so JDBC URL templates and driver paths that reference the Sui home directory work correctly
on all systems.

---

### Query Sheet Overview (`QuerySheetListPanel.java`, `Sui.java`, `TabbedPaneClassic.java`)

A new **Query Sheet Overview** panel can be opened from **Options → Query Sheet Overview**
or automatically at startup when the corresponding preference is enabled.

The panel is placed on the right side of the main window in a `JSplitPane`, giving a
draggable divider. When no panel is visible the divider is hidden (size = 0) to avoid
wasting space.

#### Features

| Feature | Description |
|---|---|
| Sortable table | Click either column header to sort ascending / descending |
| Find bar | Plain-text search, or AND/OR/IN logic when "AND/OR" checkbox is checked; matched rows highlighted in yellow |
| Double-click / "Open selected tab" | Switches the main `TabbedPane` to the corresponding tab |
| "Show content in query box" | Opens the SQL of any sheet in a `ShowQryBox` window without switching tabs |
| Drag-and-drop reorder | Drag a row to a new position; calls `Sui.MoveTab()` which moves the physical tab and all `SheetProp` data |
| Reset button | Removes any active sort and clears search highlights; list reverts to tab order |
| Close button | Hides the panel |
| Tab tooltip | Hovering over a tab in `TabbedPane` shows "Last run: yyyy-MM-dd HH:mm:ss" |

---

### Startup Performance (`Sui.java`, `Highlighter.java`)

Two changes that together eliminate a common cause of slow startup when the last active
query sheet contained a large SQL statement:

1. **`SUI.QUERYONCLOSE` no longer written** — the SQL for each sheet is already stored
   in `SuiSheetProp.pro` as `SQLQUERY.N`. Writing the same SQL a second time into
   `SuiSys.pro` via `Properties.store()` caused it to be escaped as a single very long
   line, which made the next startup slow to parse. On the first startup after the upgrade
   the old `QUERYONCLOSE` value is still read as a fallback.

2. **`bulkLoadingSQL` flag** — set to `true` in `setSQL()` for strings longer than 5 000
   characters, and checked at the top of `Highlighter.processChangedLines`. The
   `DefaultStyledDocument` fires one event per character during `setText()`, each of which
   previously triggered a full-document `setCharacterAttributes()` sweep.

---

### Report Window Sort Performance (`SuiSortAdapter.java`)

The sort algorithm in the query result window has been rewritten:

| Before | After |
|---|---|
| O(n²) selection sort with nested loops | `Arrays.sort` (timsort, O(n log n)) |
| `realModel.getValueAt()` called O(n²) times | All values pre-cached as `String[]` before sort |
| `new Double(s)` (deprecated) | `Double.parseDouble(s)` |
| No exception handling for non-numeric strings | `NumberFormatException` caught; falls back to string comparison |

The change is transparent to the user — sort direction (ascending/descending) is
preserved exactly as before.

---

### Connection Manager — Reorder Connections (`ConnManager.java`)

Two new buttons have been added to the connection list panel:

- **▲ Up** — moves the selected connection one position up
- **▼ Down** — moves the selected connection one position down

The order of connections in the list determines the order in which they appear in the
URL dropdown in the main query window after the next Save. This allows frequently used
connections to be placed at the top without renaming them.

---

### General Startup Preferences (`PropmLogin.java`, `Sui.java`)

A new checkbox **"Show Query Sheet List at startup"** has been added to the General
Startup Preferences panel. When checked, `Sui.showSheetList()` is called automatically
after the main window is built.

**Property key:** `SUI.SHOWSHEETLIST` (values: `Y` / `N`, default `N`)

---

### Connection Status Bar (`Sui.java`)

The previous plain text status bar has been replaced by a full-width label placed **between the toolbar and the query tabs**. The cursor position label has moved to the very bottom of the window, matching the convention used by VS Code, IntelliJ, and Eclipse.

| State | Background | Text colour |
|---|---|---|
| Connected | `(198, 239, 206)` light green | `(0, 97, 0)` dark green |
| Not connected | `(220, 220, 220)` grey | `(80, 80, 80)` dark grey |

Right-clicking the bar opens a popup listing every connection made during the current session. The most recently used entry is highlighted green. Clicking any entry restores the credentials and immediately triggers a new connection attempt — useful for quickly jumping between databases.

---

### Query Sheet Overview — Colour Swatches and Rename (`QuerySheetListPanel.java`, `Sui.java`)

Two quality-of-life enhancements to the Query Sheet panel:

- **Colour column (col 0)**: a fixed 18 px swatch shows the assigned tab colour. Left-click opens `JColorChooser`; right-click clears the colour. Changes are applied immediately to the `JTabbedPane` tab.
- **Rename in-place (col 1)**: double-clicking the sheet name column puts it into edit mode. Pressing Enter or clicking away commits the rename to the `JTabbedPane` tab title.
- **Persistence**: tab colours are stored in `SuiSys.pro` under `SUI.TABCOLOR.N` as `R,G,B` strings and restored at startup.

---

### Query Report Row Count (`QueryRep.java`)

Every result window now shows a status label at the bottom:

- **`Rows: N`** — when no filter is active or the filter matches all rows.
- **`Rows: N (of M)`** — when a filter reduces the visible set; `M` is the total unfiltered row count.

The label is updated after every filter change, sort, and initial table population.
