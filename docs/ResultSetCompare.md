# Result Set Compare

The **Compare** feature lets you place two SQL result sets side-by-side and
instantly see what is the same, what is different, and what is missing — without
writing any extra SQL or copying data to a spreadsheet.

Typical use-cases:

- *Did the data change after a deployment?*  Run the same query before and after.
- *Do DEV and PROD have the same reference data?*  Compare across environments.
- *Did my SQL refactor produce identical output?*  Compare two queries in the same DB.
- *Why does the report look different today?*  Diff yesterday's result against today's.

---

## Starting a comparison

Every comparison starts from an **open Result window**.  Click the **`≠`** (diff)
button in its toolbar.  A small menu appears with two sections:

```
┌─────────────────────────────────────────────────┐
│  ≠  Compare with…                               │
├─────────────────────────────────────────────────┤
│  Open result windows                            │
│  ▸  ORDERS — 2 430 rows  (QueryRep #2)          │  ← already open,
│  ▸  ORDERS — 1 998 rows  (QueryRep #3)          │    instant compare
├─────────────────────────────────────────────────┤
│  Re-run against connection                      │
│  ▸  jdbc:db2://prod-server/MYDB                 │  ← runs the SQL
│  ▸  jdbc:bigquery://project/dataset             │    on a live DB
└─────────────────────────────────────────────────┘
```

| Choice | What happens |
|---|---|
| **Open result window** | Compares the two in-memory result sets immediately.  No re-execution, no password. |
| **Connection entry** | Prompts for a password (if needed), then opens an editable SQL box pre-loaded with the original query.  Adjust the SQL if table names differ across environments, then click OK.  The query runs in the background and the Compare window opens when it finishes. |

---

## The Compare window at a glance

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  TOOLBAR                                                                         ║
║  [Summary counts]  [Open in query view]  [Export CSV]                            ║
║  [✓ Ignore trailing blanks]  [¶·]  [✓ Ignore case]  [Presets ▾]  [Sync SQL]  [Close]  ║
╠══════════════╦═══════════════════════════════════════════════════════════════════╣
║              ║                                                                   ║
║  COLUMN      ║   DIFF TABLE  (scrolls horizontally and vertically)               ║
║  ROLES       ║                                                                   ║
║              ║   < CUST_ID  CUST_ID >  < NAME      NAME >   < CITY    CITY >    ║
║  Column  K C I   ──────────────────────────────────────────────────────────────  ║
║  CUST_ID ○ ● ○   │  1001    │  1001   │  Alice   │  Alice  │  Rome    │ Rome   │ ║
║  NAME    ○ ● ○   ├──────────┼─────────┼──────────┼─────────┼──────────┼────────┤ ║
║  CITY    ○ ● ○   │  1002    │  1002   │  Bob     │  Bob    │  Paris   │ Berlin │ ║
║  SCORE   ○ ● ○   ├──────────┼─────────┼──────────┼─────────┼──────────┼────────┤ ║
║          ║       │  1003    │         │  Carol   │         │  Oslo    │        │ ║
║ [Apply]  ║       ├──────────┼─────────┼──────────┼─────────┼──────────┼────────┤ ║
║          ║       │          │  1004   │          │  Dave   │          │ Berne  │ ║
╠══════════╩═══════════════════════════════════════════════════════════════════════╣
║  LEGEND  ██ Left only   ██ Right only   ██ Value differs                         ║
║  FILTER  Left: jdbc:db2://prod/MYDB     Right: jdbc:db2://dev/MYDB               ║
║  SHOW:   [All]  [Left only]  [Right only]  [Differ]                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

The window has four areas:

| Area | Purpose |
|---|---|
| **Toolbar** (top) | Summary counts, options, and action buttons |
| **Column Roles** (left panel) | Assign each column a role: Key, Compare, or Ignore |
| **Diff Table** (centre) | The merged result showing every row side-by-side |
| **Legend / Filter bar** (bottom) | Colour key, source URLs, and row-type filter |

