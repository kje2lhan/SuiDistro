# Release Notes — Sui 0.75C

**Branch:** `master`  
**Base:** `940bbc3` (2026-04-07 — "added credential docs")  
**Date:** 2026-04-08  
**Commits in this release:** 4 (PR #33 + direct commits `b81a5f7`, `d35952e`, version bump)

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Query results panel | Fix | NUMERIC/DECIMAL columns now rendered with correct decimal precision |
| CSV export | Fix | NUMERIC/DECIMAL columns in CSV export now use exact column scale |
| Security fix (compilation) | Fix | `java.awt.Desktop` name clash with `Desktop` field resolved — "Send query to" now compiles correctly |
| Documentation | Update | `README.md` updated with 0.75B section |
| ShowQryBox — query browser | Fix | Case-insensitive search: filter now matches SQL content regardless of case |
| QueryRep / SuiAdapter — row filter | Fix | String column filtering now works for columns with zero or unknown display length (e.g. BigQuery `STRING`) |
| SuiAdapter — row filter | Fix | Filter length threshold made consistent (≤ 500 or 0) in both the dialog guard and the filter engine |

---

## Detailed Changes by File

### Source Code

#### `src/RunIt.java` — Decimal precision fix for NUMERIC/DECIMAL columns (PR #33)

**Problem**  
NUMERIC and DECIMAL columns were fetched using `result.getString()` and then formatted
by `FixDec()`. This approach could produce incorrect results when the database returns
a value with fewer decimal digits than the column's defined scale (e.g. `1.5` displayed
instead of `1.50` for a `DECIMAL(10,2)` column), or when scientific notation was
returned by the JDBC driver.

**Fix**  
When the column type is `Types.DECIMAL` or `Types.NUMERIC` and the column has a
non-negative scale (read from `ResultSetMetaData.getScale()`), the value is now
fetched using `result.getBigDecimal()` and normalised with
`BigDecimal.setScale(columnScale, RoundingMode.HALF_UP).toPlainString()`.

This fix applies in two places:

- **Query results panel** (row data population loop, ~line 759): column data stored
  in `cData[][]` now preserves the declared decimal scale for NUMERIC/DECIMAL columns.
- **CSV export** (CSV data line construction loop, ~line 635): exported values for
  NUMERIC/DECIMAL columns are written using the same `BigDecimal`-based formatting,
  so CSV files match the precision displayed in the results panel.

All other column types continue using the existing `getString()` + `FixDec()` path.

---

#### `src/Sui.java` — Compilation fix: `java.awt.Desktop` name clash

The `MailMenuItem` handler introduced in 0.75B used `Desktop.getDesktop().mail(uri)`.
Because `Sui` declares a static field `private static String Desktop`, the Java compiler
resolved `Desktop` as the field rather than the `java.awt.Desktop` class, causing:

```
[ERROR] cannot find symbol
[ERROR]   symbol:   method getDesktop()
[ERROR]   location: variable Desktop of type java.lang.String
```

Fixed by qualifying the class reference: `java.awt.Desktop.getDesktop().mail(uri)`.

---

### Documentation

#### `README.md` — Updated

Added Sui 0.75B section summarising the security fix, `DatabaseManager` delegation,
preferences persistence fix, and the new `CredentialHandling.md` document.

---

## Upgrade Notes

- No property file format changes. Existing `.pro` files are fully compatible.
- Users who observed trailing-zero truncation or scientific-notation display in
  NUMERIC/DECIMAL result columns, or incorrect values in CSV exports for those column
  types, should see correct output after this release.
- Users who experienced the query-browser search (`ShowQryBox`) not matching lower-case
  SQL content should now get correct case-insensitive results.
- Users running against BigQuery (or other databases that report STRING column display
  length as 0) can now apply row filters on string columns in the results panel.

---

## Detailed Changes — 2026-04-19

### `src/ShowQryBox.java` — Case-insensitive filter in query browser (commit `9a87526`)

**Problem**  
The filter string entered in the query browser was uppercased before comparison, but the
SQL text retrieved from the store was compared as-is. Searches for lower-case content
never matched.

**Fix**  
`getSQLStmt(x).toUpperCase().contains(filter)` — the SQL content is now also uppercased
before the `contains()` check, making the comparison fully case-insensitive.

---

### `src/QueryRep.java` + `src/SuiAdapter.java` — String column filter for zero-length columns (commit `1ba2157`)

**Problem**  
BigQuery (and some other JDBC drivers) report `getColumnDisplaySize()` as `0` for
unconstrained `STRING` columns. The filter dialog guard in `QueryRep` blocked filtering
for any column with length > 500, and the actual filter loop in `SuiAdapter` skipped
columns unless length was < 250. This meant:

1. The filter dialog was shown but filtering was silently skipped for columns in the
   250–500 range.
2. Columns with length 0 were blocked entirely even though they are filterable strings.

**Fix**  
- `QueryRep.java`: dialog guard now allows filtering when length is 0, and only blocks
  when length is both > 500 *and* non-zero: `tcLn[ix] > 500 && tcLn[ix] != 0`.
- `SuiAdapter.java`: filter loop threshold raised from `< 250` to `<= 500`, and length
  0 is also explicitly allowed: `Length[j] <= 500 || Length[j] == 0`.

