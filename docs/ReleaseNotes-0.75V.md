# Release Notes — Sui 0.75V

**Branch:** `Sui0.75V`  
**Base:** `Sui 0.75U` (Cross-Connection Broadcast, performance fixes, F7/F8 row navigation)  
**Date:** 2026-05-28  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Query Result window | New feature | **Diff highlight — row mode** (Ctrl+H): highlights every cell in the selected row whose value differs from the selected cell |
| Query Result window | New feature | **Diff highlight — column mode** (Ctrl+Shift+H): highlights every cell in the selected column whose value differs from the selected cell |
| Query Result window | New feature | **Clear diff highlight** (Ctrl+R): removes all diff highlighting |
| Query Result window | New feature | Diff highlight respects dark/light theme — deep red background in dark themes, light pink in light themes |
| Query Result window | New feature | **Transpose/compare on value** (Ctrl+Shift+V): transposes all rows where the selected column has the same value as the clicked cell |
| Query Result window | New feature | **F3** closes the current result window or tab (works in both free-floating and tabbed mode) |
| Query Result window | Enhancement | Keyboard shortcuts added to right-click menu: Ctrl+D (Show cell data), Ctrl+Shift+F (Filter on value), Ctrl+G (Go to column), Ctrl+F (Find) |
| Query Result window | Enhancement | Right-click menu items "Find" and "Go to column" added to the context menu with accelerators |
| Query Result window | Bug fix | `ColorRenderer` replaced by `DiffHighlightRenderer` throughout — all filter-apply paths now correctly restore the renderer |
| Tabbed results | Enhancement | Active tab label shown in **bold**; row-limit warning tabs remain bold regardless of selection |
| Broadcast | Bug fix | Schema override now rewrites table references in the SQL via `SqlDialectConverter.applySchema()` instead of injecting a `SET SCHEMA` DDL statement — avoids permission errors and works for all database types |
| Broadcast | Bug fix | `#URL=` directive comment moved to a trailing comment on the same line — fixes a parsing bug where a preceding `--` comment caused `nonSQL` to never fire and `TMPURL` to never be set |
| Broadcast | Enhancement | Checkbox label updated to "Apply per-connection schema qualifier to table references" to accurately reflect the new behaviour |
| Schema management | New feature | **Replace Schema…** added to the right-click editor menu (Additional Edit Functions → Replace Schema…) and to the ShowQryBox toolbar |
| Schema management | Enhancement | Old schema name pre-filled from the first qualified table reference detected in the selection |
| `#URL=` / `RunIt` | Bug fix | `TMPURL` now cleared immediately after switching connection — subsequent statements in the same script reuse the switched connection instead of reconnecting on every statement |
| Version | Bump | `0.75U` → `0.75V` |

---

## Detailed Changes

---

### Diff Highlight in Query Result Window (`QueryRep.java`)

A new cell-level diff highlighting mode makes it easy to spot outliers in a row or column.

Select any cell, then use one of:

| Action | Shortcut | Behaviour |
|---|---|---|
| Highlight row differences | Ctrl+H | All cells in the same row whose value ≠ selected cell are highlighted |
| Highlight column differences | Ctrl+Shift+H | All cells in the same column whose value ≠ selected cell are highlighted |
| Clear diff highlight | Ctrl+R | Removes all highlighting |

The same three actions are also available from the right-click context menu.

The highlight colour adapts to the current Look-and-Feel:
- **Light theme** — light pink (`#FFB4B4`)
- **Dark theme** — deep red (`#8C2828`)

Theme detection uses the luminance of `Panel.background` (threshold 0.5).

The existing `ColorRenderer` has been subclassed into `DiffHighlightRenderer` which is
installed on every column during all table-build and filter-apply paths, replacing the
previous `ColorRenderer` assignments.

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

### Broadcast — Schema Rewrite Instead of SET SCHEMA (`Broadcast.java`)

The previous approach injected a vendor-specific `SET SCHEMA` / `USE` / `SET search_path`
DDL statement before each SQL in the broadcast script. This required execute permission
on that statement and did not work for all database types (e.g. BigQuery, SQLite).

The new approach calls `SqlDialectConverter.applySchema(sql, schema)` to rewrite the SQL
itself: unqualified table references after `FROM`, `JOIN`, `INTO`, `UPDATE`, `TABLE` gain
the schema prefix; existing qualifiers are replaced. No DDL is ever injected.

Additionally, the `-- broadcast: alias` comment was previously emitted on its own line
before `#URL=`. The `nonSQL` parser splits by statement delimiter and then splits by `=`
to detect `#URL`; a leading `--` comment merged into the same token caused the split to
produce `-- broadcast`, which starts with `-` not `#`, so `nonSQL` never triggered and
`TMPURL` was never set. The comment is now placed as a trailing remark on the `#URL=` line
itself, which is safe because `nonSQL` splits `arr[1]` (the URL part) by whitespace and
takes only `keyw[0]` — trailing text is ignored.

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