---

## Reading the colour coding

Three colours tell you everything at a row and cell level:

```
  Row colour            What it means
  ─────────────────     ────────────────────────────────────────────────────────
  ████████████████      Pale GREEN — this row exists ONLY on the LEFT side.
  (whole row green)     It is absent from the right result set.

  ████████████████      Pale RED — this row exists ONLY on the RIGHT side.
  (whole row red)       It is absent from the left result set.

  White / zebra         Row is MATCHED on both sides (same key or same position).

  ██ Yellow cell(s)     Row is matched but this cell's value DIFFERS between
                        left and right.  The rest of the row may be identical.
```

A quick example — three rows tell three different stories:

```
  < CUST_ID   CUST_ID >  │  < NAME      NAME >    │  < CITY      CITY >    │
  ───────────────────────┼─────────────────────────┼────────────────────────┤
   1001        1001      │   Alice       Alice     │   Rome        Rome     │  ← identical
  ───────────────────────┼─────────────────────────┼────────────────────────┤
   1002        1002      │   Bob         Bob       │  ▓Paris▓     ▓Berlin▓  │  ← same row, city differs
  ───────────────────────┼─────────────────────────┼────────────────────────┤
   1003                  │   Carol                 │   Oslo                 │  ← left only (green row)
  ───────────────────────┼─────────────────────────┼────────────────────────┤
              1004       │             Dave        │           Berne        │  ← right only (red row)
```

---

## Column layout — left column (`<`) and right column (`>`)

For every data column the Compare window shows **two side-by-side columns**:

```
         One original column (e.g. CITY)
         ┌──────────────┬──────────────┐
         │  < CITY      │  CITY >      │
         │  (left side) │  (right side)│
         └──────────────┴──────────────┘
              ▲                ▲
              │                └── value from the RIGHT result set
              └── value from the LEFT result set
```

The `<` prefix on the left column and `>` suffix on the right column are visual
anchors — scanning left-to-right you always know which side you are reading.

---

## Matching rows — Position vs Key

Before the tool can colour the rows it must decide which left-side row "belongs"
with which right-side row.  There are two modes:

### Position-based matching (the default)

Row 1 is paired with row 1, row 2 with row 2, and so on.

```
  LEFT result set          RIGHT result set
  ─────────────────        ─────────────────
  Row 1: Alice, Rome   ──► Row 1: Alice, Rome    ✓ matched (same position)
  Row 2: Bob, Paris    ──► Row 2: Bob, Berlin    ✓ matched
  Row 3: Carol, Oslo   ──► (no row 3)            ✗ LEFT ONLY
```

This works well when both queries return rows **in the same order**.  If one side
is sorted differently the results can be misleading.

### Key-based matching (recommended for reliable diffs)

You nominate one or more columns as the **Key** in the Column Roles panel.  The
tool then looks up each left-side row by its key value in a fast index of the
right-side data.

```
  LEFT result set              RIGHT result set  (indexed by CUST_ID)
  ─────────────────────        ──────────────────────────────────────
  Row 1: ID=1001, Alice   ──► found ID=1001 on right  → compare cells
  Row 2: ID=1002, Bob     ──► found ID=1002 on right  → compare cells
  Row 3: ID=1003, Carol   ──► no ID=1003 on right     → LEFT ONLY  (green)
                              ID=1004 never matched   → RIGHT ONLY (red)
```

Row order does not matter at all.  The tool finds the matching row no matter where
it appears in the right result.

**Setting a key:**  In the **Column Roles** panel on the left of the window, tick
the **K** (Key) radio button next to the column(s) that uniquely identify a row,
then click **Apply**.

```
  Column Roles panel
  ┌────────────┬───┬───┬───┐
  │ Column     │ K │ C │ I │   K = Key
  ├────────────┼───┼───┼───┤   C = Compare (default)
  │ CUST_ID    │ ● │ ○ │ ○ │   I = Ignore
  │ NAME       │ ○ │ ● │ ○ │
  │ CITY       │ ○ │ ● │ ○ │
  │ INTERNAL   │ ○ │ ○ │ ● │  ← excluded from comparison
  └────────────┴───┴───┴───┘
         [Apply]
```

