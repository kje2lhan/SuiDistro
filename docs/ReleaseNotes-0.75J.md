# Release Notes — Sui 0.75J

**Branch:** `Sui0.75J`  
**Base:** `Sui 0.75G` (SQL Editor enhancements / SQL Object Tree)  
**Date:** 2026-05-01 / 2026-05-02  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Preferences → Query | New feature | SQL formatter options panel (Ext Format SQL / FormSQL2) |
| Ext Format SQL | Enhancement | All 6 FormatConfig options read from preferences |
| Ext Format SQL | New feature | Leading comma option (post-processing) |
| SQL Editor | New feature | Trim Trailing Whitespace — Edit menu (Ctrl+Shift+X) and right-click |
| SQL Object Tree | New feature | Right-click → Additional Table Info (DB2 and BigQuery) |
| SQL Object Tree | New feature | Right-click → Table Space Information (DB2 only) |
| SQL Object Tree | New feature | Right-click → View definition (DB2 and BigQuery) |
| SQL Object Tree | Bug fix | BigQuery: table/column names now preserve original case |
| SQL Object Tree | Bug fix | F6 / F7 / F8 DB2 key actions now handle DB2 for z/OS vs LUW differences |
| SQL Object Tree | New feature | Right-click → DDL Generation (CREATE TABLE from metadata) |
| SQL Object Tree | New feature | Stored Procedures and Functions in schema tree (opt-in checkbox) |
| SQL Object Tree | New feature | Right-click SP → Draw Stored Procedure / Execute Stored Procedure |
| SQL Object Tree | New feature | Right-click Function → Draw Function (SELECT snippet with substitution vars) |
| SQL Object Tree | New feature | Drag SP/Function to query window → generates CALL / SELECT snippet |
| SQL Object Tree | Enhancement | "Build SQL to clipboard" renamed to "Build SQL" |
| SQL Object Tree | Bug fix | BigQuery: user-defined functions now loaded via `getFunctions()` (were missing from `getProcedures()`) |
| SQL Object Tree | Bug fix | BigQuery: function parameters now fetched via `getFunctionColumns()` |
| SQL Object Tree | Enhancement | "Include Stored Procedures" checkbox and group label renamed to "Include routines" / "Routines" |
| SQL Object Tree | New feature | Draw Function respects "Draw SQL to SQLBox" preference |
| ShowSQL | New feature | Right-click context menu — execute, format, copy, paste, copy to query sheet |
| ShowQryBox Viewer | New feature | Right-click context menu — same reduced popup as ShowSQL |
| Preferences → Start Up | New feature | "Include routines in SQL Tree" — sets default checked state of the SQL Tree routines checkbox |
| Preferences → Misc | New feature | "Draw SQL to SQLBox" — Draw Insert / Draw SP / Draw Function / Build SQL open in new SQLBox |
| Query History Viewer | New feature | Timestamp and URL recorded for every executed query (up to 9000 entries) |
| Query History Viewer | New feature | URL filter combobox — browse history for a specific connection |
| Query History Viewer | New feature | AND/OR/IN advanced search logic in the Find field |
| Query History Viewer | New feature | Status bar shows timestamp + URL for the currently displayed query |
| Query History Viewer | New feature | History summary tooltip (entry count, newest/oldest timestamp) |
| Query History Viewer | New feature | Configurable max history size (10–9000) in Preferences → Query |
| Preferences → Query | New feature | Configurable variable substitution character (default `&`, e.g. change to `:` for JDBC-style) |
| Query Report | Bug fix | BigQuery unbounded STRING columns no longer excluded from filter |
| Syntax Validate | Enhancement | Replaced dead `fdb-sql-parser` (2015) with JSqlParser (Apache 2.0) |
| Syntax Validate | New feature | "Syntax Validate by Prepare" in right-click menu when connected |
| Dependencies | Maintenance | `com.foundationdb:fdb-sql-parser` → `com.github.jsqlparser:jsqlparser:4.9` |
| Toolbar | Bug fix | Query File Tree button: replaced 26×26 `pages.gif` with OS folder icon at 16×16 |

---

## Detailed Changes by Area

---

### Preferences → Query Tab — Ext Format SQL Options

A new **Ext Format SQL** section has been added to the **Preferences → Query** tab
(`PropmSQL.java`). It exposes all six configuration options of the
`com.github.vertical-blank:sql-formatter` library used by the **Ext Format SQL**
right-click action.

