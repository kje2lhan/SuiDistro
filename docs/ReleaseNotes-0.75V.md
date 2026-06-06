# Release Notes — Sui 0.75V

**Branch:** `Sui0.75V`  
**Base:** `Sui 0.75U` (Cross-Connection Broadcast, performance fixes, F7/F8 row navigation)  
**Date:** 2026-05-28 (initial); last updated 2026-06-06  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Query Result window | New feature | **Diff highlight — row mode** (Ctrl+H): select one or more rows; every cell in those rows whose value differs from the anchor column is highlighted |
| Query Result window | New feature | **Diff highlight — column mode** (Ctrl+Shift+H): select one or more columns; every cell in those columns whose value differs from the anchor row is highlighted |
| Query Result window | New feature | **Clear diff highlight** (Ctrl+R): removes all diff highlighting |
| Query Result window | New feature | Diff highlight respects dark/light theme — deep red background in dark themes, light pink in light themes |
| Query Result window | New feature | **Transpose/compare on value** (Ctrl+Shift+V): transposes all rows where the selected column has the same value as the clicked cell |
| Query Result window | New feature | **F3** closes the current result window or tab (works in both free-floating and tabbed mode) |
| Query Result window | Enhancement | Keyboard shortcuts added to right-click menu: Ctrl+D (Show cell data), Ctrl+Shift+F (Filter on value), Ctrl+G (Go to column), Ctrl+F (Find) |
| Query Result window | Enhancement | Right-click menu items "Find" and "Go to column" added to the context menu with accelerators |
| Query Result window | Bug fix | `ColorRenderer` replaced by `DiffHighlightRenderer` throughout — all filter-apply paths now correctly restore the renderer |
| Query Result window | Enhancement | **Copy selected data** now includes column headers as first row when **Hdr** is checked (consistent with CSV and XLS export) |
| Tabbed results | Enhancement | Active tab label shown in **bold**; row-limit warning tabs remain bold regardless of selection |
| Broadcast | Bug fix | Schema rewrite uses same regex logic as editor Add Schema / Replace Schema — detects whether SQL has existing qualifiers and either adds or replaces accordingly; no JSQLParser dependency |
| Broadcast | Bug fix | Statement delimiter moved to before the `--` broadcast comment — `RemComm` was stripping the delimiter with the comment text, merging the `#URL=` token and the SQL so RunIt never executed the query |
| Broadcast | Enhancement | Checkbox label updated to "Apply per-connection schema qualifier to table references" to accurately reflect the new behaviour |
| Schema management | New feature | **Replace Schema…** added to the right-click editor menu (Additional Edit Functions → Replace Schema…) and to the ShowQryBox toolbar |
| Schema management | Enhancement | Old schema name pre-filled from the first qualified table reference detected in the selection |
| `#URL=` / `RunIt` | Bug fix | `TMPURL` now cleared immediately after switching connection — subsequent statements in the same script reuse the switched connection instead of reconnecting on every statement |
| Query Result window | New feature | **Freeze column** / **Unfreeze all columns** — pin one or more columns into a row-header pane that stays visible while scrolling horizontally; right-click any frozen header to unfreeze just that column |
| Query Result window | New feature | **Choose visible columns…** dialog (column right-click menu) with Select all / Deselect all buttons |
| Query Result window | New feature | **Re-run Query** (F5) and **Re-run to Compare** added to the action menu |
| Query Result window | New feature | **Copy as Markdown table** added to the right-click menu |
| Query Result window | Enhancement | Sticky sort — re-running a query reapplies the sort that was active in the previous result window |
| Query Result window | Bug fix | `SuiSortAdapter` now bounds-checks `getValueAt` / `setValueAt` so a model-shrink event between rebuilds no longer triggers `ArrayIndexOutOfBoundsException` during repaint |
| Query Result window | Performance | `ColorRenderer` caches stripe / odd-row colours per L&F — no per-cell `UIManager.getColor` or `Color` allocation |
| Query Result window | Performance | `SuiSortAdapter.sort()` reimplemented as primitive `int[]` mergesort — no `Integer` boxing, no `Comparator` allocation; fast-path skip when the input is already ordered |
| Query Result window | Performance | `FixedAdapter` (row-number column) no longer holds a `Vector<Vector>` — values are computed on the fly so filter / sort no longer rebuild it |
| Query Sheet List | Enhancement | Bidirectional sync — selecting a row in the Query Sheet List now switches the active tab; switching tabs (clicks or `Ctrl+PgUp/PgDn`) now highlights and scrolls to the matching row |
| `Sui.ini` | Enhancement | Trailing semicolon on `SuiHome=<folder>` is now optional; new alias `&current_folder` (synonym for `&current_path`) |
| RunIt | Performance | Unbounded result sets (`MaxRows=0`) grow an `ArrayList<String[]>` instead of pre-allocating a `String[500000][]` — saves ~400 MB of placeholder references for small result sets |
| RunIt | Bug fix | Confirm-change-to-database dialog and SymbRes substitution-variable dialog are now shown via `SwingUtilities.invokeAndWait` from the worker thread (previously constructed off the EDT) |
| ConnDB | Performance / safety | Connection cache wrapped in `Collections.synchronizedMap`; cached BigQuery entries are re-validated with `isValid(2)` on every `getConn()` and silently re-connected if stale |
| ExpXLS | Performance | Column class names cached outside the row loop in both full-export and selected-cells paths — eliminates `getColumnClass(j).getName().trim()` per cell |
| QryMon | Bug fix | Query Monitor result window is created on the EDT via `SwingUtilities.invokeLater` |
| TableComboBox | Bug fix | Filter validation no longer reports *"Value specified but no operator"* when only an operator (e.g. `Is Null`) is set — corrupt `Opf =!Valf` assignment removed |
| `connP` | Bug fix | Driver lookup loop now starts at index 0 (was 1); `sid` is correctly defaulted to `"null"` instead of overwriting `port`; `j` no longer reset to 0 inside the alias-rewrite loop |
| Docs | Enhancement | **DB2 — Common JDBC Properties** and **DB2 — SSL / TLS Setup** sections added to [ConnManager.md](ConnManager.md), with full property reference (`clientProgramName`, `retrieveMessagesFromServerOnGetMessage`, `timestampFormat`, `sslConnection`, `sslTrustStoreType=Windows-ROOT`, …) and step-by-step SSL setup |
| Docs | Enhancement | **BigQuery — Common JDBC Properties** section added to [ConnManager.md](ConnManager.md) — covers `OAuthType` (with strong recommendation for value `1` / interactive browser OAuth), `EnableSession`, `Location`, and a first-connect walkthrough |
| Docs | Enhancement | [SuiHome.md](SuiHome.md) updated for the optional trailing semicolon and the `&current_folder` alias |
| Docs | Enhancement | [ConnManager.md](ConnManager.md) JDBC Properties section rewritten to explain specific vs. generic prefix matching and the longest-prefix-wins precedence rule |
| In-app help | New feature | New reusable `HelpDialog` renders Markdown docs (`docs/*.md`) inside the app — supports headings, fenced code, inline code, bold/italic, lists, blockquotes, tables, internal `.md` cross-links (open in a new help popup) and external `http`/`mailto` links (open in the system browser) |
| In-app help | New feature | **Info** buttons added to **Connection Manager**, **Query Result Window** and **Result Set Compare** — open the matching help page (`ConnManager.md`, `QueryRepWindow.md`, `ResultSetCompare.md`) |
| In-app help | New feature | **Help…** entry added to the query editor right-click popup (top-level) and to its **Additional Edit functions** submenu — opens [AdditionalEditFunctions.md](AdditionalEditFunctions.md) |
| In-app help | New feature | Main menu **Help** extended with **Query Sheets & Tabs…**, **Inline Directives…** and **Profile Recovery…** — each opens the matching doc in a popup |
| Docs | New | [QuerySheetsAndTabs.md](QuerySheetsAndTabs.md) — user-oriented guide to query sheets, the tab strip and the Query Sheet Overview (creating/renaming/colouring sheets, drag-and-drop reorder, search with AND/OR/IN, bidirectional sync between tabs and Sheet List, per-sheet connection memory, all related `SuiSys.pro` properties) |
| Docs | New | [README.md](../README.md) rewritten as a short user-oriented landing page (highlights, supported databases, getting started linking to the prebuilt jar at <https://github.com/kje2lhan/SuiDistro>, a typical session, version history); the previous developer-oriented README is preserved as [Changelog.md](Changelog.md) |
| Build | Enhancement | `docs/*.md` is now bundled into the assembly jar under `/docs/` so the in-app help works from a clean install with no external files; `HelpDialog` still falls back to `./docs/<name>.md` on disk for development runs |
| Version | Bump | `0.75U` → `0.75V` |

---

## Detailed Changes

---

### Diff Highlight in Query Result Window (`QueryRep.java`)

A new cell-level diff highlighting mode makes it easy to spot outliers in a row or column.

Select one or more cells, then use one of:

| Action | Shortcut | Behaviour |
|---|---|---|
| Highlight row differences | Ctrl+H | Select one or more rows (any columns). The **first selected column** is the anchor. Every other cell in each selected row is highlighted if its value differs from the anchor column's value in that same row. |
| Highlight column differences | Ctrl+Shift+H | Select one or more columns (any rows). The **first selected row** is the anchor. Every other cell in each selected column is highlighted if its value differs from the anchor row's value in that same column. |
| Clear diff highlight | Ctrl+R | Removes all highlighting |

The same three actions are also available from the right-click context menu.

The highlight colour adapts to the current Look-and-Feel:
- **Light theme** — light pink (`#FFB4B4`)
- **Dark theme** — deep red (`#8C2828`)

Theme detection uses the luminance of `Panel.background` (threshold 0.5).

The existing `ColorRenderer` has been subclassed into `DiffHighlightRenderer` which is
installed on every column during all table-build and filter-apply paths, replacing the
previous `ColorRenderer` assignments. The anchor value is looked up per-cell at render
time via `table.getValueAt()` so multi-row and multi-column selections all compare
against the correct reference value.

---

### Transpose/Compare on Value (Ctrl+Shift+V)

Opens transpose views for all rows where the value in the selected column matches the
clicked cell value. Uses the existing `TraverseOnValue` mechanism with mode `"Value"`.
Also accessible from the right-click menu as "Transpose/compare on value".

---

### F3 Close Window/Tab

Pressing **F3** in any Query Result window:
- **Free-floating mode** — disposes the window and removes it from the open-windows registry
- **Tabbed mode** — closes the tab via `QueryRepTabbedFrame.closeByQR()`

---

### Keyboard Shortcuts in Right-click Menu

The following shortcuts, previously only available via input-map bindings, are now also
shown as accelerators in the right-click context menu:

| Menu item | Shortcut |
|---|---|
| Show cell data | Ctrl+D |
| Find | Ctrl+F |
| Go to column | Ctrl+G |
| Filter on value | Ctrl+Shift+F |
| Transpose/compare on value | Ctrl+Shift+V |
| Highlight row differences | Ctrl+H |
| Highlight column differences | Ctrl+Shift+H |
| Clear diff highlight | Ctrl+R |

---

### Active Tab Bold Label (`QueryRepTabbedFrame.java`)

A `ChangeListener` on the tabbed pane calls `TabHeader.setSelected(bool)` on every tab
header whenever the selection changes. The selected tab's label is drawn in **bold**
(`Font.BOLD, 11f`); all others are plain. Tabs with a row-limit warning (⚠ prefix) are
always bold so the orange warning colour remains visually prominent.

---

### Copy Selected Data — Column Headers (`QueryRep.java`)

When the **Hdr** checkbox in the toolbar is ticked, the **Copy selected data** action
(both right-click context menu and the action popup) now prepends a header row containing
the selected column names, space-separated, before the data rows. This matches the
existing behaviour of the CSV and XLS export buttons.

---

### Broadcast — Schema Rewrite (`Broadcast.java`)

The schema application logic has been replaced with the same regex approach used by
**Add Schema** and **Replace Schema** in the SQL editor:

- If the SQL already contains qualified references (`schema.table` after
  `FROM`/`JOIN`/`INTO`/`UPDATE`/`TABLE`): all existing schema qualifiers are **replaced**
  with the per-connection schema.
- If the SQL has no qualified references: the schema is **added** as a prefix to every
  unqualified table name.

This is purely string/regex based — no JSQLParser dependency, no parse failures on
complex or vendor-specific SQL.

**Bug fix — delimiter ordering:** The generated `#URL=` line previously placed the
statement delimiter after the `-- broadcast:` comment:
```
#URL=jdbc:...  -- broadcast: ALIAS;
```
`RunSql` passes the script through `RemComm` (comment stripper) before handing it to
`RunIt`. `RemComm` strips from `--` to end-of-line, which deleted the `;` delimiter.
`SqlSplit` then merged the `#URL=` token and the following SQL into one statement; that
combined statement was detected as a `#`-directive and processed by `nonSQL` — the SQL
was never executed.

The delimiter is now placed immediately after the URL, before the comment:
```
#URL=jdbc:...;  -- broadcast: ALIAS
```
`RemComm` strips the `--` tail but leaves the `;`, so `SqlSplit` correctly produces
two separate tokens: the `#URL=` directive and the schema-adjusted SQL statement.

---

### Replace Schema (`QryPop.java`, `ShowQryBox.java`)

A new **Replace Schema…** action replaces one schema qualifier with another across all
qualified table references in the selected SQL (or the full editor/viewer content when
nothing is selected).

- Available in: right-click menu → Additional Edit Functions → **Replace Schema…**
- Available in: ShowQryBox toolbar as a **Replace Schema…** button

A two-field dialog prompts for the old and new schema names. The old schema is
pre-filled by scanning the text for the first occurrence of
`FROM|JOIN|INTO|UPDATE|TABLE schema.table` and extracting the schema name.

The replacement is case-insensitive and covers references after `FROM`, `JOIN`, `INTO`,
`UPDATE`, and `TABLE` keywords.

---

### `#URL=` Connection Reuse Fix (`RunIt.java`)

After successfully switching to a `#URL=` target, `TMPURL` is now immediately cleared.
Previously, `TMPURL` remained set after the first switch, so every subsequent statement
in the same script re-entered the connection-switch block, closing and reopening the
`DatabaseManager` on each iteration. This caused any session-level state (schema, temp
tables, transaction context) to be lost between statements. With `TMPURL` cleared, the
switched connection is reused for all following statements until the next `#URL=`.

---

### Freeze Columns in Query Result Window (`QueryRep.java`)

A new **Freeze column** action pins the currently-selected column into a row-header
pane on the left side of the result `JScrollPane`. The pane shares vertical scrolling,
row selection, font and row height with the main table; frozen columns stay on screen
while the main table scrolls horizontally.

| Action | Where | Behaviour |
|---|---|---|
| Freeze column | Right-click a column header → **Freeze column** | Moves the column out of the main table and into the row-header pane (next to the `#` column). Width, sort state and renderer are preserved. |
| Unfreeze one | Right-click a *frozen* column header → **Unfreeze "name"** | Restores the column to (approximately) its original view-index in the main table. |
| Unfreeze all | Right-click any column header → **Unfreeze all columns** | Restores every frozen column in ascending original view-index order. |

A subtle accent-coloured divider on the right edge of the row-header makes the boundary
between frozen and scrolling columns visible. The divider is only shown when at least
one column is frozen. Sort, filter and the diff-highlight renderer all see the full
logical column set, so frozen columns participate in every operation exactly as if
they were still in the main table.

---

### Choose Visible Columns (`QueryRep.java`)

A new **Choose visible columns…** entry in the column right-click menu opens a
checkbox-grid dialog listing every column the result set originally produced. Use it to
re-show columns previously removed with **Hide column** without having to undo each one
individually, or to hide multiple columns in one operation.

The dialog has **Select all** / **Deselect all** buttons. Hidden columns retain their
position, width, sort state, and frozen / pinned state — they are simply removed from
the `TableColumnModel` and re-inserted when re-shown.

---

### Re-run Query (F5) and Re-run to Compare (`QueryRep.java`)

Two new entries in the action menu:

| Action | Shortcut | Behaviour |
|---|---|---|
| **Re-run Query** | F5 | Re-executes the SQL that produced this result against the same connection, in a new result window. The current sort column and direction are remembered and re-applied to the new window once it is loaded (sticky sort). |
| **Re-run to Compare** | (menu only) | Re-executes the SQL and feeds both the existing and new result through `RunItDiff`, opening the ResultSet Compare view side-by-side. |

`Re-run to Compare` accepts a credentials prompt if the original connection's password
is no longer in memory. The diff title is auto-generated as `<original> <-> <original>
(re-run)`.

---

### Copy as Markdown Table (`QueryRep.java`)

A new **Copy as Markdown table** entry in the right-click menu copies the current
selection (or whole result set) to the clipboard as a GitHub-flavoured Markdown table —
column headers, the `|---|---|` separator row, and pipe-separated cell values. Useful
for pasting query output into issue trackers, pull request descriptions, or any
Markdown-aware document.

---

### Query Sheet List ↔ Tab Sync (`QuerySheetListPanel.java`, `TabbedPaneClassic.java`, `Sui.java`)

The Query Sheet List panel now stays in sync with the tabbed pane in **both**
directions:

- **Row → tab.** Clicking a row in the Sheet List switches the active query tab to
  that sheet.
- **Tab → row.** Selecting a tab in the `TabbedPane` (mouse click, `Ctrl+PgUp`/`PgDn`,
  programmatic navigation) highlights and scrolls the matching row in the Sheet List
  into view.

Both directions are guarded by a `syncingFromTab` re-entry flag so the two listeners
never echo back into an infinite loop. Sort and filter applied to the Sheet List are
honoured — the highlighted row is the one whose model index matches the active tab.

A new `Sui.highlightSheetInList(int)` helper is the single entry point used by
`TabbedPaneClassic` to push the highlight to the panel only when the panel is currently
visible.

---

### `Sui.ini` — Optional Semicolon and `&current_folder` (`Sui.java`, `docs/SuiHome.md`)

The `SuiHome=<folder>` directive in `Sui.ini` is more forgiving:

- The **trailing semicolon is optional.** `SuiHome=C:\SuiData` and
  `SuiHome=C:\SuiData;` are both accepted.
- When a semicolon **is** present, any text after it is treated as a comment and
  ignored — so `SuiHome=C:\SuiData ; my desktop install` still works.
- The value is trimmed of leading/trailing whitespace before use.
- The new alias **`&current_folder`** is an exact synonym of `&current_path` — both
  resolve to the directory Sui was started from (`user.dir`) without any
  `File.isDirectory()` check.

The change preserves full backwards compatibility — every previously-valid `Sui.ini`
still parses identically.

---

### Performance: ColorRenderer Cell Painting (`ColorRenderer.java`)

`ColorRenderer.getTableCellRendererComponent` previously called `UIManager.getColor`
multiple times **per cell paint** to compute the alternate-row stripe colour. With
large result sets that means thousands of map lookups and `Color` allocations every
time the table scrolls or repaints.

The renderer now caches the stripe / odd-row colours in instance fields and invalidates
the cache only when the `Panel.background` or `Table.background` reference changes
(i.e. on a Look & Feel switch). Steady-state cell paint is now two field reads and one
`setBackground` call.

---

### Performance: Primitive Mergesort in SuiSortAdapter (`SuiSortAdapter.java`)

`SuiSortAdapter.sort()` previously boxed every row index into an `Integer[]`, allocated
a `Comparator<Integer>` (and a `Collections.reverseOrder()` wrapper for descending sort),
and called `Arrays.sort` on the boxed array. For large result sets that meant tens of
thousands of `Integer` allocations and a comparator-callback per comparison.

The sort is now a primitive `int[]` top-down mergesort that operates directly on the
`ix[]` index array using a single `int[] aux` scratch buffer. A fast-path skips the
merge when the two halves are already in order. The same `compareVals()` helper handles
numeric vs. string comparison and applies the `reverse` flag in the merge loop.

In addition, the adapter now remembers the most recent sort column and direction
(`lastSortCol` / `lastSortDir`) and exposes them via package-private getters — used by
the new **Re-run Query** sticky-sort feature.

---

### Performance: FixedAdapter as Computed Row-Number Model (`FixedAdapter.java`)

The `#` (row-number) column previously stored its own `Vector<Vector<Object>>` and
called `bldTab()` to refill that vector every time the data changed (every filter,
every re-sort, every model swap). For a 100 000-row result set that meant allocating
100 000 single-element vectors on every filter apply.

`FixedAdapter` is now a stateless `AbstractTableModel` that holds only the row count
and computes `getValueAt(row, col)` on the fly as `String.valueOf(row + 1)`. The
vector is gone, `bldTab()` is now just a row-count update plus a model-changed event,
and `setValueAt()` is a no-op (the row-number column is logically read-only). Memory
and CPU savings scale linearly with row count.

---

### Performance: Unbounded Result Sets Grow Dynamically (`RunIt.java`)

When `MaxRows` is 0 (no row limit), `RunIt` previously pre-allocated a
`String[500000][col + 1]` array up-front. For small result sets (a few hundred rows)
that is ~400 MB of dead `String[]` slots per query, all retained until the result
window closes.

The default fetch branch now allocates an `ArrayList<String[]>` (initial capacity
1024), appends one `String[col + 1]` per row as `ResultSet.next()` advances, and
finally collapses the list into the `cData` array with `toArray(new String[0][])`.
Bounded result sets (`MaxRows > 0`) continue to use the pre-allocated array because
the row count is known up-front.

---

### Performance / Safety: ConnDB Cache (`ConnDB.java`)

Two changes:

- The static `connCache` `LinkedHashMap` is now wrapped in
  `Collections.synchronizedMap`. `evictStaleBigQueryConnections()` and
  `closeAllConnections()` now operate inside `synchronized (connCache) { … }` blocks
  so concurrent `getConn()` calls from background `RunIt` threads cannot mutate the
  map mid-iteration.
- Cached BigQuery entries are now re-validated with `conn.isValid(2)` on **every**
  `getConn()` call, not just when first inserted. A stale entry (network blip, server
  idle-timeout) is silently evicted and a fresh connection is opened, so the user
  never sees a misleading *"Connection closed"* exception from a long-lived cache hit.
- `ConnInfo.valid` is now `volatile` so the validity flag is visible across threads
  without further locking.

---

### Performance: ExpXLS Column-Class Caching (`ExpXLS.java`)

In the rare path where `cTypes == null` (the SQL types are unknown), `ExpXLS` was
calling `table.getColumnClass(j).getName().trim()` inside the per-cell loop to decide
whether a column should be exported as a number or a string. For a 10 000-row × 30-col
export that's 300 000 reflective class-name lookups.

Both the full-export and selected-cells paths now pre-cache the column class names in
a `String[]` outside the row loop and read from the cache per cell.

---

### Bug fix: RunIt Confirm Dialogs and SymbRes on EDT (`RunIt.java`)

`RunIt.run()` executes on a worker thread. Two interactive prompts were previously
constructed and shown from that worker thread, which is a Swing thread-safety
violation:

- The *"Press OK to confirm change of N row(s)"* dialog after a DML statement.
- The `SymbRes` substitution-variable dialog when `Sui.GetSymbRes()` is true.

Both are now shown via `SwingUtilities.invokeAndWait` from the worker thread. The
worker blocks on the EDT round-trip, captures the user's choice into an
`AtomicInteger` / `AtomicReference`, and continues. Behaviour is unchanged for the
user; the work just happens on the correct thread.

`QryMon` similarly now opens its result window on the EDT via `SwingUtilities.invokeLater`.

---

### Bug fix: TableComboBox Filter Validation (`TableComboBox.java`)

The filter-row validator contained a corrupt nested condition:

```java
if (Opf =!Valf)   // assignment, not comparison
{
    if (op.equals("Is Null") || op.equals("Is Not Null")) ;
    else m = "Operator specified but no value";
}
```

The assignment `Opf =!Valf` rewrote `Opf` to `!Valf` and always evaluated to *true*
when `Valf` was false, so the validator reported *"Value specified but no operator"*
in cases where only an operator was entered. The nested condition has been simplified
to a straight `if (!Valf)` check and the corrupt assignment removed.

---

### Bug fix: connP Driver Lookup and SID Default (`connP.java`)

Three small but visible bugs in the connection-property handling:

- The driver lookup loop started at index 1, so the first driver entry (`drid[0]`)
  was never matched. Loop now starts at 0.
- A typo `if (sid == null) port = "null";` was overwriting `port` with the literal
  string `"null"` whenever the SID was missing — fixed to `sid = "null";`.
- In the alias-rewrite loop, the index counter `j` was being reset to 0 on every
  iteration, which sometimes duplicated entries in the rewritten property file. `j` is
  now initialised once before the loop.

---

### Documentation — JDBC Properties, DB2, BigQuery, SuiHome (`docs/*`)

[docs/ConnManager.md](ConnManager.md) has been substantially expanded:

- **JDBC Properties section rewritten** to explain the two prefix levels — *specific*
  (full URL prefix, applies to one connection) and *generic* (driver prefix only,
  applies to every connection of that driver) — and the longest-prefix-wins precedence
  rule.
- **DB2 — Common JDBC Properties** reference table added with `clientProgramName`,
  `deferPrepare`, `retrieveMessagesFromServerOnGetMessage`, `timestampFormat`,
  `timestampPrecisionReporting`, `useJDBC4ColumnNameAndLabelSemantics`, plus
  generic / specific examples and a recommendation block.
- **DB2 — SSL / TLS Setup** section added: minimum two-property setup
  (`sslConnection=true` + `sslTrustStoreType=Windows-ROOT`), an explanation of why
  `Windows-ROOT` is the path of least resistance on Windows, and full step-by-step
  guidance.
- **BigQuery — Common JDBC Properties** section added with `OAuthType`,
  `EnableSession`, `Location`, including a six-step *first connect with `OAuthType=1`*
  walkthrough and the strong recommendation to prefer interactive browser OAuth on
  desktop installs.

[docs/SuiHome.md](SuiHome.md) updated to document the optional trailing semicolon on
`SuiHome=<folder>` and the new `&current_folder` alias.

---

### In-App Help System (`HelpDialog.java`, `ConnManager.java`, `QueryRep.java`, `DiffRep.java`, `QryPop.java`, `Sui.java`, `pom.xml`)

Sui now ships with a built-in help viewer so users can read the documentation
without leaving the application.

**`HelpDialog`** is a small reusable modeless dialog (920 × 720, JScrollPane).
It loads a Markdown document by name, converts it to HTML on the fly and
renders it through a `JEditorPane` configured with `text/html` content type
and `HONOR_DISPLAY_PROPERTIES`, so the help text adapts to the active FlatLaf
theme.

The Markdown → HTML converter is intentionally minimal but covers everything
the Sui docs use:

- ATX headings `#` … `######`
- Fenced code blocks ``` ``` ``` with HTML escaping
- Inline `code`, **bold**, *italic* / _italic_
- Unordered (`-`, `*`) and ordered (`1.`) lists
- Block quotes (`>`), horizontal rules (`---`)
- Pipe tables `| a | b |` with a `-:|` separator row turning row 0 into `<th>`
- Inline links `[text](href)`

Document lookup tries the classpath first (`/docs/<name>.md`) and then falls
back to `./docs/<name>.md` on the filesystem, so the dialog works both from a
clean jar install and from a development checkout. `pom.xml` now bundles
`docs/*.md` into the assembly jar under `/docs/`.

Link handling:

| Link target | Behaviour |
|---|---|
| Another `.md` file | Opens recursively in a new `HelpDialog` |
| `http(s)://…`      | Opens in the system browser via `Desktop.browse` |
| `mailto:…`         | Opens in the system mail client |

**Wired into the UI:**

- **Connection Manager** — info button at the bottom-left of the dialog →
  [ConnManager.md](ConnManager.md).
- **Query Result Window** — info button at the right end of the toolbar →
  [QueryRepWindow.md](QueryRepWindow.md).
- **Result Set Compare** — info button at the end of the toolbar →
  [ResultSetCompare.md](ResultSetCompare.md).
- **Query editor right-click popup (`QryPop`)** — top-level **Help…** entry
  and a second **Help…** entry inside the **Additional Edit functions**
  submenu → [AdditionalEditFunctions.md](AdditionalEditFunctions.md).
- **Main menu — Help** — three new entries above **About…**:
  - **Query Sheets & Tabs…** → [QuerySheetsAndTabs.md](QuerySheetsAndTabs.md)
  - **Inline Directives…** → [InlineDirectives.md](InlineDirectives.md)
  - **Profile Recovery…** → [ProFileRecovery.md](ProFileRecovery.md)

Because the converter follows internal links, clicking any `[other doc.md]`
reference inside a help popup opens a fresh window on that document — the
user can navigate the whole `docs/` folder without ever leaving the app.

---

### New User-Oriented Documentation (`docs/QuerySheetsAndTabs.md`, `README.md`, `docs/Changelog.md`)

A new user-facing guide [QuerySheetsAndTabs.md](QuerySheetsAndTabs.md)
explains how the query sheets, the tab strip and the **Query Sheet Overview**
panel work together. It covers:

- Fixed sheet slots and how to change the count from
  **File → Preferences → Start up → Number of Sheets**
  (writes `SUI.MAXSHEET` in `SuiSys.pro`).
- Renaming sheets (right-click on the tab or inline edit in the overview),
  per-sheet connection memory (`SUI.KEEPSVARS`), hiding the tab strip
  (`Options → Query Tabs` / `SUI.QUERYTABS`).
- The Sheet Overview panel — columns (colour swatch, sheet name, last-run
  timestamp), drag-and-drop reordering, sort by header, find with
  AND / OR / IN logic, right-click menu, the bottom buttons (Reset / Clear
  colours / Close).
- The bidirectional synchronisation between the Sheet List and the tab
  strip, with the explicit note that sort/filter is cosmetic only.
- The mutual-exclusivity of the Sheet List and the Favourites bar in the
  right-side wrapper.
- A clear distinction from the **Result-window** tab system
  (`QueryRepTabbedFrame`), which is independent of the editor sheet tabs.
- A reference table of all related properties in `SuiSys.pro`.

The top-level [README.md](../README.md) has been rewritten as a short,
user-oriented landing page: a tagline, "What Sui is good at", a highlights
table linking into `docs/`, a list of supported databases, a *Getting
started* section pointing to the prebuilt jar at
<https://github.com/kje2lhan/SuiDistro> (no build instructions — Sui is not
on a public source-code git repo), a typical-session walkthrough,
*Customising Sui*, a project structure overview, version history (one row
per `ReleaseNotes-0.75*.md`), reporting issues, and licence.

The previous developer-oriented README — with per-version highlight bullets
going all the way back to the earliest releases — has been preserved as
[Changelog.md](Changelog.md) and is reachable from the new README.
