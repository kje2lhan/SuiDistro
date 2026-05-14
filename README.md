# Sui — SQL Utility Interface

Sui is a Java Swing desktop application for interacting with relational databases over JDBC. It provides a query editor, SQL object browser, result viewer with export, and a rich set of utilities that make day-to-day database work faster and less error-prone. Sui has built-in optimisations and tooling for **IBM DB2** (LUW and z/OS) and **Google BigQuery**, while remaining fully functional with any JDBC-compatible database.

---

## Key Features

### Query Editor
- Write and execute SQL statements in a tabbed multi-sheet editor.
- Execute the statement at the cursor with a single keystroke (Shift+F1 to mark, Shift+F2 to execute).
- Execute selected SQL only, or send results directly to an Excel worksheet.
- Toggle comments (Ctrl+7), go to line (Ctrl+G), block indent/unindent (Tab/Shift+Tab), uppercase/lowercase selection (Ctrl+Shift+U/L), trim trailing whitespace (Ctrl+Shift+X).
- Parenthesis-matching highlight, cursor position indicator (Ln/Col).
- Include external SQL files with `<include>path/to/file</include>` syntax.
- Configurable variable substitution (default `&`, e.g. swap to `:` for JDBC-style parameters).

### SQL Dialect Converter
- Bidirectional **DB2 ↔ BigQuery** SQL translation engine (`SqlDialectConverter`).
- DB2→BQ: strips isolation-level hints, rewrites special registers, removes `SYSIBM.SYSDUMMY1`/`DUAL`, translates `FETCH FIRST n ROWS ONLY` → `LIMIT n`, interval arithmetic, function transforms (YEAR/MONTH/DAY → EXTRACT, CHAR/INTEGER/FLOAT → CAST, STRIP → TRIM, LOCATE/POSSTR → STRPOS), and CTE column-list push-down.
- BQ→DB2: backtick identifiers → double-quoted, `CURRENT_TIMESTAMP()/DATE()/TIME()` → DB2 special registers, IF → CASE WHEN, IFNULL → COALESCE, TO_HEX → HEX, SAFE_CAST → CAST with warning.
- Accessible via right-click → "Convert SQL Dialect…"; result, warnings, and target schema are shown in a dedicated dialog; settings persisted between invocations.

### SQL Object Tree
- Lazy-loading tree of schemas → tables → columns (with optional indexes and routines/stored procedures).
- Right-click a table: Build SQL, Draw SELECT/INSERT, Count Rows, Generate DDL, List Referential Integrity, Additional Table Info, Table Space Information, View Definition.
- Right-click a column: Column Statistics (MIN/MAX/COUNT DISTINCT), Sample Unique Values.
- Right-click a stored procedure or function: Draw SP (F9), Execute SP, Draw Function.
- Drag a table or column node to the query window to insert SQL snippets at the caret.
- Schema and table filter fields; "Include indexes" and "Include routines" checkboxes; BigQuery table/column names are case-preserving.

### Result Viewer & Export
- Tabular query results with fixed decimal precision for NUMERIC/DECIMAL columns.
- Export to **Excel** (XLS/XLSX) and **CSV**.
- Query Report: right-click a row to copy a `WHERE col = val AND …` clause.
- "Build IN List from Selection" and "Copy Columns from Selection…" in the editor popup.
- Syntax validate by Prepare — validates SQL via the active JDBC connection.

### SQL Formatting
- Extended Format SQL: configurable dialect, indent width, uppercase keywords, lines between queries, max column length, parenthesis whitespace, trailing vs. leading commas.
- Format JSON strings for readability.

### Query History Viewer
- Every executed query is recorded with a timestamp and connection URL (up to 9 000 entries, configurable).
- URL filter combobox, AND/OR/IN advanced search syntax in the Find field.
- Status bar shows timestamp + URL; tooltip summarises entry count and date range.

### Connection Management
- Multi-connection support with saved JDBC URL profiles, usernames and optional driver properties.
- **BigQuery**: OAuth connection cache with a 10-hour TTL — avoids repeated authentication round-trips.
- **DB2**: SQLCODE -4471 workaround; system schemas filtered; `null` column-name pattern for metadata calls; z/OS vs LUW detected for F6/F7/F8 actions.
- **Mimer SQL**: `null` catalog and table-type filter; schema name uppercased; `AbstractMethodError` on `getFunctionColumns()` caught.
- All cached connections are closed gracefully at application exit with an elapsed-time log.
- Per-URL JDBC driver properties via `SuiConnPref.pro` (supports `&suihome` path token).
- Alt+0…Alt+9 connection profiles for instant switching.

