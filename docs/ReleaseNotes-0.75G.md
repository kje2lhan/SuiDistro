# Release Notes — Sui 0.75G

**Branch:** `Sui0.75G`  
**Base:** `Sui 0.75F` (SQL Object Tree)  
**Date:** 2026-04-25  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| SQL Editor | New feature | Toggle Comment on selected lines (Ctrl+7) |
| SQL Editor | New feature | Go to Line dialog (Ctrl+G) |
| SQL Editor | New feature | Block Indent / Unindent (Tab / Shift+Tab with selection) |
| SQL Editor | New feature | Uppercase / Lowercase Selection (Ctrl+Shift+U / Ctrl+Shift+L) |
| SQL Editor | New feature | Parenthesis matching highlight — enable/disable from right-click menu |
| SQL Editor | New feature | Cursor position indicator (Ln / Col) displayed above query tabs |
| SQL Object Tree | Enhancement | Schema / Table filter fields with titled border |
| SQL Object Tree | Enhancement | Better icons — table grid for SQL Tree, pages for Query Tree toolbar buttons |
| SQL Object Tree | Enhancement | Frame icon switches between `db.gif` (SQL tree) and `pages.gif` (file tree) |
| Query Editor popup | New feature | "Build IN List from Selection" — converts selected values to SQL `IN (…)` clause |
| Query Editor popup | New feature | "Copy Columns from Selection…" — extracts fixed-position column range to clipboard |
| Query Report popup | New feature | "Copy WHERE clause from row" — builds `WHERE col = val AND …` from the selected row |
| Bug fix | Fix | Status message not cleared before showing "Columns copied to clipboard" |

---

## Detailed Changes by Area

---

### SQL Editor — New Editing Operations

Six new editing operations are available both via the **Edit** menu and via keyboard shortcuts.  
All of them operate on the currently selected text (expanded to full lines where needed).

#### Toggle Comment — Ctrl+7

Adds or removes the database-specific line comment prefix (`--` for SQL) from every
selected line. If all non-empty lines already start with the prefix the action
**removes** them (uncomment); otherwise it **adds** them (comment).

- Works on a single line (no selection needed) or on a multi-line block.
- Menu item: **Edit → Toggle Comment** with accelerator Ctrl+7.

#### Go to Line — Ctrl+G

Prompts for a line number and moves the caret to the first character of that line.  
Clamps to the first/last line if the value is out of range.

- Menu item: **Edit → Go to Line…** with accelerator Ctrl+G.

#### Block Indent / Unindent — Tab / Shift+Tab

When text is selected, Tab indents every line in the block by 4 spaces and Shift+Tab
removes up to 4 spaces (or a single tab character) from the beginning of each line.
The selection is preserved and adjusted to cover the same lines after the operation.

- Tab with no selection still inserts a literal tab character (unchanged behaviour).
- Menu items: **Edit → Indent Block** / **Edit → Unindent Block**.

#### Uppercase / Lowercase Selection — Ctrl+Shift+U / Ctrl+Shift+L

Converts the selected text to upper-case or lower-case in place.

- Menu items: **Edit → Uppercase Selection** / **Edit → Lowercase Selection**.

---

### SQL Editor — Parenthesis Matching Highlight

A new **Enable / Disable Paren Matching** toggle is available in the right-click
context menu. When enabled, the bracket under or immediately before the caret and its
matching bracket are highlighted in real time as the caret moves.

- Color adapts to the active theme: blue on dark themes, yellow on light themes.
- Matching walks the full document, correctly handling nested brackets.
- The listener is built once at startup but only registered when the feature is enabled,
  so there is no performance cost when it is off.
- State is stored in `Sui.ParenHighLightOn`; helpers `enableParenHighLight()` /
  `disableParenHighLight()` add / remove the `CaretListener` and clean up stale
  highlights on disable.

---

### SQL Editor — Cursor Position Indicator

A compact label showing **Ln _n_, Col _n_** is displayed in a strip directly above
the tabbed query sheets. It updates on every caret move via a dedicated
`CaretListener`.

- Implemented as a `JLabel` (`cursorPosLabel`) wrapped with the `TabbedPane` in a new
  `tabbedWrapper` `JPanel` (BorderLayout: NORTH = label, CENTER = TabbedPane).
- Uses 11 pt plain font with a small left/right inset for readability.

---

### SQL Object Tree — Enhancements

#### Schema / Table Filter — Titled Border

The two filter fields at the top of `SQLTreePanel` are now enclosed in a titled border
reading **"Schema / Table Filter"**, making the purpose of the fields immediately clear.

