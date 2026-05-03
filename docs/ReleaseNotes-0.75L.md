# Release Notes — Sui 0.75L

**Branch:** `0.75L`  
**Base:** `Sui 0.75K` (SQL Object Tree enhancements / SQLite copy / index sub-tree)  
**Date:** 2026-05-03  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| SQL Dialect Converter | New feature | New `SqlDialectConverter` engine — DB2 ↔ BigQuery SQL translation |
| SQL Dialect Converter | New feature | DB2 → BQ: strips isolation clauses, rewrites date/time specials, removes dummy tables |
| SQL Dialect Converter | New feature | DB2 → BQ: `FETCH FIRST n ROWS ONLY` → `LIMIT n` |
| SQL Dialect Converter | New feature | DB2 → BQ: interval arithmetic — `CURRENT TIMESTAMP - 7 DAYS` → `TIMESTAMP_SUB(…)` |
| SQL Dialect Converter | New feature | DB2 → BQ: function transforms — YEAR/MONTH/DAY/HOUR/MINUTE/SECOND → EXTRACT, CHAR/VARCHAR → CAST STRING, INTEGER/INT → CAST INT64, FLOAT/DOUBLE → CAST FLOAT64, STRIP → TRIM, LOCATE/POSSTR → STRPOS (args reversed) |
| SQL Dialect Converter | New feature | DB2 → BQ: CTE column-list push-down — inlines column aliases into SELECT items and removes the `(col, …)` list from the WITH clause |
| SQL Dialect Converter | New feature | BQ → DB2: backtick identifiers → double-quoted, splits `project.dataset.table` segments |
| SQL Dialect Converter | New feature | BQ → DB2: CURRENT_TIMESTAMP() / DATE() / TIME() → DB2 special registers |
| SQL Dialect Converter | New feature | BQ → DB2: STRPOS → LOCATE (args reversed), IF → CASE WHEN, IFNULL → COALESCE, TO_HEX → HEX, SAFE_CAST → CAST with warning |
| SQL Dialect Converter | New feature | Schema application — rewrites unqualified table names to `schema.table` in SELECT statements; CTE names are excluded |
| Convert SQL Dialect dialog | New feature | New `ConvertSqlDialog` with From/To dialect combos (default DB2 → BQ), result area, and warnings area |
| Convert SQL Dialect dialog | New feature | "Format using Extended Format SQL" checkbox (persisted across invocations) |
| Convert SQL Dialect dialog | New feature | Target schema field — optional schema prefix applied after conversion (persisted across invocations) |
| Convert SQL Dialect dialog | New feature | Combo boxes enforce opposite selection — cannot select the same dialect in both From and To |
| Convert SQL Dialect dialog | New feature | Dialog title: "Convert SQL Dialect (experimental)" |
| QryPop | New feature | "Convert SQL Dialect…" added to query right-click popup |
| Query History Viewer | Bug fix | URL filter field no longer invisible on first open (width capped to 200 px) |
| Query History Viewer | Bug fix | `NullPointerException` in filter navigation when `getSQLStmt()` returns null — guarded |
| RunIt | Bug fix | `NullPointerException` when executing a query with no active connection — now shows "Query cannot be executed - not connected" |

---

## Detailed Changes by Area

---

### SQL Dialect Converter — Overview

A new conversion engine `SqlDialectConverter` translates SQL between DB2 and BigQuery
(bidirectionally). The entry point is:

```java
String result = new SqlDialectConverter().convert(sql, "DB2", "BigQuery");
```

`getWarnings()` returns a list of strings for constructs that required manual review
(e.g. `DIGITS()`, `EXCEPTION JOIN`, `SAFE_CAST`, array functions).

The engine uses three techniques in combination:

| Technique | Used for |
|---|---|
| Regex replacement | Keywords, date/time specials, isolation clauses, dummy tables, `FETCH FIRST … ROWS ONLY` |
| Balanced-paren function transformer | Function name rewrites that must respect nested parentheses (e.g. YEAR → EXTRACT, LOCATE → STRPOS) |
| JSqlParser 4.9 AST mutation | CTE column-list push-down and schema application |