You can pick **multiple key columns** to form a composite key
(e.g. ORDER_ID + LINE_NO together identify a unique order line).

---

## Toolbar options

### Ignore trailing blanks ✓

On by default.  When active, a value of `"Hello   "` (with trailing spaces) is
treated as equal to `"Hello"`.  Turn it off if trailing spaces are meaningful in
your data.

### ¶· (Show whitespace)

Replaces invisible whitespace characters in every cell with visible markers:

```
  Normal display:   "Hello World"
  Whitespace on:    "Hello·World"    (· = space)

  Normal display:   "First line\nSecond line"
  Whitespace on:    "First·line¶Second·line"   (¶ = newline)

  · = space     → = tab     ¶ = newline
```

Useful for spotting hidden spaces, tabs, or line-break differences that are
otherwise invisible in the cell.

### Ignore case ✓

When checked, `"PARIS"` and `"Paris"` and `"paris"` are all treated as equal.
Changing this option immediately re-runs the entire comparison.

### Presets ▾

Saves and restores a complete compare configuration — column roles (Key / Compare /
Ignore for every column) plus the current **Ignore trailing blanks** and **Ignore
case** settings — so you can re-apply a complex setup in a single click.

```
  ┌───────────────────────────────────┐
  │  Presets ▾                        │  ← click to open menu
  ├───────────────────────────────────┤
  │  Save as…                         │  ← name and save current settings
  ├───────────────────────────────────┤
  │  OrdersKey                        │  ← previously saved preset
  │  CustomerDiff                     │
  ├───────────────────────────────────┤
  │  Delete…                          │  ← pick a preset to remove
  └───────────────────────────────────┘
```

**Saving a preset** — click **Save as…**, type a name (the current key column
names are suggested automatically, e.g. `ORDER_ID+LINE_NO`), and press OK.  The
preset is written to `DiffPresets.pro` in the Sui home directory.

**Applying a preset** — click its name in the menu.  Column roles are applied
instantly to the Column Roles panel, the option checkboxes are updated, and the
diff re-runs.  Columns in the preset that are **not present** in the current result
set are silently skipped; columns in the result set that are **not in the preset**
default to Compare.

**Deleting a preset** — click **Delete…** and choose the preset to remove.

Presets make the following scenarios quick and repeatable:

| Scenario | Without preset | With preset |
|---|---|---|
| Same comparison run daily | Reassign all roles every time | Click the preset name |
| Multiple compare configurations for one table | Rebuild from scratch | Save one preset per configuration |
| Onboarding a new team member | Document the key columns | Share `DiffPresets.pro` |

---

## Filtering — focusing on what matters

The **Show:** buttons in the bottom-right corner narrow the table to only the rows
you care about:

```
  ┌──────────────────────────────────────────────────────────┐
  │  Show:  [All]  [Left only]  [Right only]  [Differ]       │
  └──────────────────────────────────────────────────────────┘

  All         → show every row (default)
  Left only   → show only the green rows  (missing from right)
  Right only  → show only the red rows    (missing from left)
  Differ      → show only matched rows where at least one cell differs
```

Switching the filter is instant.  The summary bar at the top always shows the
**full** counts regardless of which filter is active.

---

## Summary bar

The summary bar at the top tells you the overall picture at a glance:

```
  Key: CUST_ID  |  Identical: 1 842  |  Cells differ: 37  |  Left only: 5  |  Right only: 3
  ▲              ▲                    ▲                     ▲                ▲
  │              │                    │                     │                └── rows only in right
  │              │                    │                     └── rows only in left
  │              │                    └── matched rows with at least one cell difference
  │              └── matched rows where every cell is identical
  └── which column(s) are being used as the matching key
```

---

## Inspecting a specific row — double-click

