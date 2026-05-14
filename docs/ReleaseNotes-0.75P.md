# Release Notes — Sui 0.75P

**Branch:** `Sui0.75P`  
**Base:** `Sui 0.75O` (Query Sheet Overview, Connection Status Bar, Connection Manager polish)  
**Date:** 2026-05-14  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Result Set Compare | New feature | New `DiffRep` window — side-by-side visual diff of two query result sets |
| Result Set Compare | New feature | Colour coding: green = left-only row, red = right-only row, yellow cell = value differs, white = identical |
| Result Set Compare | New feature | Multi-column composite key selection via `JList`; key columns drive row matching |
| Result Set Compare | New feature | Columns matched by name (case-insensitive); columns absent from one side shown as `[L only]` / `[R only]` |
| Result Set Compare | New feature | Summary bar: key count · identical · cells-differ · left-only · right-only |
| Result Set Compare | New feature | "Open in Query View" — materialises the current diff into a `QueryRep` result window |
| Result Set Compare | New feature | Export to CSV: timestamped filename; Status column + Left_/Right_ column pairs |
| Result Set Compare | New feature | New `RunItDiff` background worker — runs the right-side SQL on a second connection; rollback+close on all paths |
| Query Report | New feature | "Diff ▼" button on result windows — popup of in-session connections to compare against |
| Query Report | New feature | Right-side SQL pre-filled from the current query; editable in a dialog for schema/filter adjustments before running |
| SQL Object Tree | New feature | "Show SQL Object Tree" toggle added to query right-click context menu |
| SQL Object Tree | New feature | "Show SQL Object Tree at startup" checkbox in **Preferences → Start Up** (`SUI.SHOWSQLTREE`) |
| SQL Object Tree | New feature | Mutual exclusion in startup preferences: File Tree ↔ SQL Object Tree; Query Toolbar (FavBar) ↔ Sheet List |
| System Log | New feature | New **System Log** panel (`Options → System Log`) — in-app viewer for `System.out` / `System.err` output |
| System Log | New feature | `SuiConsolePanel` captures startup messages via an early-capture buffer before the UI is built |
| System Log | New feature | Live tee mode after startup: output written to both the original stream and the panel simultaneously |
| System Log | New feature | Clear, Save to File, and Close buttons; 500 000 character buffer with automatic trimming |
| Split pane layout | Enhancement | Left (file-tree) and right (sheet-list/fav-bar) `JSplitPane` one-touch expand/collapse buttons centred in the divider strip |
| Split pane layout | Enhancement | One-touch arrow buttons enabled/disabled to reflect current collapsed/expanded state |
| Split pane layout | Enhancement | Left-pane divider clamped: cannot be pushed so far right that the main query area disappears |
| Split pane layout | Enhancement | Right-pane divider clamped: minimum 50 px of main content always visible when the right panel is open |
| Split pane layout | Enhancement | `consoleSplit` (vertical) wraps the right split and the System Log panel; hidden (size 0) until first shown |
| Connection Manager | Bug fix | BigQuery URLs auto-detect project ID — Auto-login and password fields disabled when a project-URL is selected |
| Tab colour on drag | Bug fix | Dragging a sheet in the Query Sheet Overview now correctly moves the tab background colour with the tab title and properties |
| Connection history | Bug fix | Failed connections (wrong password, driver error, etc.) are no longer added to the in-session connection history |
| Connection history | Enhancement | `recordConnHistory()` helper centralises deduplication logic; only called after a connection is confirmed working |
| Documentation | New | `docs/ResultSetCompare.md` — Result Set Compare usage guide |
| Documentation | New | `docs/QueryRepWindow.md` — Query Report window reference |
| Documentation | Update | `docs/CredentialHandling.md` — updated for new session-cache priority rules |
| Version | Bump | `0.75O` → `0.75P` in `Sui.java`, `pom.xml`, About dialog |

---

## Detailed Changes by Area

---

