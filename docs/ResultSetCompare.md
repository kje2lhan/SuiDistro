# Result Set Compare

The Compare feature lets you place two SQL result sets side-by-side and instantly
see which rows are identical, which rows appear on only one side, and which cells
differ between the two sides.

---

## How to start a comparison

A comparison is always started from an **open Query Result window** (QueryRep) by
clicking the **`+`** toolbar button (the diff/compare button).  A small popup menu
appears with two sections.

### Section 1 — Open result windows

Lists every other QueryRep window that is currently open (closed windows are
excluded automatically).  Choose one to compare the current result set with that
window **directly in memory** — no SQL re-execution, no password prompt, and the
comparison is instantaneous regardless of result-set size.

### Section 2 — Re-run against connection

Lists every connection that has been used in the current session.  Choose one to
compare the current result with the same (or a modified) query executed against a
**different database connection**.

Selecting a connection entry opens a two-step dialog:

1. **Password prompt** — enter the password for the target connection (skipped if
   the connection is credential-free, e.g. BigQuery with NOCRED).
2. **SQL editor** — the original SQL that produced the current result is pre-loaded
   in an editable text area.  You can adapt it for a different schema, table names,
   or date range before clicking **OK**.  The query is then executed in a background
   thread so the UI stays responsive.

---

## The Compare window (DiffRep)

When the comparison is ready, a dedicated **Diff window** opens.

### Layout

```
+──────────────────────────────────────────────────────────────────────────────+
│  Key columns panel  │  Toolbar (summary, buttons, options)                   │
+─────────────────────┴────────────────────────────────────────────────────────+
│                                                                               │
│          Merged result table  (scrollable)                                    │
│                                                                               │
+──────────────────────────────────────────────────────────────────────────────+
│  Legend / colour key                │  Show: All  Left only  Right only  Differ  │
+──────────────────────────────────────────────────────────────────────────────+
```

---

## Column structure of the merged table

For every column that appears in either result set, the table shows **two
side-by-side columns**:

| Header format | Meaning |
|---|---|
| `< COLUMN_NAME` | Value from the **left** result set |
| `COLUMN_NAME >` | Value from the **right** result set |

Columns are aligned by **name** (case-insensitive).  If the two result sets have
different column sets:

- Columns present only in the left result are marked **`[L only]`** in the key
  selector.
- Columns present only in the right result are marked **`[R only]`** in the key
  selector.

---

## Row colouring

| Background colour | Meaning |
|---|---|
| **Pale green** (full row) | Row exists only in the left result set (`LEFT_ONLY`) |
| **Pale red / pink** (full row) | Row exists only in the right result set (`RIGHT_ONLY`) |
| **Pale yellow** (individual cells) | Both sides have this key, but the cell value differs |
| **White** | Row is fully identical on both sides |

Selected rows follow the standard selection colour (colouring is suppressed while
a row is highlighted by selection).

---

## Matching mode — Key columns

The **Key columns** panel on the left side of the toolbar controls how rows from
the two result sets are paired.

### Position-based matching (default)

When no key columns are selected, rows are matched by their **position** — row 1
left vs row 1 right, row 2 left vs row 2 right, etc.  Click **Position** to reset
to this mode at any time.

This mode is only reliable when both result sets return rows in the same order.

### Key-based matching

Select one or more column names in the list (use **Ctrl+click** for a composite
key) and click **Apply key**.  The diff algorithm then:

1. Builds a **HashMap** of the right-side result indexed by the composite key value.
2. For every left-side row, looks up the matching right-side row.
3. Any left-side row with no right-side counterpart becomes `LEFT_ONLY`.
4. Any right-side row that was never matched becomes `RIGHT_ONLY` and is appended
   at the bottom.
5. Matched rows are placed together and their cells are compared.

**Composite keys** are supported — selecting `ORDER_ID` + `LINE_NO` creates a
two-part key, with parts separated internally by a null character to avoid false
matches.

Columns marked **[L only]** or **[R only]** are poor key candidates because the
other side has no value to match against.

### Numeric key normalisation

For columns whose JDBC type is a numeric type (TINYINT, SMALLINT, INTEGER, BIGINT,
FLOAT, REAL, DOUBLE, NUMERIC, DECIMAL), key values are normalised through
`BigDecimal.stripTrailingZeros()` before being stored in the HashMap.  This means
`42`, `42.0`, and `42.00` all resolve to the same key entry, so rows match
correctly even when the left and right databases use different numeric precision or
scale (e.g. DB2 SMALLINT vs BigQuery INT64).

---

## Value comparison

### String columns

Two values are equal if their normalised strings are equal.  Normalisation means
stripping trailing whitespace from both sides when the **Ignore trailing blanks**
option is checked (it is on by default).