All settings are stored in `SuiSys.pro` under the `SUI.FMT2.*` key namespace and
read by `FormSQL2.java` at format time.

#### Controls added

| Label | Control | Property key | Default |
|---|---|---|---|
| Dialect | `JComboBox` (db2, mysql, mariadb, postgresql, sqlite, tsql, spark, bigquery, hive, plsql, n1ql, singlestoredb, trino) | `SUI.FMT2.DIALECT` | `db2` |
| Indent spaces | `JSpinner` (0 – 5) | `SUI.FMT2.INDENT` | `2` |
| Uppercase keywords | `JCheckBox` | `SUI.FMT2.UPPERCASE` | off |
| Lines between queries | `JTextField` (non-negative integer, `NonNegIntFilter`) | `SUI.FMT2.LINESBETWEEN` | `1` |
| Max column length | `JTextField` (non-negative integer, `NonNegIntFilter`) | `SUI.FMT2.MAXCOLLEN` | `50` |
| Skip whitespace near block parentheses | `JCheckBox` | `SUI.FMT2.SKIPWSNEARPARENS` | off |
| Comma position | `JComboBox` (Trailing (default), Leading) | `SUI.FMT2.COMMAPOS` | `Trailing (default)` |

#### Layout

The existing upper controls and the new Ext Format SQL block are merged into a single
`GridBagLayout` panel with a `JSeparator` section header row between them. A spacer
column at `gridx=2` with `weightx=1.0` centres the two-column form in the available width.

Input validation runs at save time (`AppPropmSQL()`):
- Indent: `JSpinner` range 0–5 prevents invalid values at entry.
- Lines between / Max column length: non-negative integer filter on the text field;
  out-of-range values revert to the stored value with a `JOptionPane` warning.

#### Dialog size

`PropmAll.java` — `setSize` height increased from `400` to `580` to accommodate
the new rows without clipping.

---

### Ext Format SQL — Leading Comma Option

When **Comma position = Leading** is selected, `FormSQL2.java` applies a post-processing
pass (`applyLeadingCommas()`) after the formatter runs.

The pass strips the trailing comma from each line and places it one character to the
left of the indent of the following line:

```
-- Trailing (default):        -- Leading:
SELECT                        SELECT
    col1,                         col1
    col2,                        ,col2
    col3                         ,col3
FROM t                        FROM t
```

The implementation splits on `\n`, walks line-pairs, and shifts the comma without
adding a space after it.

---

### SQL Editor — Trim Trailing Whitespace

**Menu item:** Edit → Trim Trailing Whitespace  
**Keyboard shortcut:** Ctrl+Shift+X  
**Right-click menu:** yes (after "Remove Initial numerics from SQL")

Removes trailing spaces and tabs from every line in the query editor without
disturbing the content of quoted string literals.

---

### SQL Object Tree — Right-click Context Menu Additions

Three new items appear in the right-click popup on a table or view node in the
SQL Object Tree. The items are shown only for the databases that support them.

#### Additional Table Info

**Databases:** DB2 (LUW and z/OS), BigQuery  
**Availability:** tables and views

Runs a query against the system catalogue to retrieve detailed column metadata,
matching the information shown by the existing **F6** action in the main query panel.

| Database | Source table |
|---|---|
| DB2 LUW | `SYSIBM.SYSCOLUMNS` |
| DB2 z/OS | `SYSIBM.SYSCOLUMNS` (adds `DEFAULTVALUE` column) |
| BigQuery | `<dataset>.INFORMATION_SCHEMA.COLUMNS` |

#### Table Space Information

**Databases:** DB2 (LUW and z/OS)  
**Availability:** base tables only (not views)

Queries tablespace metadata for the selected table, matching the **F7** action.

| Database | Source |
|---|---|
| DB2 z/OS | `SYSIBM.SYSTABLESPACE` joined to `SYSIBM.SYSTABLES` |
| DB2 LUW | `SYSCAT.TABLESPACES` joined to `SYSCAT.TABLES` |

#### View definition

**Databases:** DB2, BigQuery  
**Availability:** view nodes only

Retrieves the view definition text.

| Database | Source |
|---|---|
| DB2 | `SYSIBM.SYSVIEWS` |
| BigQuery | `<dataset>.INFORMATION_SCHEMA.VIEWS` |

---