---

### SQL Dialect Converter — DB2 → BigQuery

Transforms applied in order:

1. **Interval arithmetic** — `CURRENT TIMESTAMP - 7 DAYS` →
   `TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)` (and `+` → `TIMESTAMP_ADD`).
   `CURRENT DATE` and `CURRENT TIME` variants are also handled.
2. **Isolation clause** — `WITH UR`, `WITH CS`, `WITH RR`, `WITH RS` removed.
3. **Date/time specials** — bare `CURRENT TIMESTAMP` → `CURRENT_TIMESTAMP()`,
   `CURRENT DATE` → `CURRENT_DATE()`, `CURRENT TIME` → `CURRENT_TIME()`.
4. **Dummy tables** — `FROM SYSIBM.SYSDUMMY1`, `FROM SYSIBM.DUAL`, `FROM DUAL`
   removed (entire `FROM` clause stripped).
5. **`FETCH FIRST n ROWS ONLY`** → `LIMIT n`.
6. **Warnings** — `CALL` statements and `EXCEPTION JOIN` are flagged for manual review.
7. **Function transforms** (balanced-paren aware):

   | DB2 | BigQuery |
   |---|---|
   | `YEAR(x)` | `EXTRACT(YEAR FROM x)` |
   | `MONTH(x)` | `EXTRACT(MONTH FROM x)` |
   | `DAY(x)` | `EXTRACT(DAY FROM x)` |
   | `HOUR(x)` | `EXTRACT(HOUR FROM x)` |
   | `MINUTE(x)` | `EXTRACT(MINUTE FROM x)` |
   | `SECOND(x)` | `EXTRACT(SECOND FROM x)` |
   | `CHAR(x)` | `CAST(x AS STRING)` |
   | `VARCHAR(x, n)` | `CAST(x AS STRING)` |
   | `INTEGER(x)` / `INT(x)` | `CAST(x AS INT64)` |
   | `FLOAT(x)` / `DOUBLE(x)` | `CAST(x AS FLOAT64)` |
   | `STRIP(x, …)` | `TRIM(x)` |
   | `LOCATE(needle, haystack)` | `STRPOS(haystack, needle)` (args reversed) |
   | `POSSTR(haystack, needle)` | `STRPOS(haystack, needle)` |

8. **Warnings** — `DIGITS()` and `HEX()` have no direct BigQuery equivalents; flagged.
9. **CTE column-list push-down** (see below).

---

### SQL Dialect Converter — CTE Column-List Push-Down

DB2 allows column aliases to be declared in the `WITH` clause header:

```sql
WITH cte (col1, col2) AS (
    SELECT a, b FROM t
)
SELECT * FROM cte
```

BigQuery does not support this syntax. The converter inlines the aliases as `AS`
clauses on the corresponding `SELECT` items and removes the column list:

```sql
WITH cte AS (
    SELECT a AS col1, b AS col2 FROM t
)
SELECT * FROM cte
```

This is implemented using the JSqlParser 4.9 AST. `WithItem.getSelect()` is used
(rather than `getPlainSelect()`) to safely handle the case where the CTE body is
wrapped in a `ParenthesedSelect`.

---

### SQL Dialect Converter — BigQuery → DB2

Transforms applied in order:

1. **Backtick identifiers** → double-quoted. `` `project.dataset.table` `` is split on
   dots and each segment double-quoted individually:
   `"project"."dataset"."table"`. String literal content is preserved unchanged.
2. **Date/time functions** — `CURRENT_TIMESTAMP()` → `CURRENT TIMESTAMP`,
   `CURRENT_DATE()` → `CURRENT DATE`, `CURRENT_TIME()` → `CURRENT TIME`.
