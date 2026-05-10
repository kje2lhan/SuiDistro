# Release Notes — Sui 0.75N

**Branch:** `Sui0.75N`  
**Base:** `Sui 0.75M` (Connection Manager)  
**Date:** 2026-05-10  

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
| SQL Dialect Converter | New feature | NVL, NVL2, ZEROIFNULL, NULLIFZERO, DECODE, ADD_MONTHS, CHR, ASCII, TRUNCATE, MINUS→EXCEPT DISTINCT conversions |
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
| SQL Tree | Enhancement | Schema node now groups objects into **Tables / Views / Aliases / Synonyms** sub-folders; only non-empty groups shown |
| SQL Tree | Enhancement | "Include routines" checkbox adds a lazy **Routines** group alongside the object-type groups |
| Excel export | Enhancement | Numeric columns written as Excel numeric cells; integers and decimals use separate configurable formats |
| Excel export | Enhancement | `BigDecimal` columns formatted as decimals; all others attempted as integers with fallback to string |
| Excel export | Enhancement | Meta sheet now includes "Result set status" (full / partial) and row count |
| Excel export | Enhancement | Font, integer format, and decimal format configurable in Preferences → Export |
| Preferences → Export | New feature | New fields: XLS font name (dropdown of installed fonts), XLS integer format, XLS decimal format |
| ConnDB | Bug fix | `sanitizeUrl` negative lookahead prevents stripping `://` from BigQuery `https://` embedded URLs |
| Toolbar | Enhancement | Connection Manager toolbar button tooltip updated; action wired to `ConnManager` dialog |
| Version | Bump | Version string updated to `0.75N` in `Sui.java`, `ExpXLS.java`, `ExpXLSRS.java`, `pom.xml`, About dialog |

---

## Detailed Changes by Area

---

### SQL Dialect Converter (`SqlDialectConverter.java`, `ConvertSqlDialog.java`)

A new **Convert SQL Dialect…** dialog is available from the **Options** menu and from the
right-click menu in the query editor. It converts DB2 SQL to BigQuery-compatible SQL and
collects warnings about constructs that were changed or need manual review.

#### Function conversions

| DB2 construct | BigQuery equivalent | Notes |
|---|---|---|
| `DECIMAL(expr, p, s)` | `ROUND(CAST(expr AS NUMERIC), s)` | Warning generated |
| `DECIMAL(expr, p)` | `CAST(expr AS NUMERIC)` | Warning generated |
| `VARCHAR_FORMAT(expr, fmt)` | `FORMAT_TIMESTAMP(bq_fmt, expr)` or `FORMAT_DATE(…)` | DB2 format tokens mapped to BigQuery strftime tokens |
| `NVL(a, b)` | `COALESCE(a, b)` | |
| `NVL2(a, b, c)` | `IF(a IS NOT NULL, b, c)` | |
| `ZEROIFNULL(a)` | `COALESCE(a, 0)` | |
| `NULLIFZERO(a)` | `NULLIF(a, 0)` | |
| `DECODE(e, s, r, …)` | `CASE WHEN e=s THEN r … END` | |
| `ADD_MONTHS(d, n)` | `DATE_ADD(d, INTERVAL n MONTH)` | |
| `CHR(n)` | `CODE_POINTS_TO_STRING([n])` | |
| `ASCII(s)` | `TO_CODE_POINTS(s)[OFFSET(0)]` | |
| `TRUNCATE(n, s)` | `TRUNC(n, s)` | |
| `MINUS` (set operator) | `EXCEPT DISTINCT` | |
| `MERGE INTO tgt t …` | `MERGE tgt AS t …` | `INTO` removed; target alias in `UPDATE SET` blocks de-qualified |

#### CTE handling

A CTE that selects `SELECT *` in its body previously left the column header list in place,
producing invalid BigQuery syntax. The converter now strips the header list and emits a warning.

#### Date format mapping (`convertDb2DateFmt`)

| DB2 token | BigQuery token |
|---|---|
| `YYYY` | `%Y` |
| `MM` | `%m` |
| `DD` | `%d` |
| `HH24` | `%H` |
| `HH` | `%I` |
| `MI` | `%M` |
| `SS` | `%S` |
| `DY` | `%a` |
| `DAY` | `%A` |
| `MON` | `%b` |
| `MONTH` | `%B` |

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
each Run, so it does not persist between runs.

The Query Report window title reflects the overriding URL, not the URL-box URL.

#### `#SET` — new syntax

In addition to the original `#SET= KEY VALUE` form, the natural `KEY=VALUE` form is
now also accepted:

```sql
#SET MYSCHEMA=REPORTING;
```

Both forms store the value in session memory where it can be referenced as `&&MYSCHEMA`
without prompting the user.

See [InlineDirectives.md](InlineDirectives.md) for full documentation of all inline
directives including `<include>` and `#FILX=`.

---

### Syntax Highlighting (`Highlighter.java`)

- Approximately 60 additional SQL keywords are now recognised and coloured.
- **Performance cap**: when the editor document exceeds 5 000 characters, keyword
  scanning is skipped entirely. The `HighLightOn` preference is not changed, so
  highlighting resumes automatically when the document is cleared or reduced.
- **Comment fix**: a `/*` token appearing after `--` on the same line no longer
  triggers multi-line comment colouring for the rest of the document.
- Styles are reset on every keystroke so that coloured text does not bleed into
  newly typed characters when highlighting is toggled off mid-session.

---

### SQL Tree (`SQLTreePanel.java`)

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

- Columns are now classified using the JDBC `java.sql.Types` column-type array
  passed from `QueryRep` rather than the JTable column class name.
- `DECIMAL`/`NUMERIC` columns are formatted as decimal numbers using configurable
  format strings and written as `double` via `BigDecimal.doubleValue()`.
- Integer-type columns are written as `int` values with a separate configurable
  format string.
- Non-numeric columns remain as strings.
- If parsing fails for any numeric value, the cell falls back to a string value.

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

The font name is selected from a dropdown populated with all fonts installed on the
local system.

---

### ConnDB — BigQuery URL fix (`ConnDB.java`)

The `sanitizeUrl` helper that strips empty port colons from JDBC URLs
(e.g. `jdbc:mysql://host:/db` → `jdbc:mysql://host/db`) now uses a negative
lookahead to avoid matching the embedded `https://` in BigQuery JDBC URLs
(`jdbc:bigquery://https://www.googleapis.com/…`).

---

### QryPop Right-click Menu (`QryPop.java`)

The right-click context menu in the query editor has been reorganised:

1. Format SQL
2. Ext Format SQL
3. Syntax Validate
4. Syntax Validate by Prepare *(when connected)*
5. ───────────────
6. Convert SQL Dialect…
7. Remove Initial numerics…
8. InList / TextIns
9. ───────────────
10. Del CSV / Del XLS / Del tmp
11. ───────────────
12. Highlighting / ParenHig / HideQ·ShowQ / LineNo / QueryToolbar / SQLTree
13. ───────────────
14. Box / SheetBox / Imp
15. ───────────────
16. Copy / Cut / Paste
17. Trim Trailing Whitespace
18. Copy Columns from Selection…

"Sheet Preferences" has been removed.

---

### Options Menu (`Sui.java`)

"Convert SQL Dialect…" has been added at the bottom of the **Options** menu,
separated from the existing items by a menu separator. It opens the same
`ConvertSqlDialog` as the right-click menu item.