### SQL Object Tree — BigQuery Case Sensitivity Fix

When the active connection is BigQuery, `SQLTreePanel` now preserves the original
case of schema and table names when populating the global `Sui.schema` / `Sui.TbNm`
fields used by subsequent queries. Previously names were forced to uppercase, which
caused all catalogue queries against BigQuery to fail since BigQuery identifiers
are case-sensitive in the Simba JDBC driver.

---

### SQL Object Tree — DB2 z/OS / LUW Compatibility Fix (F6, F7, F8)

The `Additional Table Info`, `Table Space Information`, and `View definition`
actions (both from the tree context menu and the existing F6/F7/F8 keyboard
shortcuts in `Sui.java`) now detect whether the connected DB2 instance is
**z/OS** or **LUW** by inspecting `DatabaseMetaData.getDatabaseProductVersion()`:

- z/OS versions begin with `DSN`.
- Detection is done once per action invocation via a lightweight metadata call.
- DB2 z/OS uses `SYSIBM.SYSTABLESPACE`; DB2 LUW uses `SYSCAT.TABLESPACES`.
- The `DEFAULTVALUE` column in `SYSIBM.SYSCOLUMNS` is included only on z/OS
  (LUW exposes it differently and the column does not exist in the same form).

---

### Query Report — BigQuery STRING Filter Fix

`QueryRep.java` — the column-width guard that excluded columns with
`displaySize > 500` from the filter row was incorrectly excluding BigQuery
`STRING` columns, which report `Integer.MAX_VALUE` as their display size.

The guard now skips the length check for `String`-typed columns; only non-String
columns with a display size over 500 (and non-zero) are excluded.

---

### Syntax Validate — JSqlParser Replacement

The `com.foundationdb:fdb-sql-parser` library (last released 2015, archived) has
been replaced with `com.github.jsqlparser:jsqlparser:4.9` (Apache 2.0, actively
maintained).

`TableSplitter.java` was rewritten:

| Before | After |
|---|---|
| ~160 lines including two inner `Visitor` classes | ~45 lines |
| `SQLParser.parseStatements()` + manual AST walk | `CCJSqlParserUtil.parseStatements()` |
| `TableFinder` inner class (manual `FromBaseTable` walk) | `TablesNamesFinder.getTableList()` (built-in) |
| `TableKeeper` inner class (AST mutation, result unused) | removed — was dead code |
| Catches `StandardException` | Catches `JSQLParserException` (includes position info) |

The **Syntax Validate** right-click menu item behaviour is unchanged.

---

### Syntax Validate by Prepare — New Right-click Option

**Menu item:** "Syntax Validate by Prepare"  
**Availability:** only shown in the right-click menu when Sui is in connected state

When selected, the currently selected SQL text is validated by submitting it to
the active JDBC connection via `prepareStatement()`. The database engine's own
parser is used — making the check dialect-aware by definition.

- If nothing is selected an error message is shown immediately.
- The connection is opened and closed within the call (same pattern as `RunIt`).
- DB2-specific error codes are decoded via `DB2SQLCA` for clearer messages.
- Note: DB2's `prepareStatement` performs limited validation for `SELECT`
  statements (syntax errors are caught; unresolved table/column names may not be).
  DML statements (INSERT / UPDATE / DELETE) are validated more thoroughly.

**Implementation:** `TableSplitter.validateByPrepare()` — `DatabaseManager` is used
to obtain the connection; `QryPop` adds the item conditionally via `Sui.IsConnect()`.

---

## Changes — 2026-05-02

