# Query Sheets, Tabs and the Sheet List

Sui lets you keep many SQL queries open at the same time, each in its own
**query sheet**. A sheet is a workspace that remembers:

- the SQL text in the editor,
- the timestamp of the last execution,
- (optionally) the connection it was last run on, and
- (optionally) a custom background colour for the tab.

There are two ways to navigate between sheets:

1. The **tab strip** at the bottom of the editor (the "TabbedPane").
2. The **Query Sheet Overview** panel on the right side of the main window.

Both views are kept in sync — switching tabs highlights the matching row in
the Sheet Overview, and clicking a row in the Sheet Overview switches the
active tab.

---

## 1. The tab strip (query sheets)

The tab strip sits at the bottom of the SQL editor.

```
┌──────────────────────────────────────────────────────────────┐
│  SQL editor                                                  │
│                                                              │
│                                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] ...        │
└──────────────────────────────────────────────────────────────┘
```

### Fixed slots, not a "new tab" button

Sui creates a fixed number of sheets at start-up (default **12**). To
change the number, open **File → Preferences → Start up** tab and pick
a new value from the **Number of Sheets** drop-down (6, 12, 18, 24, 30,
36, 48, 60 or 90). The new value is written to `SUI.MAXSHEET` in
`SuiSys.pro` and takes effect on the next start-up.

There is no "new tab" or "close tab" button — every slot is permanent.
To "clear" a sheet, simply select it and delete its SQL.

### Switching sheets

| Method                                         | Effect                                  |
|------------------------------------------------|-----------------------------------------|
| Click a tab in the strip                       | Activates that sheet                    |
| Click a row in the **Query Sheet Overview**    | Activates that sheet                    |
| Drag-and-drop a row in the Sheet Overview      | Reorders the sheets                     |

### Renaming a sheet

Right-click on the tab itself to open the **Change Sheet label** dialog.
You can also rename inline by double-clicking the **Sheet** column in the
Sheet Overview panel (see §3).

### Per-sheet connection memory

If you set `SUI.KEEPSVARS=Y` in `SuiSys.pro` (or tick the corresponding
option in **File → Preferences**), each sheet additionally remembers its
own connection (driver, URL, user). Switching to a sheet restores the
connection that was active the last time it was used. With
`SUI.KEEPSVARS=N` (the default), the current connection stays the same
when you switch sheets.
### Hiding the tab strip

If you prefer to navigate purely from the Sheet Overview, hide the tab
strip via:

- **Options → Query Tabs** (toggles visibility), or
- by setting `SUI.QUERYTABS=N` in `SuiSys.pro`.

The sheets still exist — only the tab row disappears.

### Persistence and recovery

All sheet content is saved automatically to `SuiSheetProp.pro` in your
*SuiHome* folder:

- on shutdown,
- periodically while Sui is running, and
- whenever you switch sheets.

A single-generation backup (`SuiSheetProp.pro.bak`) plus 30 days of
timestamped snapshots under `SuiBup/` protect you against corruption.
See [Profile Recovery](ProFileRecovery.md) for the full procedure.

---

## 2. Show / hide the Query Sheet Overview

- **Options → Query Sheet Overview** (toggles the panel)
- Tick **Show Query Sheet List at startup** under
  **File → Preferences → Start up** to open it automatically (this sets
  `SUI.SHOWSHEETLIST=Y` in `SuiSys.pro`).

The panel docks on the right side of the main window. Note that **the
Sheet Overview and the Favourites bar share the same slot** — only one
of the two can be visible at a time. Showing the Sheet Overview hides
the Favourites bar and vice versa.

---

## 3. Inside the Query Sheet Overview

```
┌── Query Sheet Overview ─────────────┐
│  Find:  [ ____________ ] [Search]   │
│         [ ] AND/OR    [Clear]       │
│ ┌──┬─────────────────┬────────────┐ │
│ │■ │  Sheet          │  Last Run  │ │
│ ├──┼─────────────────┼────────────┤ │
│ │■ │  daily_report   │ 2026-06-06 │ │
│ │  │  cleanup_temp   │ 2026-06-05 │ │
│ │■ │  3              │            │ │
│ │  │  4              │            │ │
│ │  │  ...                          │ │
│ └──┴─────────────────┴────────────┘ │
│        [Reset]  [Clear colours]      │
│        [Close]                       │
└──────────────────────────────────────┘
```

### Columns