```java
JPanel filterRow = new JPanel(new GridLayout(2, 2, 2, 1));
filterRow.setBorder(BorderFactory.createTitledBorder("Schema / Table Filter"));
```

#### Improved Toolbar Icons

| Button | Old icon | New icon | Rationale |
|---|---|---|---|
| Show SQL Object Tree | `schema.gif` | `selecttable_16x16.png` | Table-grid icon is unambiguous |
| Show Query File Tree | `find.png` | `pages.gif` | Stacked-pages icon clearly means file browser |

#### Dynamic Frame Icon

The `JInternalFrame` that hosts the left panel now shows a context-appropriate icon:

| Active panel | Icon |
|---|---|
| File / Query Tree | `pages.gif` (stacked documents) |
| SQL Object Tree | `db.gif` (database cylinder) |

The icon is set in `getFileTree()`, `showSQLTree()`, and `restoreFileTree()`.

---

### Query Editor Right-Click — Build IN List from Selection

**Menu item:** "Build IN List from Selection"  
**Location:** after "Remove Initial numerics from SQL" in the right-click popup.

Converts the currently selected lines into a SQL `IN (…)` clause:

1. Splits the selection by line, discarding blank lines.
2. Asks: *Treat values as numeric? Yes / No / Cancel*
3. Builds the clause — each value on its own line with a trailing comma:

```sql
IN (
'SMITH',
'JONES',
'CLARK'
)
```

Numeric mode omits the single quotes. Single quotes inside string values are
automatically escaped (`'` → `''`). The clause replaces the current selection.

---

### Query Editor Right-Click — Copy Columns from Selection

**Menu item:** "Copy Columns from Selection…"  
**Location:** after "Build IN List from Selection".

Extracts a fixed character-position range from each line of the selection and copies
the result to the system clipboard without modifying the editor content.

1. Prompts for **Start column** (1-based) and **End column** (inclusive).
2. Clips each line to the requested range (short lines produce an empty contribution).
3. Copies the multi-line result via `StringSelection` / `getSystemClipboard().setContents()`.
4. Shows status message: *"Columns copied to clipboard"* (previous errors cleared first).

Typical use case: extract a specific data column from a fixed-width query result
pasted into the editor.

---

### Query Report Right-Click — Copy WHERE Clause from Row

**Menu item:** "Copy WHERE clause from row"  
**Location:** in the row right-click popup (`popa`) after "Copy selected data".

Builds a multi-line `WHERE` clause from every column of the currently selected row
and copies it to the system clipboard. Useful for quickly constructing a targeted
re-query based on a result row.

Example output for a three-column row:

```sql
WHERE EMPNO = 7369
  AND ENAME = 'SMITH'
  AND HIREDATE = '1980-12-17'
```

**Type handling:**

| Value | Column class | Generated fragment |
|---|---|---|
| `?` (null) | any | `COL IS NULL` |
| numeric | superclass `Number` | `COL = 42` |
| all other | — | `COL = 'value'` (single quotes in value escaped as `''`) |

Column visibility is respected: hidden columns (via Hide Column) are not included
because they are absent from the current column model.

---

### Bug Fix — Status Message Not Cleared on Success

`Sui.SetMsg(String)` (single-argument form) **appends** to any existing error text
in `emsg` rather than replacing it. The "Copy Columns from Selection" success message
was calling this form and therefore displayed accumulated prior error messages alongside
the confirmation text.

**Fix:** changed to `Sui.SetMsg("Columns copied to clipboard", "E", "N")` which clears
`emsg` first (`"E"`) and suppresses the error beep (`"N"`).

---

## Files Changed

| File | Type | Change summary |
|---|---|---|
| `src/Sui.java` | Modified | Version → 0.75G; 6 Edit menu items + key handlers; paren matching; Ln/Col label; `enableParenHighLight()` / `disableParenHighLight()`; `getToolBar()`; frame icon changes |
| `src/SuiTb.java` | Modified | `sqlTreeI` → `selecttable_16x16.png`; `queryTreeI` → `pages.gif` |
| `src/QryPop.java` | Modified | "Build IN List from Selection"; "Copy Columns from Selection…"; "Enable/Disable Paren Matching" menu item; `SetMsg` fix |
| `src/QueryRep.java` | Modified | "Copy WHERE clause from row" in row popup |
| `src/SQLTreePanel.java` | Modified | Titled border on filter row |
| `docs/ReleaseNotes-0.75G.md` | New | This file |

---

## Upgrade Notes

- No configuration or schema changes are required.
- All new icons (`selecttable_16x16.png`, `pages.gif`, `db.gif`) were already present
  in the `imgs/` resource folder from prior releases.
- No new external dependencies are introduced.