### Customisable UI
- Pluggable Look & Feel via `Sui.ini` — supports FlatLaf (dark/light) and any IntelliJ theme.
- Configurable global font (name + size).
- Pyjamas report formatting toggle.

### Security & Data Safety
- Password is **never written to disk** unless the user explicitly saves it in Preferences.
- Safe-write pattern for all `.pro` files (write-to-temp → rename, with `.bak` rollback).
- Automatic per-session and shutdown backups in `SuiBup/` with 30-day rotation.
- Automatic fallback to `.bak` on load failure.

---

## Getting Started

See **[USAGE.md](USAGE.md)** for build instructions, prerequisites, and a quick-start guide.

---

## Documentation

| Document | Description |
|---|---|
| [USAGE.md](USAGE.md) | Build instructions, prerequisites, running Sui, property files overview |
| [docs/SuiHome.md](docs/SuiHome.md) | How the Sui home directory is resolved; `Sui.ini` syntax, symbolic tokens, Look & Feel / FlatLaf configuration |
| [docs/ConnDB.md](docs/ConnDB.md) | JDBC connection factory logic, BigQuery LRU cache and TTL eviction, `closeAllConnections()` at shutdown |
| [docs/CredentialHandling.md](docs/CredentialHandling.md) | How user IDs and passwords flow through the application; what is and is not written to disk; security recommendations |
| [docs/ProFileRecovery.md](docs/ProFileRecovery.md) | All `.pro` configuration files described; safe-write pattern; `SuiBup/` backup folder; recovery procedures for each file type |
| [docs/ConnManager.md](docs/ConnManager.md) | Connection Manager dialog — creating and managing JDBC connection profiles, driver catalog, JDBC properties |
| [docs/InlineDirectives.md](docs/InlineDirectives.md) | Inline script directives — `#URL=`, `#SET`, `#REM`, and other mid-script control statements |
| [SECURITY.md](SECURITY.md) | Supported versions and how to report a vulnerability |

### Release Notes

| Version | Notes |
|---|---|
| 0.75O | [docs/ReleaseNotes-0.75O.md](docs/ReleaseNotes-0.75O.md) |
| 0.75N | [docs/ReleaseNotes-0.75N.md](docs/ReleaseNotes-0.75N.md) |
| 0.75M | [docs/ReleaseNotes-0.75M.md](docs/ReleaseNotes-0.75M.md) |
| 0.75L | [docs/ReleaseNotes-0.75L.md](docs/ReleaseNotes-0.75L.md) |
| 0.75K | [docs/ReleaseNotes-0.75K.md](docs/ReleaseNotes-0.75K.md) |
| 0.75J | [docs/ReleaseNotes-0.75J.md](docs/ReleaseNotes-0.75J.md) |
| 0.75G | [docs/ReleaseNotes-0.75G.md](docs/ReleaseNotes-0.75G.md) |
| 0.75F | [docs/ReleaseNotes-0.75F.md](docs/ReleaseNotes-0.75F.md) |
| 0.75C | [docs/ReleaseNotes-0.75C.md](docs/ReleaseNotes-0.75C.md) |
| 0.75B | [docs/ReleaseNotes-0.75B.md](docs/ReleaseNotes-0.75B.md) |
| 0.75A | [docs/ReleaseNotes-0.75A.md](docs/ReleaseNotes-0.75A.md) |

---

## Change Log

### Sui 0.75O
---------
- **Connection status bar** — full-width bar between the toolbar and query tabs; light green when connected, grey when not; right-click for a popup of all in-session connections to quickly switch databases
- Cursor position label (`Ln / Col`) moved to the very bottom of the window — standard IDE convention
- **Query Sheet Overview**: colour swatch column — left-click to assign a tab colour via `JColorChooser`, right-click to clear; colours saved/restored across sessions (`SUI.TABCOLOR.N`)
- Query Sheet Overview: sheet name column editable in-place (double-click to rename; propagated to the tab title)
- **Query Report** row count label at the bottom of every result window — "Rows: N" or "Rows: N (of M)" when a filter is active
- Connection Manager: drag-and-drop alias reordering in the connection list; ▲/▼ buttons as keyboard alternative
- Exec-Append dialog pre-selects the last-used URL and driver on open
- Auto-fills userid/password from session cache or connection profile when switching URL