| Column     | What it shows                                                        |
|------------|----------------------------------------------------------------------|
| **Colour** | A small swatch. Click to pick a colour for the tab; right-click to clear it. |
| **Sheet**  | The sheet name (defaults to its number). Double-click to rename inline. |
| **Last Run** | Timestamp of the last query execution on this sheet.              |

### Selecting and opening a sheet

- **Single-click** a row to switch the editor to that sheet.
- **Double-click** to do the same explicitly.
- The active row stays highlighted as you click tabs in the strip, and
  scrolls into view when you switch tabs via the keyboard or programmatically.

### Right-click on a row

| Menu item                   | Action                                             |
|-----------------------------|----------------------------------------------------|
| **Open selected tab**       | Switch the editor to that sheet                    |
| **Rename sheet…**           | Prompt for a new name                              |
| **Show content in query box** | Open the SQL of that sheet in a separate window  |

### Reordering sheets

Drag a row up or down to move that sheet. All associated data (SQL text,
timestamp, connection info, colour, name) follows the row. The moved row
is automatically re-selected after the drop.

### Sorting

Click a column header to sort by that column. Sorting is **visual only** —
sheet numbers are unchanged, and selecting a row still opens the correct
sheet. Click **Reset** at the bottom to return to the original tab order.

### Finding sheets by content

Type a term in the **Find** box and press Enter or click **Search**. Rows
whose SQL contains that term are highlighted in yellow. Tick **AND/OR**
to use compound expressions:

- `term1 AND term2` — both terms must appear
- `term1 OR term2` — either term must appear
- `IN (a, b, c)` — any of the listed values

Click **Clear** to remove highlights.

### Buttons at the bottom

| Button          | Effect                                                       |
|-----------------|--------------------------------------------------------------|
| **Reset**       | Clear any active sort and return to tab-order                |
| **Clear colours** | Remove the custom background colour from every tab         |
| **Close**       | Hide the panel (same as the Options menu toggle)             |

Column widths are remembered between sessions.

---

## 4. Bidirectional sync at a glance

```
                     ┌──────────────┐
   click a row  ─▶  │  Sheet List  │  ◀─  switch a tab
                     └──────┬───────┘
                            │  bidirectional
                            ▼
                     ┌──────────────┐
                     │  TabbedPane  │
                     └──────────────┘
```

The link works in both directions and is guarded against infinite echo,
so you can navigate from either side without surprises. Sort or filter
in the Sheet Overview is purely cosmetic — the underlying sheet numbers
stay the same.

---

## 5. Tip: Sheet Overview vs. tab strip

| If you want to…                       | Use…                                  |
|---------------------------------------|---------------------------------------|
| See all sheets in one glance          | Query Sheet Overview                  |
| Search SQL across all sheets          | Query Sheet Overview (Find)           |
| Reorder, recolour or rename sheets    | Query Sheet Overview                  |
| Quickly hop between two sheets        | Click on the tab strip                |
| Save screen real-estate               | Hide the tab strip (Options menu)     |

---

## 6. Result windows — a different kind of tab

The tab strip described above only holds **SQL editor** sheets.
Query **result** windows have their own tab system in the
[Result Window](QueryRepWindow.md) — you can dock multiple results
into one tabbed frame, or release them back to free-floating windows
with the toolbar buttons. The two systems are independent.

---

## Related properties (`SuiSys.pro`)

All of the settings below live in `SuiSys.pro` (in your *SuiHome*
folder). Most of them have a checkbox or drop-down in
**File → Preferences**; you only need to edit the file by hand for the
ones that don't.

| Property                  | Default | Purpose                                           |
|---------------------------|---------|---------------------------------------------------|
| `SUI.MAXSHEET`            | 12      | Number of sheets created at start-up (Preferences → Start up) |
| `SUI.QUERYTABS`           | Y       | Show the tab strip at the bottom of the editor    |
| `SUI.SHOWSHEETLIST`       | N       | Open the Sheet Overview automatically at start-up |
| `SUI.KEEPSVARS`           | N       | Remember a separate connection per sheet          |
| `SUI.DSIZESHEETLIST`      | 200     | Width of the Sheet Overview panel                 |
| `SUI.DSIZESHEETCOL.1`     | 80      | Width of the **Sheet** column                     |
| `SUI.DSIZESHEETCOL.2`     | 90      | Width of the **Last Run** column                  |
| `SUI.TABCOLOR.<n>`        | —       | Background colour of sheet *n* (`#RRGGBB`)        |

---

## See also

- [Main window layout](MainWindowLayout.md)
- [Profile recovery](ProFileRecovery.md)
- [Result window](QueryRepWindow.md)
- [Inline directives](InlineDirectives.md)
