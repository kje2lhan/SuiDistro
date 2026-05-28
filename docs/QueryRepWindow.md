# Query Result Window

Every SELECT query opens a result window with a toolbar, a scrollable table, and context menus. This document describes the available functionality.

---

## Toolbar

| Button / Control | Action |
|---|---|
| Export CSV | Export all visible rows to a CSV file |
| Export XLS | Export to Excel (requires the Apache POI library on the classpath) |
| Copy | Copy selected cells to the clipboard (space-separated, one line per row) |
| **Trim** checkbox | When checked, trailing whitespace is stripped from every cell value and from each copied line before it is placed on the clipboard. Applies to both the toolbar Copy button and the right-click **Copy selected data** menu item. |
| Print | Print the result table |
| Print Preview | Preview before printing |
| Page Setup | Configure paper size and orientation |
| Query Monitor | Open or refresh the Query Monitor |
| Transpose | Transpose columns of the selected row (see below) |
| Zoom in / Zoom out | Increase or decrease the table font size |
| Remove filters | Clear all active column filters (enabled only when a filter is active) |
| List Columns | Show column metadata for the result set |
| Show SQL | Show the original SQL statement that produced this result (SELECT windows only) |
| Diff (+) | Compare this result against another connection or open result window (SELECT windows only — see [ResultSetCompare.md](ResultSetCompare.md)) |

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
| Find | Open the Find bar for in-table text search |
| Go to column | Open the searchable column picker and jump/select that column |
| Filter on value | Immediately filter to rows where this column equals the selected cell value |
| Remove filter on Column | Clear the filter on this column only |
| Select row | Extend the selection to the entire row |
| Select for transpose | Mark this row for a multi-row transpose comparison |
| Transpose/compare selected | Transpose all rows marked *Sel* into a side-by-side comparison window |
| Transpose/compare on value | Transpose all rows whose value in the selected column matches the current cell |
| Highlight row differences from selected cell | Compare against the selected cell and highlight non-matching values in the same row |
| Highlight column differences from selected cell | Compare against the selected cell and highlight non-matching values in the same column |
| Clear diff highlight | Remove active row/column diff highlighting |
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
Supported for **text**, **integer**, and **decimal/numeric** columns.  
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

- **Filter value** field — numeric columns show a numeric-only text field; text columns accept any string.
- For **BETWEEN**, a second value field appears.
- **Apply** to activate, **Cancel** to dismiss without change.

Numeric columns (INTEGER, SMALLINT, BIGINT, TINYINT, DECIMAL, NUMERIC) use numeric
comparison internally, so `> 100` correctly excludes `99.5` regardless of how many
decimal places the stored value has.

Multiple columns can each have an independent filter active at the same time.  
Filters are combined with AND logic.  
The row count in the status bar updates to reflect how many rows pass all active filters.

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

There are two separate Excel export paths depending on whether you want the full result or just a selection.

#### Full result export

**Toolbar excel icon** or **Options → Run XLS Query** (Ctrl+T from the main query window runs the current query directly to Excel without opening a result window first).

- Exports every visible row (post-filter) and every column in the current display order.
- Writes an `.xlsx` file to the default export path (configured as `SUI.DEFSUIEPATH` in Preferences).
- The file name is auto-generated from the current time: `tHHMMSS.xlsx`.
- The workbook contains two sheets:
  - **Sui-Export** — the data, with a bold header row and numeric types right-aligned.
  - **Sui-Meta** — provenance metadata (see below).
- Numeric columns (`INTEGER`, `BIGINT`, `SMALLINT`, `TINYINT`, `DECIMAL`) are written as proper Excel numbers, not text, so arithmetic and sorting work natively in Excel.
  - Integer format is controlled by the `SUI.XLS.INTFMT` property (default `0`).
  - Decimal format is controlled by the `SUI.XLS.DECFMT` property (default `# ##0.000`).
- The cell font is controlled by the `SUI.XLS.FONT` property (default `Courier`).
- Column widths are auto-sized (for results up to 50 columns wide).
- If `SUI.LAUNCHXLS=Y` is set in Preferences, the file is opened immediately after creation using the command in `SUI.XLSLAUNCHCMD` (default `cmd /c start`). Otherwise, the status bar shows the generated file name.

**Requires the Apache POI library** (`poi-ooxml-*.jar`) on the classpath. If POI is missing, an error dialog appears.

#### Selection export (XLS sel)

Toolbar **XLS sel** button.

Exports only the rows and columns you have selected in the table — not the full result set.

**How to use:**

1. Click a cell, then drag to select a rectangle of rows and columns. Or hold **Ctrl** and click individual rows to build a non-contiguous selection. Or click a column header to select all rows in that column.
2. Click **XLS sel**.
3. The file is written to the same auto-named `.xlsx` in the default export path.

**Behaviour differences from the full export:**

| | Full export | Selection export |
|---|---|---|
| Rows | All visible (post-filter) | Only selected rows |
| Columns | All columns | Only selected columns |
| Header row | Always included | Included only when **Hdr** checkbox is ticked |
| Meta sheet contents | Driver, URL, user, SQL, row count, result-set status | Created-at timestamp and selected-row count only |
| Status bar message | `XLSX file … skapad` | `XLSX selection export: …` |

The **Hdr** checkbox (next to the **Trim** checkbox on the toolbar) controls whether the first row of the selection export contains the column names. It has no effect on the full export (which always writes a header row).

If no cells are selected when **XLS sel** is clicked, an information dialog reminds you to select rows/columns first.

#### Sui-Meta sheet contents (full export)