### Result Set Compare (`DiffRep.java`, `RunItDiff.java`, `QueryRep.java`)

A **Diff** button is now available on every result window (type "S"). Clicking it shows a
popup of all in-session connections. Selecting one opens a SQL editor dialog (pre-filled
with the current query, editable for right-side adjustments), then executes that SQL
on the chosen connection in a background thread.

When both result sets arrive, a `DiffRep` window opens showing a merged table.

#### Column handling

Columns from both sides are merged into a single set matched **by name** (case-insensitive).
- Columns present on both sides appear once, with left and right values side by side.
- Columns present only on the left are annotated `[L only]` in the key-column picker.
- Columns present only on the right are annotated `[R only]`.

#### Key column selection

A `JList` on the right of the diff window shows all merged column names. Select one or
more entries to use them as composite keys for row matching. With no key columns selected,
rows are matched by position.

#### Colour codes

| Colour | Meaning |
|---|---|
| Green row | Row exists in the left result only |
| Red row | Row exists in the right result only |
| Yellow cell | Row matched on key; this cell's value differs |
| White row | Row matched on key; all values identical |

#### Summary bar

```
Key: X | Identical: N | Cells differ: N | Left only: N | Right only: N
```

#### Buttons

| Button | Action |
|---|---|
| Re-diff | Re-run comparison with the currently selected key columns |
| Open in Query View | Opens diff as a `QueryRep` window with a STATUS column and Left_/Right_ column pairs |
| Export CSV | Saves the current diff table to a timestamped CSV file |

---

### System Log (`SuiConsolePanel.java`)

`Options → System Log` toggles an in-app console panel that shows all `System.out` and
`System.err` output. A vertical `JSplitPane` separates the main window area from the
console; the divider is hidden (size 0) until the console is first shown.

Early startup output (before the UI is built) is captured via
`SuiConsolePanel.startEarlyCapture()` called from `main()` and replayed into the text
area once `installRedirect()` runs.

The panel trims itself to 500 000 characters when the buffer grows too large.

---

### Split Pane One-Touch Buttons

The one-touch arrow buttons on both the left (`MainPan`) and right (`rightSplit`) split
panes are now:

- **Centred** in the divider strip via a custom `LayoutManager` installed through a
  `HierarchyListener` (runs after the first layout pass so real pixel dimensions are available).
- **Enabled/disabled** based on whether the panel is currently collapsed or expanded,
  preventing the buttons from being used to push content off-screen.

A `PropertyChangeListener` on `DIVIDER_LOCATION_PROPERTY` clamps the divider and syncs
the button state on every drag.

---

### Bug Fixes

#### Tab colour lost on sheet drag (fix in `Sui.MoveTab`)

`MoveTab` shifted tab titles and all `SheetProp`/`TmpProp` data but never updated
`TabbedPane.setBackgroundAt`. After the fix, the background colour is snapshotted from the
source tab, shifted through the intermediate positions, and placed at the destination —
mirroring the same logic used for the title. `SysProp` `SUI.TABCOLOR.N` keys are re-synced
for all affected positions so a save/restore after the move also reflects the correct colours.

#### Failed connection added to history (fix in `Sui.java` + `RunIt.java`)

The FASTCONN path was calling `connHistory.add()` before `RunSql` started — optimistically
assuming the connection would work. If the password was wrong the bad entry stayed in the
history popup. The fix:

1. A new `Sui.recordConnHistory(url, uid)` helper centralises the deduplicate-then-prepend
   logic.
2. The FASTCONN block no longer touches the history list (it still sets `Connect=true` and
   updates the status bar, as before).
3. `ConnDB()` and `RunIt` both call `recordConnHistory()` only after
   `getConnection()` / `getConn()` returns successfully.

#### BigQuery password fields in Connection Manager

When a URL containing a project ID (BigQuery OAuth flow) is selected in Connection Manager,
the Auto-login checkbox and password field are now automatically disabled, preventing
accidental credential storage for OAuth-based connections.