### Sui 0.75N
---------
- New **SQL Dialect Converter** additions (DB2 → BigQuery): `DECIMAL`, `VARCHAR_FORMAT`, `MERGE INTO`, `NVL`, `NVL2`, `ZEROIFNULL`, `NULLIFZERO`, `DECODE`, `ADD_MONTHS`, `CHR`, `ASCII`, `TRUNCATE`, `MINUS → EXCEPT DISTINCT`
- SQL Dialect Converter: CTE `SELECT *` — column header list stripped and warned instead of left as invalid BigQuery syntax
- SQL Dialect Converter: `MERGE INTO target alias` → `MERGE target AS alias`; target alias de-qualified inside `UPDATE SET` block
- SQL Dialect Converter: DB2 date format tokens mapped to BigQuery strftime tokens for `VARCHAR_FORMAT`
- SQL Dialect Converter: warning bullet character encoding fixed (`â€¢` → `•`)
- "Convert SQL Dialect…" added to the **Options** menu
- Right-click menu reorganised — Format/Validate/Convert at top; file/table ops grouped; Edit ops at bottom; "Sheet Preferences" removed
- Inline directive `#URL=` — switches JDBC connection mid-script to any previously-connected URL (credentials resolved from session memory, no prompt)
- Inline directive `#SET KEY=VALUE` — new natural syntax alongside original `#SET= KEY VALUE` form
- Query Report title now shows the `#URL=` override URL instead of the URL-box URL
- Syntax highlighting: ~60 additional SQL keywords (JOIN, ON, NULL, IS, LIKE, BETWEEN, WITH, OVER, MERGE, LIMIT, EXCEPT, INTERSECT, and more; DDL: INDEX, VIEW, UNIQUE, PRIMARY KEY, FOREIGN, PROCEDURE, FUNCTION, TRIGGER, SEQUENCE; functions: NVL, TRIM, EXTRACT, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, CURRENT_DATE/TIME/TIMESTAMP, and more)
- Syntax highlighting: `/*` inside a `--` single-line comment no longer colours the rest of the document
- Syntax highlighting: scanning skipped when document exceeds 5 000 characters (performance); styles reset on every change to prevent colour bleeding when toggling off
- SQL Object Tree: schema expands into typed sub-folders — **Tables / Views / Aliases / Synonyms**; empty groups omitted; Routines group appended when "Include routines" is checked
- Excel export: numeric columns written as Excel numeric cells — decimals via `BigDecimal`, integers separately; configurable integer and decimal format strings
- Excel export: meta sheet now includes result set status (full/partial) and row count
- Excel export: font, integer format, and decimal format configurable in **Preferences → Export**
- Bug fix (ConnDB): BigQuery embedded `https://` URL no longer incorrectly stripped by `sanitizeUrl`
- Toolbar: Connection Manager button tooltip updated; action wired to `ConnManager` dialog

### Sui 0.75M
---------
- New **Connection Manager** dialog (`File → Connection Manager…`) — unified replacement for the old `connP` dialog
  - Left panel: named alias list with New, Copy, Remove buttons
  - Tab 1 (Connection): Alias, Driver combobox, Server, Port, Database/Project, SID, URL (auto-filled from template or directly editable), User, Password (Show/Hide), Auto-login, Test Connection
  - Tab 2 (Driver / JAR): global driver catalog with Name, Driver Class, JAR path, and live Status column (✔/✘); Browse JAR, Reload JARs buttons
  - Tab 3 (JDBC Properties): editable key/value table backed by `SuiConnPref.pro`
  - Password only written to disk when Auto-login is explicitly ticked
  - Auto-migrates legacy `connprop.pro` and old `SUI.JDBCURL.0.N` entries to new `SuiConnProp.pro` format on first Save
- URL selection in main panel auto-fills userid from the matching saved connection profile when the field is blank
- URL selection auto-fills password when the saved profile has `AUTOLOGIN=Y` and a non-empty saved password
- New **Keywords** tab in Preferences — editable 3-column table (Trigger / Expansion / Description) for F1 auto-completion shortcuts; saved to `SuiKeywProp.pro`
- Bundled `keyw.pro` in JAR — 30 default SQL keyword completions active on first run (no user file required)
- Keyword merge: bundled defaults are used as a base; user edits in `SuiKeywProp.pro` override matching triggers
- Bug fix (MariaDB): `ArrayIndexOutOfBoundsException` when port field is left blank — stray `:/` colon-slash stripped from JDBC URL before connecting