Double-clicking any row opens a **Row Detail** dialog showing all columns of that
row on a single screen, making it easier to read long values.

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  Row 12  —  MATCH                                                         │
  ├──────────────┬──────────────────────────────┬──────────────────────────┤
  │  Column      │  Left                        │  Right                   │
  ├──────────────┼──────────────────────────────┼──────────────────────────┤
  │  CUST_ID     │  1002                        │  1002                    │
  ├──────────────┼──────────────────────────────┼──────────────────────────┤
  │  NAME        │  Bob Smith                   │  Bob Smith               │
  ├──────────────┼──────────────────────────────┼──────────────────────────┤
  │  CITY        │  ▓Pa▓ris   ← differs         │  ▓Be▓rlin  ← differs     │
  │  (yellow)    │  (bold+underline shows       │  (bold+underline shows   │
  │              │   the differing part)        │   the differing part)    │
  ├──────────────┼──────────────────────────────┼──────────────────────────┤
  │  SCORE       │  98.5                        │  98.5                    │
  └──────────────┴──────────────────────────────┴──────────────────────────┘
                                               [✓ Show as hex]  [Close]
```

For differing cells, the **common prefix and suffix are shown in normal text** and
the **unique middle portion is shown in bold and underlined**.  This makes it
immediate to see exactly which characters differ, even in long strings.

The **Show as hex** checkbox switches every value to space-separated Unicode
codepoint hex — useful for diagnosing invisible character or encoding problems.

---

## Hex view — diagnosing invisible characters

Right-clicking any cell in the Compare table opens a context menu:

```
  ┌────────────────────────────────────┐
  │  Show hex: < CITY                  │
  │  ────────────────────────────────  │
  │  Row detail…                       │
  └────────────────────────────────────┘
```

Choosing **Show hex** opens a hex-dump dialog for that cell's value:

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  Hex: < CITY                                                              │
  │                                                                           │
  │  Value  : Münich                                                          │
  │  Length : 6 char(s),   7 byte(s) UTF-8                                    │
  │                                                                           │
  │  Offset   Hex (UTF-8)                                        ASCII        │
  │  ------   -------------------------------------------------  --------    │
  │  000000   4D C3 BC 6E 69 63 68                               M.nich      │
  │                                                                           │
  │  Non-ASCII Unicode codepoints:                                            │
  │    [1] U+00FC  'ü'                                                        │
  └──────────────────────────────────────────────────────────────────────────┘
```

The hex view is also accessible inside the **Row Detail** dialog — right-click any
Left or Right cell in the detail table to hex-dump just that value.  Alternatively
check the **Show as hex** checkbox to convert the entire row to codepoint notation.

This feature is most useful when:
- A diff shows cells as different but the values **look identical** on screen
  (hidden control characters, non-breaking spaces, different newline encodings)
- You need to confirm whether a value is truly empty or contains whitespace
- You are diagnosing a multi-byte character encoding mismatch between databases

---

## Generating sync SQL

The **Sync SQL** button generates INSERT and/or UPDATE statements to bring one
side in line with the other.  A dialog lets you choose the direction and which
row types to include:

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Target table name:  [ CUSTOMER                           ] │
  │                                                             │
  │  Sync RIGHT side  (make RIGHT match LEFT):                  │
  │  [✓] INSERT missing rows into RIGHT   (5 rows)              │
  │  [✓] UPDATE differing rows in RIGHT   (37 rows)             │
  │                                                             │
  │  Sync LEFT side  (make LEFT match RIGHT):                   │
  │  [ ] INSERT missing rows into LEFT    (3 rows)              │
  │  [ ] UPDATE differing rows in LEFT    (37 rows)             │
  │                                                       [OK]  │
  └─────────────────────────────────────────────────────────────┘