| Row | Content |
|---|---|
| 0 | Spreadsheet created by / Sui 0.75x |
| 1 | Created at / timestamp |
| 2 | Driver / JDBC driver class name |
| 3 | URL / JDBC connection URL |
| 4 | Userid / database user |
| 5 | SQL-Stmt / the original SQL statement (truncated at 32 000 characters) |
| 6 | Result set status / `full result set` or `partial result set` |
| 7 | Report rows / row count |

#### Preferences properties for Excel

| Property | Default | Description |
|---|---|---|
| `SUI.XLS.FONT` | `Courier` | Cell font for data rows |
| `SUI.XLS.INTFMT` | `0` | Excel number format for integer columns |
| `SUI.XLS.DECFMT` | `# ##0.000` | Excel number format for decimal columns |
| `SUI.DEFSUIEPATH` | (system) | Directory where `.xlsx` files are written |
| `SUI.LAUNCHXLS` | `N` | Set to `Y` to open Excel automatically after export |
| `SUI.XLSLAUNCHCMD` | `cmd /c start` | OS command used to launch Excel when `SUI.LAUNCHXLS=Y` |

---

## Sorting

Click a column header once to select the column, then right-click for **Sort data Ascending** or **Sort data Descending**.

Sorting is performed in-memory on the currently loaded result set. It respects the current filter — only visible rows are reordered.

**Sort columns Ascending** reorders the *columns themselves* alphabetically by name, which can be useful when comparing wide result sets with many columns.

---

## Keyboard shortcuts

| Key | Action |
|---|---|
| Ctrl+Shift+V | Transpose/compare on value |
| Ctrl+D | Show cell data |
| Ctrl+F | Open Find bar |
| Ctrl+Shift+F | Filter on value (from selected cell) |
| Ctrl+G | Go to column |
| Ctrl+L | Transpose selected row |
| Ctrl+C | Copy selected cells |
| Ctrl+H | Highlight row differences from selected cell |
| Ctrl+Shift+H | Highlight column differences from selected cell |
| Ctrl+R | Clear diff highlight |
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

---

## Tabbed Results Window

Sui lets you choose — for each individual result set — whether it lives in its own free-floating window or in a shared **Query Results** tabbed frame. You can move results between the two modes at any time without re-running the query.

### The two modes

| Mode | Description |
|---|---|
| **Free-floating** | Default. Each result opens as its own window that can be moved, resized, and minimised independently. |
| **Tabbed** | The result is hosted as a tab inside the shared *Query Results* frame. Useful when you want several results organised in one place. |

### Opening results in the tabbed frame by default

In **Preferences → Misc**, check **Open results in tabbed view**.

When this preference is on, every new SELECT result is automatically routed into the tabbed frame instead of opening as a standalone window.

### Pulling a free-floating result into the tabbed frame

Every query result toolbar contains a **← (left arrow)** button at the far right.

- Click it to move that result into the tabbed frame.
- The free-floating window disappears; the result reappears as a new tab.
- The ← button hides itself once the result is tabbed.

### The Query Results tabbed frame

The tabbed frame opens automatically the first time a result is pulled in (or when auto-routing is on). It behaves like a normal window.

**Tab header** — each tab shows a short title (connection + timestamp, truncated to 35 characters). Hover the title for the full text as a tooltip. Two inline buttons appear on each tab:

| Button | Action |
|---|---|
| **→** (right arrow) | Release this result back to a free-floating window |
| **×** | Close and discard this result |

**Right-click context menu on a tab:**

| Item | Action |
|---|---|
| Release me | Send the result back to a free-floating window |
| Close | Dispose the result |

**Bottom bar buttons:**

| Button | Action |
|---|---|
| Pull all free results in | Pull every currently open free-floating result into the tabbed frame in one step |
| Free us all | Release every tab back to its own free-floating window |

**Closing the tabbed frame** (window close button or Alt+F4) **closes and disposes all tabs**. Results are not released — they are gone. Use *Free us all* first if you want to keep them.

### Releasing a result back to a free-floating window

Use any of these:

1. Click the **→** button in the tab header.
2. Right-click the tab → **Release me**.
3. Click **Free us all** (releases every tab at once).

After release the result reappears as a standalone window and its ← button becomes visible again.

### Child windows inherit the parent's mode

Several actions open a secondary result window *derived from* the current result:

| Action | Window opened |
|---|---|
| Double-click a row (or Ctrl+L / **Transpose Row**) | Transpose — column names in one column, cell values in the other |
| **F8** in a Transpose window | Transpose of the *next* row in the parent result |
| **F7** in a Transpose window | Transpose of the *previous* row in the parent result |
| Right-click → **Transpose/compare on value** | Side-by-side comparison of all rows sharing the clicked cell's value |
| Right-click → **Transpose/compare selected** | Side-by-side comparison of all rows marked *Sel* |
| Toolbar → **List Columns** | Column metadata table (name, type, length, decimals, nullability) |

**Behaviour:**

- If the parent result is **free-floating**, all secondary windows open as free-floating windows, exactly as they did before.
- If the parent result is **tabbed**, all secondary windows are routed directly into the tabbed frame without ever appearing as a separate window first.

This means that when you are working inside the tabbed frame, transpose views, row comparisons, and the column list all appear as new tabs rather than popup windows scattered on the desktop. You can then use the tab's **→** button to release any of them back to a free-floating window if you want to position it separately.

### Comparing results across both modes

The **Compare** toolbar button works regardless of mode. Both tabbed and free-floating results appear together in the *Open result windows* list of the comparison picker, so you can diff a tabbed result against a free-floating one without changing either window's mode.