### Numeric columns

For columns with a numeric JDBC type, values are compared using `BigDecimal`
arithmetic.  This means:

- `123` == `123.000` == `123.00` (different decimal scales)
- `1.5E2` == `150` (exponent notation)

String representation differences such as trailing zeros or exponent notation
do **not** produce false diffs.

The JDBC type used for comparison is taken from the **left** result set's column
metadata.

---

## Toolbar controls

| Control | Action |
|---|---|
| **Apply key** | Re-run the diff using the currently selected key columns |
| **Position** | Clear key selection and re-run using row position |
| **Ignore trailing blanks** checkbox | Toggle trailing-whitespace normalisation and re-run the diff immediately |
| **Open in query view** | Open the current (filtered) diff result as a full QueryRep window, where you can sort, filter, hide columns, transpose, export to XLS, etc. |
| **Export CSV** | Save the diff result to a CSV file with a `Status` column plus left and right value columns for every field |
| **Close** | Close the diff window |

---

## Summary bar

The summary label shows at a glance:

```
Key: ORDER_ID+LINE_NO  |  Identical: 1 842  |  Cells differ: 37  |  Left only: 5  |  Right only: 3
```

| Counter | Description |
|---|---|
| **Identical** | Rows matched by key (or position) where every cell is equal |
| **Cells differ** | Rows matched by key but at least one cell value differs |
| **Left only** | Rows in the left result that have no counterpart on the right |
| **Right only** | Rows in the right result that have no counterpart on the left |

The summary always reflects the **full** diff (all rows), not the current filter view.

---

## Row filters

The **Show:** toggle buttons in the bottom-right corner filter which rows are
visible in the table.  Only one mode is active at a time.

| Button | Rows shown |
|---|---|
| **All** | Every row (default) |
| **Left only** | Only rows that exist exclusively in the left result |
| **Right only** | Only rows that exist exclusively in the right result |
| **Differ** | Only matched rows that have at least one cell value differing |

Switching the filter is instant.  The summary counts always reflect the complete
diff regardless of which filter is active.  **Open in query view** and **Export
CSV** both honour the active filter — only the currently visible rows are included.

---

## Open in query view

Clicking **Open in query view** creates a full QueryRep result window from the
rows currently visible in the diff table.  The new window contains:

- A **STATUS** column as the first column (`MATCH`, `LEFT_ONLY`, or `RIGHT_ONLY`)
- Interleaved `< COLUMN` / `COLUMN >` columns for every merged column

From that window all standard QueryRep features are available: sort, apply filter,
hide columns, transpose, export to XLS, copy to clipboard, and so on.

---

## Export CSV

The CSV file produced by **Export CSV** contains:

- A header row: `Status, Left_COL1, Right_COL1, Left_COL2, Right_COL2, ...`
- One data row per **currently visible** (filtered) diff row
- Cell values are quoted when they contain commas, double quotes, or newlines
- The file is named `DiffResult_YYYYMMDD_HHmmss.csv` by default (editable in the
  file chooser)

---

## Source identification

The bottom-left legend panel shows the connection URLs of both sides:

```
[green]  Left only     [red]  Right only     [yellow]  Value differs
Left: jdbc:db2://prod-server/MYDB        Right: jdbc:bigquery://...
```

Long connection URLs are truncated to 60 characters with `...` prefixed so the
panel stays compact.

---

## Tips and common workflows

**Comparing the same query across environments (DEV vs PROD)**

1. Run the query in DEV — a QueryRep window opens.
2. Click **`+`** → choose the PROD connection from the history list.
3. Adjust the SQL if schema names differ, enter the PROD password, click **OK**.
4. The diff window opens.  Select the primary-key column(s) in the **Key columns**
   panel and click **Apply key** for a meaningful comparison regardless of row order.

**Comparing two already-open result windows**

1. Both queries must already be open as QueryRep windows.
2. Click **`+`** in either window → the other window appears under *Open result windows*.
3. Choosing it compares the in-memory data immediately — useful for comparing two
   reformulations of the same query without any extra connection or SQL execution.

**Narrowing down to differences only**

1. Click **Differ** in the bottom-right **Show:** filter to hide identical rows.
2. Use **Open in query view** to work with the diff rows in a full result window
   (sort, apply a further filter, export to XLS).

**Handling numeric precision mismatches**

Key-based matching and cell comparison both use `BigDecimal` for numeric JDBC types,
so differences in trailing zeros or decimal scale never produce false positives.  If
you see unexpected mismatches on a numeric column, check the **Ignore trailing
blanks** checkbox — a space character embedded in a numeric string can prevent
`BigDecimal` parsing and fall back to string comparison.