```

The generated SQL appears in a text box ready to copy into a query window.
UPDATE statements require at least one **Key** column to be defined.

---

## Exporting the result

| Button | What you get |
|---|---|
| **Export CSV** | A `.csv` file with a `Status` column plus left/right columns for every field.  Only the currently **filtered** rows are exported — use **Differ** first to export only the mismatches. |
| **Open in query view** | Opens the filtered rows as a full Result window.  From there you can sort, filter further, hide columns, transpose, and export to XLS. |

---

## Workflow walkthroughs

### Workflow A — Compare DEV vs PROD

```
  1. Run query in DEV  →  Result window opens
           │
           ▼
  2. Click ≠  →  choose PROD from "Re-run against connection"
           │
           ▼
  3. Enter PROD password  →  adjust SQL if schema differs  →  OK
           │
           ▼
  4. Compare window opens
           │
           ▼
  5. Assign Key column(s) in the Column Roles panel  →  Apply
           │
           ▼
  6. Read summary:  "Identical: 4 821  |  Cells differ: 12  |  Left only: 0  |  Right only: 0"
           │
           ▼
  7. Click [Differ] filter  →  see only the 12 mismatched rows
           │
           ▼
  8. Double-click a row  →  Row Detail shows exactly which characters differ
```

### Workflow B — Spot invisible character problems

```
  1. Open Compare window — two values look the same but are flagged as different
           │
           ▼
  2. Right-click the suspicious cell  →  "Show hex: < COLUMN_NAME"
           │
           ▼
  3. Hex dump reveals a non-breaking space (U+00A0) or carriage return (U+000D)
           │
           ▼
  4. Toggle ¶· (Show whitespace) on the main table to confirm visually
```

### Workflow C — Reconcile two result sets after a refactor

```
  1. Run original query  →  Result window A
  2. Run refactored query  →  Result window B
  3. Click ≠ in window A  →  choose window B (instant, in-memory compare)
  4. If row order differs, assign a Key  →  Apply
  5. Click [Differ]  →  empty table means the refactor is correct ✓
```

### Workflow D — Re-use a saved preset

```
  1. First time setup:
         Assign column roles and options as usual  →  Apply
              │
              ▼
         Click [Presets ▾]  →  Save as…  →  type a name, e.g. "ORDERS_KEY"
              │
              ▼
         Settings written to DiffPresets.pro

  2. Every subsequent run:
         Open Compare window (any two ORDERS result sets)
              │
              ▼
         Click [Presets ▾]  →  ORDERS_KEY
              │
              ▼
         All roles restored, diff re-runs immediately ✓
```

---

## Quick-reference card

```
  ┌───────────────────────────────────────────────────────────────────┐
  │  COMPARE WINDOW — QUICK REFERENCE                                 │
  ├───────────────┬───────────────────────────────────────────────────┤
  │  GREEN row    │  Row present only on the LEFT                     │
  │  RED row      │  Row present only on the RIGHT                    │
  │  YELLOW cell  │  Matched row, but this cell value differs          │
  │  White row    │  Fully identical row                              │
  ├───────────────┼───────────────────────────────────────────────────┤
  │  K role       │  Use this column as matching key                  │
  │  C role       │  Compare this column's values (default)           │
  │  I role       │  Ignore this column (don't compare, don't key)    │
  ├───────────────┼───────────────────────────────────────────────────┤
  │  Double-click │  Row Detail — see all columns; bold+underline     │
  │               │  marks the exact differing characters             │
  │  Right-click  │  Show hex dump of that cell / open Row Detail     │
  ├───────────────┼───────────────────────────────────────────────────┤
  │  ¶·           │  Make spaces/tabs/newlines visible                │
  │  Ignore case  │  Treat ABC and abc as equal                       │
  │  Ignore trail │  Treat "Hello   " and "Hello" as equal            │
  │  Presets ▾    │  Save/load column roles + options in one click    │
  ├───────────────┼───────────────────────────────────────────────────┤
  │  [Differ]     │  Show only rows with at least one cell difference │
  │  [Left only]  │  Show only rows absent from the right             │
  │  [Right only] │  Show only rows absent from the left              │
  └───────────────┴───────────────────────────────────────────────────┘
```


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