### Sui 0.75L
---------
- New `SqlDialectConverter` engine — DB2 ↔ BigQuery SQL translation (bidirectional)
- DB2 → BQ: strips `WITH UR/CS/RR/RS`, rewrites `CURRENT TIMESTAMP/DATE/TIME` → BQ equivalents, removes `SYSIBM.SYSDUMMY1` / `DUAL`, `FETCH FIRST n ROWS ONLY` → `LIMIT n`
- DB2 → BQ: interval arithmetic — `CURRENT TIMESTAMP - 7 DAYS` → `TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)` and `+` / `-` variants
- DB2 → BQ: function transforms — YEAR/MONTH/DAY/HOUR/MINUTE/SECOND → EXTRACT, CHAR/VARCHAR → CAST STRING, INTEGER/INT → CAST INT64, FLOAT/DOUBLE → CAST FLOAT64, STRIP → TRIM, LOCATE/POSSTR → STRPOS (args reversed)
- DB2 → BQ: CTE column-list push-down — inlines `(col, …)` aliases as `AS` clauses on SELECT items, removes the column list from the WITH clause
- BQ → DB2: backtick identifiers → double-quoted, splits `project.dataset.table` segments; CURRENT_TIMESTAMP()/DATE()/TIME() → DB2 special registers; STRPOS → LOCATE (args reversed), IF → CASE WHEN, IFNULL → COALESCE, TO_HEX → HEX, SAFE_CAST → CAST with warning
- New `ConvertSqlDialog` — "Convert SQL Dialect (experimental)": From/To combo (default DB2→BQ, combos enforce opposite selection), result + warnings areas, "Format using Extended Format SQL" checkbox, target schema field; settings persisted across invocations
- "Convert SQL Dialect…" added to query right-click popup
- Bug fix: Query History Viewer URL filter field was invisible on first open — width capped at 200 px
- Bug fix: Query History Viewer `NullPointerException` during filter navigation when history entry has no SQL text
- Bug fix: executing a query when not connected now shows "Query cannot be executed - not connected" instead of a `NullPointerException`

Sui 0.75K
---------
- SQL Object Tree: index sub-tree per table — Indexes folder with UNIQUE/NON-UNIQUE entries and column children; enabled by new "Include indexes" checkbox (left of "Include routines")
- Preferences → Start Up: "Include indexes in SQL Tree" checkbox — controls default checked state of the SQL Tree indexes checkbox
- SQL Object Tree right-click table: Count Rows (`COUNT_BIG(*)` for DB2, `COUNT(*)` otherwise)
- SQL Object Tree right-click table: List Referential Integrity (uses `getImportedKeys`)
- SQL Object Tree right-click column: Column Statistics — MIN, MAX, COUNT DISTINCT in one query
- SQL Object Tree right-click column: Sample Unique Values — `SELECT DISTINCT col` limited by Max Rows setting
- Bug fix: "Build SQL" no longer shows spurious "SQL opened in SQLBox" message
- ShowSQL right-click popup: "Exec. → Append" added
- "Exec. → Derby" replaced by "Exec. → SQLite" in query right-click popup; checks for SQLite JDBC driver in both system and Sui dynamic class loaders before opening
- New `CopyToSQLite` dialog: SQLite DB file path, table name, max rows, drop/re-create option; file path persisted between invocations
- `RunDerby` / `CreateDDL`: full SQLite support — schema-less `CREATE TABLE` / `DROP TABLE` / `INSERT INTO`; automatic table creation for SQLite URLs; inserting into an existing table without re-create no longer errors
- Bug fix: `setReadOnly(true)` on source connection silently ignored when driver rejects it mid-transaction (e.g. BigQuery → SQLite copy)
- Bug fix (Mimer): `AbstractMethodError` on `getFunctionColumns()` caught; falls back to `getProcedureColumns()`
- Bug fix (Mimer): dummy table corrected from `SYSTEM_ONEROW` to `SYSTEM.ONEROW`

