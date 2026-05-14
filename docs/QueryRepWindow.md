# Query Result Window

Every SELECT query opens a result window with a toolbar, a scrollable table, and context menus. This document describes the available functionality.

---

## Toolbar

| Button | Action |
|---|---|
| Export CSV | Export all visible rows to a CSV file |
| Export XLS | Export to Excel (requires the Apache POI library on the classpath) |
| Copy | Copy selected cells to the clipboard |
| Print | Print the result table |
| Print Preview | Preview before printing |
| Page Setup | Configure paper size and orientation |
| Query Monitor | Open or refresh the Query Monitor |
| Transpose | Transpose columns of the selected row (see below) |
| Zoom in / Zoom out | Increase or decrease the table font size |
| Remove filters | Clear all active column filters (enabled only when a filter is active) |
| List Columns | Show column metadata for the result set |
| Show SQL | Show the original SQL statement that produced this result (SELECT windows only) |
| Diff (+) | Compare this result against another connection (SELECT windows only — see [ResultSetCompare.md](ResultSetCompare.md)) |

---

## Column header right-click menu

Click the header of any column to select that column, then right-click for:

| Item | Description |
|---|---|
| Column Information | Summary statistics for the selected column (see below) |
| Sort data Ascending | Sort the entire result by this column, A→Z / low→high |
| Sort data Descending | Sort the entire result by this column, Z→A / high→low |
| Sort columns Ascending | Reorder the visible *columns* alphabetically by name |
| Hide Column | Remove this column from the view (data is not lost) |
| Undo hide column | Restore the most recently hidden column next to the current column |
| Undo hide of all columns | Restore all hidden columns |
| Apply Filter | Open the filter dialog for this column (see below) |

### Column Information

Shows a popup with:

- Column name, data type, display length, total row count
- For **numeric** columns: non-null count, lowest value, highest value, sum, average
- For **character** columns (length ≤ 200): non-null count, lowest value, highest value

---

## Cell right-click menu (row area)

Right-click any cell in the data area for:

| Item | Description |
|---|---|
| Transpose Row | Open the selected row as a two-column list (column name / value) |
| Show cell data | Open the full cell content in a resizable text window with format options |
| Filter on value | Immediately filter to rows where this column equals the selected cell value |
| Remove filter on Column | Clear the filter on this column only |
| Select row | Extend the selection to the entire row |
| Select for transpose | Mark this row for a multi-row transpose comparison |
| Transpose/compare selected | Transpose all rows marked *Sel* into a side-by-side comparison window |
| Transpose/compare on value | Transpose all rows whose value in the selected column matches the current cell |
| Copy selected data | Copy selected cells to the clipboard |
| Copy WHERE clause from row | Build a `WHERE col = 'value' AND …` clause from the entire row and copy it to the clipboard |
| Hide Row | Remove this row from the view (does not affect the database) |
| Build Insert | Generate an INSERT statement from this row |
| Launch File | Open a BLOB or CLOB file reference stored in the cell |

---

## Filtering

### Filter on value (quick)

Right-click a cell → **Filter on value**.  
The table immediately narrows to rows where that column equals the cell content.  
The **Remove filters** toolbar button lights up.

### Apply Filter (dialog)

Right-click a column header → **Apply Filter**.  
Opens a small dialog with:

- **Operator** dropdown — available operators depend on the column data type:

  | Operator | Applies to |
  |---|---|
  | `=` | text, numeric |
  | `<>` | text, numeric |
  | `>` | text, numeric |
  | `<` | text, numeric |
  | `BETWEEN` | text, numeric — shows a second value field |
  | `IS NULL` | text, numeric |
  | `IS NOT NULL` | text, numeric |
  | `IN` | text, numeric — enter comma-separated values |
  | `NOT IN` | text, numeric — enter comma-separated values |
  | `LIKE` | text only |
  | `NOT LIKE` | text only |

