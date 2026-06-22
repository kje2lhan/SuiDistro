# Additional Edit Functions

The **Additional Edit functions** submenu collects the text-manipulation tools
that operate on the SQL query window.  It appears when you **right-click**
inside the query editor (the popup is also known as *QryPop*), as a sub-menu
beneath the execution entries:

```
┌──────────────────────────────────────────────────┐
│  Execute query                                   │
│  Exec. -> XLS                                    │
│  Exec. -> CSV                                    │
│  Exec. -> Append                                 │
│  Additional Exec               ▸                 │
│  ───────────────────────────────                 │
│  Additional Edit functions     ▸                 │   ← this document
│  Convert SQL Dialect…                            │
│  ───────────────────────────────                 │
│  Disable HighLighting                            │
│  …                                               │
└──────────────────────────────────────────────────┘
```

Most entries either rewrite the **current selection** (when something is
selected) or the **entire query window** (when nothing is selected).  Each
description below makes that distinction explicit.

---

## Submenu contents

```
┌─ Additional Edit functions ──────────────────────┐
│  Format SQL                                       │
│  Ext Format SQL                                   │
│  Syntax Validate                                  │
│  Syntax Validate by Prepare         (if connected)│
│  ───────────────────────────────                  │
│  Add Schema…                                      │
│  Remove Schema                                    │
│  ───────────────────────────────                  │
│  Remove Initial numerics from SQL                 │
│  Build IN List from Selection                     │
│  Text -> Insert Statement                         │
│  ───────────────────────────────                  │
│  Trim Trailing Whitespace            Ctrl+Shift+X │
│  Copy Columns from Selection…                     │
│  ───────────────────────────────                  │
│  Uppercase Selection                 Ctrl+Shift+U │
│  Lowercase Selection                 Ctrl+Shift+L │
│  Indent Block                                     │
│  Unindent Block                                   │
│  Toggle Comment                      Ctrl+7       │
│  Go to Line…                         Ctrl+G       │
│  ───────────────────────────────                  │
│  Enable/Disable Paren Matching                    │
└───────────────────────────────────────────────────┘
```

---

## Formatting

### Format SQL
Re-flows the SQL using Sui's built-in formatter (`FormatSQL`).  Capitalises
keywords, breaks `SELECT` lists onto separate lines, indents `FROM`/`WHERE`
clauses, etc.

- If there is a **selection**, only that selection is reformatted.
- Otherwise the **entire query window** is reformatted.

### Ext Format SQL
Calls the extended formatter (`FormSQL2`), which performs a deeper parse and
produces a more aggressive layout (sub-queries on their own lines, aligned
operators, etc.).  If the SQL cannot be parsed an error message is displayed
in the status bar and the text is left unchanged.

- Works on the **selection** only — select the statement you want to reformat
  before invoking.

---

## Syntax validation

### Syntax Validate
Parses the selected SQL with the embedded `TableSplitter` and lists every
table/alias it found.  Use this as a quick check that the parser can read
your statement, and to see how Sui interprets table references for
autocomplete and the Query Tree.

- Operates on the **selection**.

### Syntax Validate by Prepare
Only available when a connection is open.  Sends the selected SQL to the
database driver as a **prepared statement** (without executing it) so the
server itself reports any syntax or binding error.  Best for vendor-specific
syntax that Sui's local parser does not understand.

- Operates on the **selection**.
- Requires an active JDBC connection.

---

## Schema rewriting

These two helpers are designed for the common case of moving a query between
environments where the schema/owner differs (e.g. `DEV.ORDERS` vs `PROD.ORDERS`).

### Add Schema…
Prompts for a schema name and prefixes every **unqualified** table reference
in the selection with `<schema>.`.  Recognised contexts:

```
FROM tbl     → FROM   <schema>.tbl
JOIN tbl     → JOIN   <schema>.tbl
INTO tbl     → INTO   <schema>.tbl
UPDATE tbl   → UPDATE <schema>.tbl
TABLE tbl    → TABLE  <schema>.tbl
```

Already-qualified names (`schema.table`) are left untouched.

- Operates on the **selection**.

### Remove Schema
The inverse of *Add Schema*: strips any schema prefix from tables that follow
`FROM | JOIN | INTO | UPDATE | TABLE`.

```
FROM dev.orders → FROM orders
JOIN prod.lines → JOIN lines
```

- Operates on the **selection**.

---

## Cleanup / extraction

### Remove Initial numerics from SQL
Strips leading line-number columns that often appear when SQL is copied from
a mainframe listing or numbered report.  Calls `Sui.RemLineNo()`.

- If text is selected, only that block is cleaned; otherwise the whole
  query window is cleaned.

### Trim Trailing Whitespace `Ctrl+Shift+X`
Removes trailing spaces and tabs from every line of the **entire query
window** and also any trailing whitespace at the very end of the document.
Caret position is preserved as well as possible.

### Copy Columns from Selection…
Treats the selected text as a fixed-width listing and copies a **column
range** from every line to the system clipboard.

```
Selection:
0001  ALICE   Rome
0002  BOB     Paris
0003  CAROL   Oslo
```

Choose start column 7 and end column 12 → clipboard contains:

```
ALICE
BOB  
CAROL
```

Column numbers are **1-based**; the end column is inclusive.  Short lines are
truncated silently.

---

## Generating SQL from text

### Build IN List from Selection
Wraps the selected lines into an `IN ( … )` clause.  Empty lines are ignored.
After selecting you are asked whether the values are *numeric* or *strings*:

