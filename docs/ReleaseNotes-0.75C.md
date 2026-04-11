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