| Area | Type | Description |
|---|---|---|
| SQL Object Tree | New feature | DDL Generation — right-click table → `CREATE TABLE` statement |
| SQL Object Tree | New feature | Stored Procedures and Functions shown in schema tree (opt-in checkbox) |
| SQL Object Tree | New feature | Right-click SP → Draw Stored Procedure (F9 equivalent) |
| SQL Object Tree | New feature | Right-click SP → Execute Stored Procedure (draw + run in one step) |
| SQL Object Tree | New feature | Right-click Function → Draw Function (SELECT snippet with substitution vars) |
| SQL Object Tree | New feature | Drag SP to query window → generates `{CALL …}` statement |
| SQL Object Tree | New feature | Drag Function to query window → generates `SELECT func(…)` snippet |
| SQL Object Tree | Enhancement | Mimer SQL: function SELECT uses `FROM SYSTEM.ONEROW` instead of `FROM SYSIBM.SYSDUMMY1` |
| SQL Object Tree | Enhancement | "Build SQL to clipboard" renamed to "Build SQL" |
| SQL Object Tree | Bug fix | BigQuery: user-defined functions now loaded via `getFunctions()` |
| SQL Object Tree | Bug fix | BigQuery: function parameters fetched via `getFunctionColumns()` |
| SQL Object Tree | Enhancement | "Include Stored Procedures" checkbox and group label renamed to "Include routines" / "Routines" |
| SQL Object Tree | New feature | Draw Function respects "Draw SQL to SQLBox" preference |
| ShowSQL | New feature | Right-click context menu (execute, format, copy, copy to query sheet) |
| ShowQryBox Viewer | New feature | Right-click context menu (same popup as ShowSQL) |
| Preferences → Start Up | New feature | "Include routines in SQL Tree" default-state checkbox |
| Preferences → Misc | New feature | "Draw SQL to SQLBox" — generated SQL opens in new SQLBox instead of clipboard |
| Toolbar | Bug fix | Query File Tree button icon replaced: was 26×26 `pages.gif`, now OS folder icon at 16×16 |

---

### Query History Viewer — Enhancements

The **Query History Viewer** (`ShowQryBox`) received a significant set of enhancements
to make browsing and searching query history practical with large history sizes.

#### Timestamp and URL recording

Every query executed via `RunQry()` is now recorded with:
- **Timestamp** — `yyyy-MM-dd HH:mm:ss` captured at execution time.
- **Connection URL** — the active JDBC URL at the time of execution.

Both are stored in `SuiSys.pro` under `SUI.QUERYTIMESTAMP.n` and `SUI.QUERYURL.n` keys,
persisted and restored across sessions alongside the existing query text.

Storage capacity is configurable (see below). Arrays are pre-allocated to 9000 slots as
the hard maximum.

#### URL filter combobox

A **URL** combobox is shown in the filter bar of the QueryBox viewer. It is populated
with all distinct URLs present in the history, plus `*` (match all). Selecting a specific
URL limits Next/Previous navigation and search to queries executed against that connection.

#### Advanced AND/OR/IN search

The existing Find field gains an **AND/OR** checkbox. When checked, the filter text
supports three syntaxes:

| Syntax | Matches when… |
|---|---|
| `Apple AND Orange` | query text contains both terms |
| `Apple OR Orange` | query text contains either term |
| `IN (Apple, Orange, Pear)` | query text contains any of the listed terms |

When the checkbox is off, the original plain substring match is used.

#### Status bar — timestamp and URL

A sunken status bar is shown at the bottom of the viewer window. While browsing, it
displays the **timestamp** and **URL** for the currently visible query entry:

```
2026-05-01 14:32:10   |   jdbc:db2://myhost:50000/MYDB
```

#### History summary tooltip

Hovering over the status bar label shows a tooltip summarising the full history:

```
Entries: 847
Newest: 2026-05-02 11:44:05
Oldest: 2026-04-01 09:12:33
```

#### Configurable max history size

A **"Max query history"** field has been added to **Preferences → Query** (`PropmSQL.java`).
Accepted range: 10–9000. The setting is stored as `SUI.QHIST.MAXSIZE` in `SuiSys.pro`.
`saveBox()` in `Sui.java` reads this value at save time so the effective limit is applied
immediately without a restart.

---

### Preferences → Query — Configurable Variable Substitution Character

The **Preferences → Query** tab (`PropmSQL.java`) already had a **Variable Substitution**
checkbox (`SUI.VARSUBS`). A new single-character text field next to it now lets the user
choose **which character** is used as the substitution prefix.

| Control | Property key | Default |
|---|---|---|
| Substitution char (1-char field) | `SUI.VARSUBS.CHAR` | `&` |

The field enforces a maximum of one character via a `DocumentFilter`. Saving an empty
field reverts to `&`.

The configured character is used consistently everywhere Sui generates parameterised SQL:
- **Draw SQL (INSERT)** — `RunIt.BldStmt()` for `dt=INS`
- **Draw Stored Procedure** — `RunIt.BldStmt()` for `dt=SP` (IN parameters)
- **Draw Function** — `SQLTreePanel.insertFunctionSelect()` (IN parameters)
- **Drag SP / Drag Function** — same paths as above