Sui 0.75J
---------
- Preferences → Query: new Ext Format SQL panel — dialect, indent, uppercase, lines between queries, max column length, skip whitespace near parentheses, comma position (trailing/leading)
- Ext Format SQL: leading comma post-processing option moves trailing commas to the beginning of the next line
- SQL Editor: Trim Trailing Whitespace — Edit menu (Ctrl+Shift+X) and right-click menu
- SQL Object Tree right-click: "Additional Table Info" for DB2 (LUW and z/OS) and BigQuery
- SQL Object Tree right-click: "Table Space Information" for DB2 (LUW and z/OS, tables only)
- SQL Object Tree right-click: "View definition" for DB2 and BigQuery (view nodes only)
- SQL Object Tree: BigQuery table/column names now preserve original case (case-sensitive JDBC driver fix)
- Bug fix: F6 / F7 / F8 DB2 actions now correctly distinguish DB2 for z/OS from DB2 LUW
- Bug fix: BigQuery unbounded STRING columns no longer excluded from Query Report filter row
- Replaced dead `com.foundationdb:fdb-sql-parser` (2015) with `com.github.jsqlparser:jsqlparser:4.9` (Apache 2.0, actively maintained)
- Right-click menu: "Syntax Validate by Prepare" — validates selected SQL via the active JDBC connection (shown only when connected)
- Query History Viewer: every executed query now records a timestamp and connection URL (up to 9000 entries, configurable in Preferences → Query)
- Query History Viewer: URL filter combobox — browse history for a specific connection only
- Query History Viewer: AND/OR/IN advanced search syntax in the Find field
- Query History Viewer: status bar shows timestamp + URL for the current entry; tooltip summarises entry count and date range
- Preferences → Query: configurable variable substitution character (default `&`, e.g. `:` for JDBC-style) stored as `SUI.VARSUBS.CHAR`
- SQL Object Tree right-click table: "Generate DDL" — generates `CREATE TABLE` statement from database metadata including columns, types, defaults, NOT NULL and primary key constraint
- SQL Object Tree: "Include Stored Procedures" checkbox — when enabled, schemas show a Tables group and a Stored Procedures group
- SQL Object Tree right-click stored procedure: "Draw Stored Procedure (F9)" and "Execute Stored Procedure" (draw + run in one step)
- SQL Object Tree right-click function: "Draw Function" — inserts `SELECT schema.func(&p1, ?)` snippet using the configured substitution character
- SQL Object Tree: SP and Function nodes are draggable — drop on the query window generates the `{CALL …}` or `SELECT func(…)` snippet
- SQL Object Tree: "Build SQL to clipboard" renamed to "Build SQL"
- SQL Object Tree: "Include routines" checkbox (renamed from "Include Stored Procedures") — shows a Routines group per schema; default checked state set in Start Up preferences
- SQL Object Tree: BigQuery user-defined functions now loaded (via `getFunctions()`); function parameters fetched via `getFunctionColumns()`
- SQL Object Tree: Draw Function respects the "Draw SQL to SQLBox" preference
- ShowSQL dialog: right-click context menu (execute, format, copy, copy to query sheet)
- QueryBox Viewer: right-click context menu — same popup as ShowSQL
- Preferences → Misc: "Draw SQL to SQLBox" — Draw Insert, Draw SP, Draw Function and Build SQL open in a new SQLBox window instead of copying to clipboard
- Preferences → Start Up: "Include routines in SQL Tree" — controls default checked state of the SQL Tree routines checkbox
- Toolbar: Query File Tree button icon replaced with OS-native folder icon at correct 16×16 size (was an oversized 26×26 `pages.gif`)

Sui 0.75G
---------
- Toggle Comment on selected lines (Ctrl+7)
- Go to Line dialog (Ctrl+G)
- Block Indent / Unindent (Tab / Shift+Tab with selection)
- Uppercase / Lowercase Selection (Ctrl+Shift+U / Ctrl+Shift+L)
- Parenthesis matching highlight — enable/disable from right-click menu
- Cursor position indicator (Ln / Col) displayed above query tabs
- SQL Object Tree: Schema / Table filter fields with titled border
- SQL Object Tree: Better icons — table grid for SQL Tree, pages for Query Tree toolbar buttons
- SQL Object Tree: Frame icon switches between `db.gif` (SQL tree) and `pages.gif` (file tree)
- Query Editor popup: "Build IN List from Selection" — converts selected values to SQL `IN (…)` clause
- Query Editor popup: "Copy Columns from Selection…" — extracts fixed-position column range to clipboard
- Query Report popup: "Copy WHERE clause from row" — builds `WHERE col = val AND …` from the selected row
- Bug fix: Status message not cleared before showing "Columns copied to clipboard"

