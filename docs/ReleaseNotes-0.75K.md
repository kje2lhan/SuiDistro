# Release Notes — Sui 0.75K

**Branch:** `0.75K`  
**Base:** `Sui 0.75J` (SQL Object Tree / Query History / ShowSQL enhancements)  
**Date:** 2026-05-03  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| SQL Object Tree | New feature | Index sub-tree per table — TYPE_INDEX_GROUP / TYPE_INDEX / TYPE_INDEX_COL nodes |
| SQL Object Tree | New feature | "Include indexes" checkbox in the filter row (left of "Include routines") |
| SQL Object Tree | New feature | Right-click table → Count Rows (`COUNT_BIG(*)` for DB2, `COUNT(*)` otherwise) |
| SQL Object Tree | New feature | Right-click table → List Referential Integrity (uses `getImportedKeys`) |
| SQL Object Tree | New feature | Right-click column → Column Statistics (MIN, MAX, COUNT DISTINCT) |
| SQL Object Tree | New feature | Right-click column → Sample Unique Values (respects Max Rows setting) |
| SQL Object Tree | Bug fix | "Build SQL" no longer shows spurious "SQL opened in SQLBox" message |
| Preferences → Start Up | New feature | "Include indexes in SQL Tree" checkbox — sets default for the SQL Tree indexes checkbox |
| ShowSQL / QryPop | New feature | "Exec. → Append" added to ShowSQL right-click popup |
| Copy to SQLite | New feature | "Exec. → SQLite" replaces "Exec. → Derby" in query right-click popup |
| Copy to SQLite | New feature | SQLite jar availability check before opening dialog (searches system and dynamic class loaders) |
| Copy to SQLite | New feature | New `CopyToSQLite` dialog (file path, table name, max rows, drop/re-create) |
| Copy to SQLite | New feature | File path persisted between invocations (`SQLITEFILE` tmp property) |
| RunDerby | Enhancement | SQLite URLs automatically enable table creation (`Create = true`) |
| RunDerby | Enhancement | Inserting into an existing table without re-create no longer throws "already exists" error |
| RunDerby | Bug fix | `setReadOnly(true)` on source connection silently ignored when driver rejects it mid-transaction (e.g. BigQuery) |
| DDL Generation | Enhancement | `CREATE TABLE` / `DROP TABLE` / `INSERT INTO` omit schema prefix when schema is empty (SQLite compatibility) |
| Mimer SQL | Bug fix | `AbstractMethodError` on `getFunctionColumns()` caught; falls back to `getProcedureColumns()` |
| Mimer SQL | Bug fix | Dummy table corrected from `SYSTEM_ONEROW` to `SYSTEM.ONEROW` |

---

## Detailed Changes by Area

---

### SQL Object Tree — Index Sub-Tree

When **Include indexes** is checked, each table node gains an **Indexes** folder child
after its columns are loaded. Expanding the folder is a no-op (indexes are loaded
eagerly when the table expands). Each index entry shows `[UNIQUE]` or `[NON-UNIQUE]`
and expands to its constituent column names.

Three new internal node-type constants are used:

| Constant | Value | Rendered as |
|---|---|---|
| `TYPE_INDEX_GROUP` | `"INDEX_GROUP"` | Folder icon, bold label "Indexes" |
| `TYPE_INDEX` | `"INDEX"` | File icon, italic |
| `TYPE_INDEX_COL` | `"INDEX_COL"` | No icon, italic |

Index data is loaded via a `SwingWorker` using `DatabaseMetaData.getIndexInfo(false, false)`.
Indexes are grouped by `INDEX_NAME`; the `NON_UNIQUE` flag determines the label suffix.

---

### SQL Object Tree — Include Indexes Checkbox

A checkbox **Include indexes** has been added to the SQL Tree filter row at position
`gridx=0` in the third row of the 3×2 grid, placing it to the left of the existing
**Include routines** checkbox. Its checked state is initialised from the
`SUI.INCLUDE.INDEXES` property (default `"N"`).

---

### SQL Object Tree — Count Rows

Right-click a table node → **Count Rows** executes:

```sql
-- DB2:
SELECT COUNT_BIG(*) AS ROW_COUNT FROM schema.table

-- All other databases:
SELECT COUNT(*) AS ROW_COUNT FROM schema.table
```

The result opens in the normal query result panel.

---

### SQL Object Tree — List Referential Integrity

Right-click a table node → **List Referential Integrity** sets the active schema and
table in Sui and calls `RunSql(null, "R")` which triggers `getImportedKeys` via `RunIt`.

---

### SQL Object Tree — Column Statistics

Right-click a column node → **Column Statistics** executes:

```sql
SELECT MIN(col) AS MIN_VALUE,
       MAX(col) AS MAX_VALUE,
       COUNT(DISTINCT col) AS DISTINCT_COUNT
FROM schema.table
```

`COUNT_BIG(DISTINCT col)` is used for DB2. The result opens in the query result panel.