3. **Function transforms**:

   | BigQuery | DB2 |
   |---|---|
   | `STRPOS(haystack, needle)` | `LOCATE(needle, haystack)` (args reversed) |
   | `IF(cond, t, f)` | `CASE WHEN cond THEN t ELSE f END` |
   | `IFNULL(x, y)` | `COALESCE(x, y)` |
   | `TO_HEX(x)` | `HEX(x)` |
   | `SAFE_CAST(x AS t)` | `CAST(x AS t)` + warning |

4. **Warnings** — array functions (`ARRAY_AGG`, `UNNEST`, `ARRAY_LENGTH`, etc.)
   have no direct DB2 equivalents; flagged.

---

### SQL Dialect Converter — Schema Application

`applySchema(sql, schema)` rewrites all unqualified table references in a `SELECT`
statement to `schema.table`. It uses a `SelectDeParser` with an overridden
`visit(Table)` method. Tables whose names match any CTE defined in the `WITH` clause
are excluded (CTE names are collected into a `HashSet` from `getWithItemsList()`).

If JSqlParser cannot parse the SQL (e.g. it uses dialect-specific syntax), the
original SQL is returned unchanged and a warning is recorded.

---

### Convert SQL Dialect Dialog

A new `ConvertSqlDialog` is opened via **Convert SQL Dialect…** in the query
right-click popup.

**Layout:**

| Row | Contents |
|---|---|
| 0 | "From dialect:" combo | "  To dialect:" combo |
| 1 | "Format using Extended Format SQL" checkbox (spans row) |
| 2 | "Target schema (optional):" label | schema text field |
| — | Source SQL text area (read-only, pre-filled from query window) |
| — | Result SQL text area |
| — | Warnings text area |
| — | Convert / To Sheet / Show SQL / Close buttons |

**Combo behaviour:** Selecting a dialect in one combo automatically sets the other to
the opposite dialect. The same dialect cannot appear in both combos simultaneously.

**Default:** Always opens with DB2 as From and BigQuery as To.

**Format checkbox:** When checked, the conversion result is passed through
`FormSQL2` (Extended Format SQL) before display. This applies the formatting
preferences set in Preferences → Query → Ext Format SQL.

**Target schema:** When non-empty, `applySchema()` is called on the converted SQL
after conversion. CTE-named tables are not qualified.

**Persistence:** The `chExtFmt` checkbox state and the schema field value are stored
in `TmpProp.pro` under the keys `CONVDLG.EXTFMT` and `CONVDLG.SCHEMA` and restored
on the next invocation.

**Buttons:**

| Button | Action |
|---|---|
| Convert | Runs conversion + optional schema application + optional formatting; populates result and warnings areas |
| To Sheet | Copies result to the active query sheet |
| Show SQL | Opens result in a `ShowSQL` viewer |
| Close | Disposes the dialog |

---

### Query History Viewer — URL Filter Width Fix

The URL filter combobox was rendered with its unconstrained preferred width, which
often exceeded the width of the filter row and made the field invisible. The preferred
and minimum sizes are now capped at 200 px so the field is always visible on first
open regardless of connection URL length.

---

### Query History Viewer — Null Statement Guard

`calculateNewPosition()` called `getSQLStmt(x).toUpperCase()` without checking for
`null`. When the history entry has no SQL text the call threw a
`NullPointerException` and broke filter navigation. A null check has been added so
null-text entries are treated as non-matching.

---

### RunIt — Not Connected Guard

`PerformProc()` previously attempted to construct a `DatabaseManager` (which opens
`ConnDB`) even when no connection URL was set, resulting in:

```
NullPointerException: Cannot invoke "String.trim()" because "urlin" is null
    at ConnDB.<init>(ConnDB.java:39)
    at DatabaseManager.<init>(DatabaseManager.java:9)
    at RunIt.PerformProc(RunIt.java:…)
```

`PerformProc()` now checks `Sui.Geturl()` before constructing `DatabaseManager`. When
the URL is null or blank the method sets the status message to
*"Query cannot be executed - not connected"* and returns immediately.