Sui 0.75F
---------
- New `SQLTreePanel` — lazy-loading JTree of schemas → tables → columns
- Toolbar buttons to show SQL Object Tree / Query File Tree
- Right-click table node: "Build SQL to clipboard", "Draw SQL (SELECT)", "Draw SQL (INSERT)"
- Drag table node to query window — choose `schema.table` or full `SELECT` statement
- Drag column node to query window — inserts column name at caret
- DB2: SQLCODE -4471 resolved — `conn.commit()` added after every metadata `ResultSet` close
- DB2: System schemas (SYSIBM, SYSCAT, SYSSTAT, etc.) filtered from tree
- DB2: `getColumns()` called with `null` column-name pattern instead of `%` wildcard
- BigQuery: OAuth connection cache preserved — `closeConn()` is a no-op for BigQuery
- BigQuery: Schema list filtered to current project only (extracted from JDBC URL `ProjectId=`)
- BigQuery: `project.dataset` schema name prefix stripped before `getTables()` call
- Mimer SQL: Tables now load — `null` catalog and `null` table-type filter used in `getTables()`
- Mimer SQL: Schema name uppercased for Mimer and DB2 before metadata calls

Sui 0.75C
---------
- Fixed decimal precision for NUMERIC/DECIMAL columns in query results panel and CSV export
- Fixed compilation error in "Send query to" mail feature (java.awt.Desktop name clash)

Sui 0.75B
---------
- Security fix: command injection vulnerability in "Send query to" mail feature eliminated
- DatabaseManager now delegates to ConnDB, ensuring SuiConnPref.pro properties (including BigQuery OAuth settings) are always applied
- Connection and classpath preferences now saved immediately when the preferences dialog is closed, not only at application shutdown
- Fixed file-handle leak in profile store (StoreProf)
- Added credential handling documentation (docs/CredentialHandling.md)

Sui 0.75A
---------
- BigQuery connections now kept in a cache with a 10-hour TTL, reducing repeated connection overhead
- Row limit enforced for BigQuery result sets to prevent runaway memory use
- All cached connections are closed gracefully at application exit
- DConnInf completely rewritten — now displays approximately 80 JDBC metadata properties
- Fixed compatibility issues with older JDBC drivers (AbstractMethodError, Mimer SQLException)
- Improved thread safety: all 7 `.pro` file save methods are now synchronized
- Fixed Garabage background thread (interrupt handling, dead code removal)
- Build version and timestamp are now baked into the jar and shown in the About dialog
- New DatabaseManager helper class added
- All image assets moved to `src/imgs/` subfolder
- Unused source files moved to `src/unused/`
- Updated POM dependencies to remove known security vulnerabilities
- Added new documentation: USAGE.md and several docs/ files

Sui 0.74
------
- New Option to blank out password, when a new not previously not connected URL is selected (Misc properties 
  set PW Blank is not connected
- Added function to customize lookandFeel, added Flatlaf Sample Sui.ini to use a black theme:   
 SuiHome=c:\SuiDev;                          
 font=consolas,13;                           
 pyjamas=false;                              
 LookandFeel=com.formdev.flatlaf.FlatDarkLaf;
- New function to format/Make a JSON string readable from 


Sui 0.73

Version 0.73 up to 0.73K
------------
- Added function to mark SQL at cursor (based on usage of Semicolon as delimiter) (Shift f1)
  Example : Place cursor att the second row and press Shift-F1, SELECT * FROM SYSIBM.SYSCOLUMNS is marked.
- Added function to execute SQL at cursor (based on usage of Semicolon as delimiter) (Shift f2)
- Corrected some issues in Export Excel
- Added DB2 specific functions to list columns (F6) and Tablespace (F7)
- Improved handling using the SuiConnPref.pro file
- Changed the syntax for include statement, the syntax is now:
<include>c:\folder\file</include>  (Where c:\folder\file is a fully qualified file name)
- Changed source for extended Format SQL to make it generally available
- Removed built in support for Derby
- Did some cleanup in Find-Replace logic

Version 0.73L
-------------
- Made it possible to only execute marked SQL from query box
- Made it possible to run SQL and get result directly to Excel from query box
- Built function to search for text strings in Sheets Version (querysheetviewer) right click and query window and select from list)
- Added F8 option to list content of View only avaialable for DB2 in same way as F6 to list columns and F7 to List tablespace)
- Made it possible to use variable when setting suihome variabeln for SuiConnPref
- Made it possible to use variable when setting suihome for SuiCPProp
- Fixed nullpointer eception in startup when deleteing temp datasets
- Added confirm dialog for delete from file tree

