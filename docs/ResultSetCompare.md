# Result Set Compare

Compare the result of a SELECT query against the same query (or a modified version) executed on a different connection.

---

## Starting a compare

1. Run any SELECT query — the result window opens as usual.
2. Click the **+** button in the toolbar (tooltip: *Diff with another connection*).  
   A menu appears listing every connection used in the current session.
3. Pick the target connection.
4. If the target connection requires a password that is not cached, a password prompt appears.
5. A SQL editor opens pre-filled with the original query.  
   Edit the SQL if the target connection uses a different schema name, table name, or needs different filter conditions. Click **OK**.
6. The query runs in a background thread against the target connection.  
   When it completes, the **Diff window** opens.

---

## Diff window

### Colour coding

| Colour | Meaning |
|---|---|
| Pale green (full row) | Row exists in the **left** (original) result only |
| Pale red (full row) | Row exists in the **right** (target) result only |
| Pale yellow (individual cell) | Row matched on both sides, but this cell value differs |
| White | Row is identical on both sides |

The **left** connection is always the one that ran the original query.  
The **right** connection is the one selected from the menu.

### Column handling

Columns are matched **by name** (case-insensitive) across the two result sets.

- Columns present on both sides are placed side-by-side: `◄ COLNAME` (left value) and `COLNAME ►` (right value).
- Columns that exist only on one side are included and show an empty cell on the other side. They appear in the key list annotated as **[L only]** or **[R only]**.
- Left-side columns appear first; any right-only columns are appended at the end.

### Summary bar

Shown in the toolbar:

```
Key: COLNAME  |  Identical: N  |  Cells differ: N  |  Left only: N  |  Right only: N
```

`Key:` shows which columns are used for row matching (or `position` if none are selected).

---

## Key column selection

By default rows are matched **by position** (row 1 vs row 1, row 2 vs row 2, etc.).  
This is only reliable when both result sets return rows in the same order.

To match rows by value instead:

1. In the **Key columns** panel (top-left of the diff window), click one or more column names.  
   Use **Ctrl+click** to select multiple columns (composite key).
2. Click **Apply key** — the diff is recomputed using the selected columns as a composite match key.
3. Click **Position** to clear the key selection and return to position-based matching.

Columns marked **[L only]** or **[R only]** are poor key candidates because the other side has no value to match against.

---

## Opening the result in a full query window

Click **Open in query view** to materialise the current diff result into a standard Sui result window.

The query window contains:

| Column | Content |
|---|---|
| `STATUS` | `MATCH`, `LEFT_ONLY`, or `RIGHT_ONLY` |
| `◄ COLNAME` | Left-side value for each column |
| `COLNAME ►` | Right-side value for each column |

Because it is a standard result window you get the full toolbar:  
filter, transpose, transpose on value, export to XLS, export to CSV, print, zoom, show cell data, column information, sort, hide columns, etc.

The diff window remains open alongside it so the colour highlighting is still visible.

---

## Exporting the diff

**Export CSV** (in the diff window toolbar) writes the current diff result to a CSV file.

- Default file name: `DiffResult_yyyyMMdd_HHmmss.csv`
- Columns: `Status`, then `Left_COLNAME` / `Right_COLNAME` pairs for every merged column.
- Only the current diff state (with the currently active key) is exported.

---

## Connection and transaction handling

The target query runs through the same connection infrastructure as a normal query (`DatabaseManager` → `ConnDB`), including:

- Any `SuiConnPref.pro` properties that match the target URL prefix.
- The transaction isolation level configured in Sui preferences.
- Explicit `rollback` + `close` after the result set is fetched, so DB2 and other databases that require transaction cleanup before close work correctly.

The background thread is named `RunItDiff` and is visible in the Query Monitor while it is running.

---

## Limitations

- The compare button is only available on SELECT result windows (type `S`). It does not appear on table/schema browser windows.
- Null values are represented as `?`, matching the convention used throughout Sui.
- The diff window itself does not support filter or sort; use **Open in query view** for those operations.