This allows users who prefer JDBC-style named parameters (`:paramname`) or other
conventions to generate ready-to-use SQL without manual editing.

---

### DDL Generation

**`CreateDDL.CreateTBLDDLFromMeta(Connection, catalog, schema, table)`** — new method
that builds a `CREATE TABLE` statement from `DatabaseMetaData.getColumns()` and
`DatabaseMetaData.getPrimaryKeys()`. Handles column types (Oracle `NUMBER`/`VARCHAR2`,
Derby `CHAR` cap, `DECIMAL`/`NUMERIC` with precision/scale, all common no-length types),
`DEFAULT` values, `NOT NULL` constraints, and a `CONSTRAINT PK_table PRIMARY KEY (…)` clause.
Also sets `DropStmt` to the corresponding `DROP TABLE` statement.

**`SQLTreePanel`** — right-click on a base table node now includes **"Generate DDL"**.
The generated DDL is shown in a `ShowSQL` dialog. Not available for views.

---

### Stored Procedures and Functions in the SQL Object Tree

A new **"Include Stored Procedures"** checkbox in the SQL Object Tree filter panel
controls whether SPs and Functions are loaded. When checked, expanding a schema node
shows two group sub-nodes: **Tables** and **Stored Procedures**.

#### Loading

- `loadStoredProcs()` calls `DatabaseMetaData.getProcedures()`. The `PROCEDURE_TYPE`
  column determines whether each entry is a `PROCEDURE` or `FUNCTION`. Overload
  suffixes (`;N` appended by some drivers) are stripped.
- `loadProcedureParams()` calls `DatabaseMetaData.getProcedureColumns()` and stores
  direction (`IN` / `OUT` / `INOUT` / `RETURN`) + type in the node's `extra` field.
- **BigQuery:** `effectiveCatalog = projectId` (same pattern as table loading). SP and
  dataset names are case-sensitive and are never uppercased.

#### Right-click context menu — Procedure nodes

| Item | Action |
|---|---|
| Draw Stored Procedure (F9) | Sets `Sui.SPNm` + schema, `dt=SP`, `dst=Q`, runs `RunSql(null,"0")` — same as pressing F9 from the query window. Pastes the generated `{CALL …}` statement into the query area. |
| Execute Stored Procedure | Same as Draw but `dst=E` — draw + immediately run (`RunQry("S")`) in a single `SwingUtilities.invokeLater` call. |

#### Right-click context menu — Function nodes

| Item | Action |
|---|---|
| Draw Function | Builds `SELECT [schema.]funcname(&p1, &p2, ?)` using the configured substitution character for `IN` parameters and `?` for `OUT`/`INOUT`. Appends `FROM sysibm.sysdummy1` for DB2 or `FROM SYSTEM.ONEROW` for Mimer. Uses cached params if the node was already expanded; otherwise fetches via `getProcedureColumns()` on a background thread. |

---

### Drag-and-Drop for SP and Function Nodes

SP and Function nodes (`TYPE_SP`) are now draggable alongside the existing
Table and Column drag support.

**Drop on the query text area:**
- **Procedure node** — calls `drawStoredProc()`, generating and pasting the `{CALL …}` statement.
- **Function node** — calls `drawFunction()`, generating and inserting the `SELECT func(…)` snippet.

No dialog is shown (unlike the Table drag which prompts for `schema.table` vs `SELECT`).
Params are read from already-loaded tree children where available; otherwise fetched
from `DatabaseMetaData.getProcedureColumns()` on a background thread.

---

### Toolbar — Query File Tree Icon Fix

The **Show Query File Tree** toolbar button was using `imgs/pages.gif` (26×26 pixels),
making it visually larger than all other toolbar icons (16×16 PNG).

The icon is now generated at startup by `SuiTb.scaledFolderIcon(16)`:
- Fetches `UIManager.getIcon("FileView.directoryIcon")` — the OS-native folder icon,
  which matches the Windows Explorer folder appearance requested.
- Renders it into a 16×16 `BufferedImage` using bicubic interpolation.
- Returns an `ImageIcon` at the correct size, consistent with all other toolbar buttons.

---

### ShowSQL and ShowQryBox Viewer — Right-click Context Menu

Both the **ShowSQL** dialog (used for view definitions, DDL, generated SQL) and the
**QueryBox Viewer** (`ShowQryBox`) now have a right-click context menu.