| Choice | Output |
|---|---|
| **Yes** (numeric) | `IN (\n1001,\n1002,\n1003\n)` |
| **No** (strings)  | `IN (\n'1001',\n'1002',\n'1003'\n)` — single quotes inside values are escaped to `''` |

The selection is **replaced** with the generated `IN` clause.

### Text -> Insert Statement
Opens the *Text → Insert Statement* helper (`TextInsStmt`) pre-loaded with
the selected text.  Use it to turn a column-separated text block into a set
of `INSERT INTO … VALUES (…)` statements for a target table.

- Operates on the **selection**.

---

## Case / indentation / commenting

### Uppercase Selection `Ctrl+Shift+U`
Converts the current selection to uppercase.

### Lowercase Selection `Ctrl+Shift+L`
Converts the current selection to lowercase.

### Indent Block
Adds four spaces to the start of every line that the selection touches
(even partial selections expand to whole lines).  If nothing is selected the
current line is indented.

### Unindent Block
The reverse of *Indent Block*: removes a leading four-space prefix from each
selected line, or one leading tab character if no four-space prefix is
present.

### Toggle Comment `Ctrl+7`
Comments or uncomments every line that the selection touches, using the
comment prefix configured in `SUI.COMMENTSTRING` (defaults to `--`).

- If **all** non-blank lines in the range already start with the prefix the
  command **removes** it (uncomment).
- Otherwise the prefix is **added** to every line (comment).

Empty lines never receive a prefix when commenting.

### Go to Line… `Ctrl+G`
Prompts for a 1-based line number and moves the caret to the start of that
line, scrolling the editor as needed.  Invalid or out-of-range values are
clamped (negative → first line, beyond end → last line).

---

## Editor behaviour

### Enable / Disable Paren Matching
Toggles live highlighting of matching parentheses.  When enabled, the
character under the caret and its mate are highlighted (blue on dark themes,
yellow on light themes).  The label of the menu entry reflects the current
state.

The setting is **session-only** — it is not written to the property file.

---

## Panel visibility toggles

The query editor's right-click menu also lets you show or hide the surrounding
panels.  Each entry is a **single toggle** whose label reflects the current
state (`Show …` when the panel is hidden, `Hide …` when it is visible).

| Toggle | What it shows / hides | Mutual exclusion |
|---|---|---|
| **Show / Hide SQL Object Tree** | The SQL Object Tree in the left dock | Showing it hides the Query Tree (they share the left dock) |
| **Show / Hide QueryTree** | The file-based Query Tree in the left dock | Showing it hides the SQL Object Tree |
| **Show / Hide Query Sheet Overview** | The Sheet Overview on the right | Showing it hides the Query Toolbar (they share the right slot) |
| **Show / Hide Query Toolbar** | The Query Toolbar (Favourites bar) on the right | Showing it hides the Query Sheet Overview |
| **Show / Hide Query Tabs** | The tab strip at the bottom of the editor | — |

The SQL Object Tree and the Query Tree share the same left-hand dock panel, so
only one of the two can be visible at a time; likewise the Query Sheet Overview
and the Query Toolbar share the right-hand slot.  The same toggles are also
available from the **Options** menu (see
[Query Sheets, Tabs and the Sheet List](QuerySheetsAndTabs.md)).  The Query
Tabs choice is persisted to `SUI.QUERYTABS` in `SuiSys.pro`.

---

## Quick reference

| Function | Scope | Shortcut |
|---|---|---|
| Format SQL | selection or all | — |
| Ext Format SQL | selection | — |
| Syntax Validate | selection | — |
| Syntax Validate by Prepare | selection (connected only) | — |
| Add Schema… | selection | — |
| Remove Schema | selection | — |
| Remove Initial numerics from SQL | selection or all | — |
| Build IN List from Selection | selection | — |
| Text → Insert Statement | selection | — |
| Trim Trailing Whitespace | whole document | `Ctrl+Shift+X` |
| Copy Columns from Selection… | selection → clipboard | — |
| Uppercase Selection | selection | `Ctrl+Shift+U` |
| Lowercase Selection | selection | `Ctrl+Shift+L` |
| Indent Block | selected lines | — |
| Unindent Block | selected lines | — |
| Toggle Comment | selected lines | `Ctrl+7` |
| Go to Line… | caret only | `Ctrl+G` |
| Paren Matching toggle | editor-wide | — |
| Show / Hide SQL Object Tree | left dock | — |
| Show / Hide QueryTree | left dock | — |
| Show / Hide Query Sheet Overview | right slot | — |
| Show / Hide Query Toolbar | right slot | — |
| Show / Hide Query Tabs | tab strip | — |

---

## Tips & workflows

- **Combining operations.**  *Format SQL* followed by *Indent Block* on a
  sub-query gives you a cleanly formatted, visually offset inner query
  without any manual whitespace work.
- **Cross-environment migration.**  Use *Remove Schema* in the source
  environment, save the cleaned SQL, then *Add Schema* in the target.
- **Reverse-engineering reports.**  Paste an existing report into the query
  window, run *Remove Initial numerics from SQL* to drop the line numbers,
  then *Copy Columns from Selection…* to lift specific columns into your
  next query.
- **Quick `IN` lists.**  Select a column of identifiers (one per line) and
  hit *Build IN List from Selection*; paste the result directly into your
  `WHERE` clause.
- **Mass commenting.**  Select a region and press `Ctrl+7` to comment it
  out, then `Ctrl+7` again to bring it back.  Useful when debugging long
  SQL scripts.