- **Filter value** field (or two fields for BETWEEN).
- **Apply** to activate, **Cancel** to dismiss without change.

Multiple columns can each have an independent filter active at the same time. They are combined with AND logic. The row count in the status bar at the bottom of the window updates to reflect how many rows pass all active filters.

To clear individual column filters: right-click the cell → **Remove filter on Column**.  
To clear all filters at once: toolbar **Remove filters** button or menu **Options → Remove All filters**.

---

## Transpose Row

**Toolbar button** or **Ctrl+L** or menu **Options → Transpose Row**.  
Requires a row to be selected first.

Opens a new result window with two columns:

| Column name | Column Value |
|---|---|
| NAME | Alice |
| DEPT | Finance |
| … | … |

The new window is itself a full result window, so it can be filtered, sorted, exported, etc.  
Use **F8 / F7** in the transpose window to step to the next or previous row of the original result.

---

## Transpose / compare on value

Right-click a cell in the data area for two multi-row transpose options:

### Transpose/compare selected

1. Right-click each row you want to include → **Select for transpose** (marks the row header with `Sel`).
2. Right-click any cell → **Transpose/compare selected**.

All marked rows are opened side-by-side in a new result window: columns become rows, and each selected row becomes a column labelled `Row: N`.

### Transpose/compare on value

Right-click a cell → **Transpose/compare on value**.

All rows where the selected column has the same value as the clicked cell are collected and transposed side-by-side into a **Compare Rows** window, one column per matching row.

This is useful for comparing two versions of the same entity (e.g. the same customer record in two environments, two time periods, etc.).

---

## Show cell data

Right-click a cell → **Show cell data**.

Opens a resizable text window showing the full, untruncated cell content. Large values (JSON documents, XML fragments, long SQL strings) that are cut off in the table are fully readable here.

### Format buttons in the cell data window

| Button | Action |
|---|---|
| Format JSON | Pretty-print the content as JSON with 2-space indentation |
| Format XML | Pretty-print the content as indented XML |
| Format SQL | Parse and reformat the content as SQL |
| Cancel | Close the window |

All three format buttons operate on the **selected text** if any text is selected, or on the entire content otherwise. The formatted result replaces the content in the window; the original cell in the table is not modified.

---

## Column list

Toolbar **List Columns** button (available on SELECT result windows).

Opens a separate result window showing one row per column:

| Col. Name | Col. Type | Length | Decimals | Display Length | Is nullable |
|---|---|---|---|---|---|
| NAME | VARCHAR | 50 | 0 | 50 | Yes |
| AMOUNT | DECIMAL | 10 | 2 | 10 | No |

---

## Export

### CSV

Toolbar **Export CSV** or menu **File → Export**.  
Writes the currently visible rows (post-filter) with the current column order to a CSV file via a file chooser dialog.

### Excel (XLS)

Toolbar **Export XLS** or menu **File → Exp XLS**.  
Requires the Apache POI library. Exports the table including the original SQL statement on a second sheet.

---

## Sorting

Click a column header once to select the column, then right-click for **Sort data Ascending** or **Sort data Descending**.

Sorting is performed in-memory on the currently loaded result set. It respects the current filter — only visible rows are reordered.

**Sort columns Ascending** reorders the *columns themselves* alphabetically by name, which can be useful when comparing wide result sets with many columns.

---

## Keyboard shortcuts

| Key | Action |
|---|---|
| Ctrl+L | Transpose selected row |
| Ctrl+C | Copy selected cells |
| Ctrl+E | Export to CSV |
| Ctrl+M | Query Monitor |
| Ctrl+P | Print |
| F3 | Exit / close window |
| F7 | Previous row (in transpose window) |
| F8 | Next row (in transpose window) |

(SELECT windows only)

| Key | Action |
|---|---|
| Ctrl+T | List Columns |
| Ctrl+Q | Show SQL statement |