A new third constructor `QryPop(JTextArea source)` was added to `QryPop.java`. Unlike
the existing constructors (which operate on the main query area `Sui.getTextArea()`),
this variant operates directly on the supplied `JTextArea`.

The reduced menu contains:

| Item | Notes |
|---|---|
| Execute query | Runs the text area content as a query |
| Exec → XLS | Runs and exports to Excel |
| Exec → CSV | Runs and exports to CSV |
| *(separator)* | |
| Format SQL | Standard SQL formatter |
| Ext Format SQL | Extended formatter (FormSQL2) |
| Syntax Validate | JSqlParser validation |
| Syntax Validate by Prepare | Via active JDBC connection (shown only when connected) |
| Trim Trailing Whitespace | |
| *(separator)* | |
| Copy | |
| Cut | (only if editable) |
| Paste | (only if editable) |
| *(separator)* | |
| Copy to query sheet | Shows a confirmation dialog, then calls `Sui.setSQL(source.getText())` |

**Implementation:** `ShowSQL.java` and `ShowQryBox.java` each add a `MouseAdapter` on
their text area that triggers `new QryPop(textArea).show(…)` on both `mousePressed` and
`mouseReleased` popup trigger events.

---

### Preferences → Misc — Draw SQL to SQLBox

A new **"Draw SQL to SQLBox"** checkbox has been added to the **Misc. Preferences** panel
(`PropmMisc.java`). Property key: `SUI.DRAW.SQLBOX` (default `N`).

When checked, the following "Draw" actions open the generated SQL in a new **SQLBox**
(`ShowSQL` window with `Exec=true`) instead of copying to the clipboard or pasting into
the main query area:

| Action | Source |
|---|---|
| Draw Insert | `RunIt.BldStmt()` — `dt=INS` branch |
| Draw Stored Procedure | `RunIt.BldStmt()` — `dt=SP` branch |
| Build SQL | `SQLTreePanel.copySelectToClipboard()` |
| Draw Function | `SQLTreePanel.insertFunctionSelect()` |

This gives users the option to review generated SQL in a separate, independently
executable window before committing it to the main query editor.

---

### BigQuery — User-defined Functions in SQL Object Tree

#### Functions not returned by `getProcedures()`

`loadStoredProcs()` in `SQLTreePanel.java` now calls `DatabaseMetaData.getFunctions()`
in addition to `getProcedures()` when the active connection is BigQuery.

Background:
- BigQuery's Simba JDBC driver does not return user-defined functions from
  `getProcedures()` — only the `getFunctions()` call exposes them.
- DB2 and Mimer return functions from `getProcedures()` with `PROCEDURE_TYPE = 2`
  (procedureReturnsResult), so no change was needed for those databases.
- A duplicate-check (`procs.stream().anyMatch(p -> p.name.equalsIgnoreCase(fn))`) prevents
  the same name appearing twice if a driver ever returns it from both calls.
- Functions loaded via `getFunctions()` have `NodeInfo.extra = "FUNCTION"` so downstream
  code can distinguish them from procedures.

#### Function parameters not loaded (`getFunctionColumns`)

`loadProcedureParams()` previously called `DatabaseMetaData.getProcedureColumns()` for all
nodes. For functions loaded via `getFunctions()`, this returns no rows on BigQuery.

Both `loadProcedureParams()` and the background fetch inside `drawFunction()` now detect
`"FUNCTION".equalsIgnoreCase(spInfo.extra)` and call `DatabaseMetaData.getFunctionColumns()`
instead, mapping column types via the `functionColumnIn / Out / InOut / Return` constants.

---

### SQL Object Tree — "Include routines" Rename and Startup Preference

#### Rename

The **"Include Stored Procedures"** checkbox in the SQL Object Tree filter panel has
been renamed to **"Include routines"**. The corresponding tree group node that appears
under each schema has been renamed from **"Stored Procedures"** to **"Routines"**, and
the empty-state placeholder from `(no stored procedures)` to `(no routines)`.

#### Startup default preference

A new **"Include routines in SQL Tree"** checkbox has been added to the
**Start Up → General Startup Preferences** panel (`PropmLogin.java`).
Property key: `SUI.INCLUDE.ROUTINES` (default `N`).

When saved, this value is read by `SQLTreePanel` at construction time to set the
initial checked state of the "Include routines" checkbox — so users who always want
routines visible do not need to re-check the box every session.