---

### SQL Object Tree — Sample Unique Values

Right-click a column node → **Sample Unique Values** executes:

```sql
-- DB2:
SELECT DISTINCT col FROM schema.table FETCH FIRST n ROWS ONLY

-- BigQuery / others with LIMIT:
SELECT DISTINCT col FROM schema.table LIMIT n
```

where `n` is the current Max Rows setting.

---

### SQL Object Tree — Build SQL Message Removed

`copySelectToClipboard()` no longer shows the "SQL is opened in SQLBox" message when
the "Draw SQL to SQLBox" preference is off. Only the clipboard confirmation message
is shown.

---

### Preferences → Start Up — Include Indexes

A new **Include indexes in SQL Tree** checkbox (`ChIncludeIndexes`) has been added to
the Start Up preferences panel at `gridy=6, gridx=1`, to the right of the existing
**Include routines in SQL Tree** checkbox. Its state is saved as `SUI.INCLUDE.INDEXES`
(`"Y"` / `"N"`) by `AppPropmLogin()`.

---

### ShowSQL / QryPop — Exec. → Append

The ShowSQL right-click popup (`QryPop(JTextArea)` constructor) now includes
**Exec. → Append**, which opens the `AppendToTable` dialog at size 440×300.

---

### Copy to SQLite

#### Menu item

The **Exec. → Derby** menu item in the main query right-click popup
(`QryPop(String)` constructor) has been replaced with **Exec. → SQLite**.

#### Jar availability check

Before opening the dialog, the action checks for the SQLite JDBC driver:

1. `Class.forName("org.sqlite.JDBC")` — system class loader
2. `Sui.ucl.loadClass("org.sqlite.JDBC")` — Sui's dynamic `URLClassLoader`

If neither succeeds, the message *"SQLite not available"* is shown and the action
aborts. This covers the common case where the driver was added via Sui's driver
configuration rather than placed on the system classpath.

#### CopyToSQLite dialog

A new `CopyToSQLite` dialog collects:

| Field | Description |
|---|---|
| SQLite DB File Path | Full path to the `.db` file (e.g. `C:/data/mydb.db`) |
| Target Table Name | Table to create or append to |
| Max rows to insert | Pre-filled from the current Max Rows setting |
| Drop/Re-create table | When checked: drops and recreates the table before inserting |

The file path is persisted in the `SQLITEFILE` tmp property across invocations.

On OK the dialog sets:

```
DERURL  = "jdbc:sqlite:{filePath}"
DERUSER = ""
DERPW   = ""
DERTB   = {table}
DERSC   = ""        ← empty = no schema prefix in DDL / INSERT
DERMR   = {maxRows}
DERAPP  = "Y"       ← routes RunDerby to SetUpApp()
DERRE   = "Y"/"N"
DERDDL  = "N"
```

and launches `RunDerby` in a background thread, reusing the existing Derby copy
infrastructure via the `SetUpApp()` path.

---

### RunDerby — SQLite Enhancements

**Automatic table creation:** When `DERAPP = "Y"` and the URL starts with
`jdbc:sqlite:`, `Setup()` overrides `Create = true` and `Drop = ReTb.equals("Y")`.
Previously `SetUpApp()` always set `Create = false`.

**Insert into existing table:** When `Create = true` but the table already exists and
re-create is not requested, the `CREATE TABLE` error is now silently ignored
(detected by "already exist" in the error message) and execution proceeds to the
`INSERT`. Previously this threw an exception.

**`setReadOnly` compatibility:** The call `conn.setReadOnly(true)` on the source
connection is now wrapped in a try-catch that silently ignores `SQLException`. Some
drivers (notably BigQuery) reject this call when a transaction is already active. The
call is a hint only and has no effect on correctness.

---

### DDL Generation — Schema-less Tables

`CreateDDL.CreateTBLDDL()` now checks whether `TbSc` is empty before constructing
`CREATE TABLE` and `DROP TABLE` statements. When empty, the schema prefix and dot
are omitted:

```sql
-- With schema:    CREATE TABLE APP.MYTABLE ( … )
-- Without schema: CREATE TABLE MYTABLE ( … )
```

`RunDerby.cpTable()` applies the same logic to the `INSERT INTO` statement.
This makes the Derby copy infrastructure compatible with SQLite, which does not use
schemas.

---

### Mimer SQL — Bug Fixes

**`AbstractMethodError` on `getFunctionColumns()`:** The Mimer JDBC driver throws
`AbstractMethodError` (not `SQLException`) when `getFunctionColumns()` is called.
`loadProcedureParams()` now catches `AbstractMethodError` specifically and falls back
to `getProcedureColumns()`, setting `useFunctionCols = false` so that the correct
JDBC type constants are used for the fallback result set.

**Dummy table name:** The dummy table used for function draw statements was
incorrectly specified as `SYSTEM_ONEROW`. Corrected to `SYSTEM.ONEROW`.

---
