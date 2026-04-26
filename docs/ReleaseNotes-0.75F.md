# Release Notes — Sui 0.75F

**Branch:** `Sui0.75F`  
**Base:** `Sui 0.75C` (master)  
**Date:** 2026-04-25  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| SQL Object Tree | New feature | New `SQLTreePanel` — lazy-loading JTree of schemas → tables → columns |
| SQL Object Tree | New feature | Toolbar buttons to show SQL Object Tree / Query File Tree |
| SQL Object Tree | New feature | Right-click table node: "Build SQL to clipboard", "Draw SQL (SELECT)", "Draw SQL (INSERT)" |
| SQL Object Tree | New feature | Drag table node to query window — choose `schema.table` or full `SELECT` statement |
| SQL Object Tree | New feature | Drag column node to query window — inserts column name at caret |
| DB2 compatibility | Fix | SQLCODE -4471 resolved: `conn.commit()` added after every metadata `ResultSet` close |
| DB2 compatibility | Fix | System schemas (SYSIBM, SYSCAT, SYSSTAT, etc.) filtered from tree |
| DB2 compatibility | Fix | `getColumns()` called with `null` column-name pattern instead of `%` wildcard |
| BigQuery compatibility | Fix | OAuth connection cache preserved — `closeConn()` is a no-op for BigQuery |
| BigQuery compatibility | Fix | Schema list filtered to current project only (extracted from JDBC URL `ProjectId=`) |
| BigQuery compatibility | Fix | `project.dataset` schema name prefix stripped before `getTables()` call |
| Mimer SQL compatibility | Fix | Tables now load: `null` catalog and `null` table-type filter used in `getTables()` |
| Mimer SQL compatibility | Fix | Schema name uppercased for Mimer and DB2 before metadata calls |
| `Sui.java` | New feature | `showSQLTree()` with no-connection guard, panel swap, toolbar state update |
| `Sui.java` | New feature | `restoreFileTree()`, `showQueryTree()`, `isSQLTreeActive()`, `getToolBar()` |
| `SuiTb.java` | New feature | Two new toolbar buttons: "Show SQL Object Tree" (`schema.gif`) and "Show Query File Tree" (`find.png`) |
| `SuiTb.java` | New feature | `updateTreeButtons()` — disables the button for the currently active panel |
| `QryPop.java` | Enhancement | "SQL Object Tree" / "Hide SQL Object Tree" toggle menu item added |
| `QryPop.java` | Enhancement | ShowQ/HideQ now delegate to `Sui.showQueryTree()` / `updateTreeButtons()` |

---

## Detailed Changes by File

### `src/SQLTreePanel.java` — NEW FILE

A new panel class that replaces the `FileTreePanel` in the left-hand `jif` internal
frame while a database connection is active.  Swap back to the file tree at any time
using the toolbar or the Query pop-up menu.

#### Tree structure

The tree has three levels, all loaded lazily on first expand:

```
▶ MYSCHEMA
    ▶ CUSTOMERS
        CUSTID        INTEGER NOT NULL
        CUSTNAME      VARCHAR(80)
        …
    ▶ ORDERS
        …
```

Schema nodes are shown in bold with a directory icon; table nodes use a file icon;
column nodes are shown in italic with the data-type/size as a suffix.

#### Lazy loading

Expanding a schema node triggers a `SwingWorker` that calls
`DatabaseMetaData.getTables()` on a background thread.  Expanding a table node calls
`DatabaseMetaData.getColumns()` similarly.  A ⌛ Loading… sentinel is displayed while
the worker runs, replaced by the real rows on completion.  A `Refresh` button at the
top of the panel reloads the full schema list from scratch.

#### Status bar

A one-line label above the tree shows the current operation ("Loading schemas…",
"N schemas loaded", or any error message) so the user always knows what the tree is
doing.

#### Database-specific behaviour

| Database | `getTables()` catalog arg | Schema uppercase | `getColumns()` pattern | Post-RS `commit()` |
|---|---|---|---|---|
| DB2 | `null` | Yes | `null` | Yes |
| BigQuery | project-id string | No | `null` | Yes |
| Mimer SQL | `null` | Yes | `null` | Yes |
| Others | `null` | No | `null` | No |

**DB2 SQLCODE -4471 fix** — IBM DB2 JDBC raises `-4471` ("The use of a cursor with
the HOLD attribute is not supported in this environment") if a `ResultSet` obtained
from `DatabaseMetaData` is open when a second metadata call is made inside the same
transaction.  Every `ResultSet` is now closed and followed by `try { conn.commit(); }`
before the next metadata call, eliminating this error.

**DB2 system schema filter** — `getSchemas()` returns SYSIBM, SYSCAT, SYSSTAT,
SYSTOOLS, SYSFUN, SYSPROC, SYSIBMADM, and any name beginning with SYS.  These are
suppressed by `isDB2SystemSchema()` so only user schemas appear.

**BigQuery project filter** — The BigQuery JDBC driver returns schemas for every
dataset in every accessible project.  The project ID is extracted from the JDBC URL
(`ProjectId=<id>`) and only schemas belonging to that project are shown.  The
`project.dataset` prefix is stripped before the `getTables()` call because the driver
does not accept the compound form as a schema argument.

**Mimer SQL fix** — Passing a non-null catalog or a restricted table-type array
(`{"TABLE","VIEW"}`) to `getTables()` causes Mimer to return zero rows.  Both
arguments are now passed as `null`, matching the pattern used in `TableProvider.java`.

#### Right-click context menu (table nodes only)

| Item | Behaviour |
|---|---|
| **Build SQL to clipboard** | Fetches all column names (from tree cache if already expanded, otherwise via `getColumns()` in background), builds `SELECT col1,\n       col2\nFROM schema.table`, and copies to the system clipboard. |
| **Draw SQL (SELECT)** | Sets the active schema and table name from the node, then invokes `RunSql(null, "D")` with draw-type `SEL` — same behaviour as the existing toolbar Draw SELECT button but without needing the table name in the query window. |
| **Draw SQL (INSERT)** | Same as above with draw-type `INS`. |

#### Drag-and-drop into query window

- **Table node** — drag onto the query text area; a dialog asks whether to insert
  `schema.table` or a full `SELECT` statement.  The SELECT is built the same way as
  "Build SQL to clipboard" (cached columns preferred, background fetch fallback).
- **Column node** — drag onto the query text area; the column name is inserted at the
  current caret position with no dialog.

---

### `src/Sui.java` — Modified

New static field:

```java
static private SQLTreePanel SQLTree;
```

New static methods:

| Method | Purpose |
|---|---|
| `showSQLTree()` | Guard-checks for an active connection, creates/reloads `SQLTreePanel`, swaps it into `jif`, calls `ToolBar.updateTreeButtons()` |
| `restoreFileTree()` | Swaps `FileTree` back into `jif`, calls `ToolBar.updateTreeButtons()` |
| `showQueryTree()` | Makes `jif` visible, sets divider position, calls `ToolBar.updateTreeButtons()` |
| `isSQLTreeActive()` | Returns `true` when `SQLTreePanel` is the current content of `jif` |
| `getToolBar()` | Returns the `SuiTb` toolbar instance (needed by `QryPop`) |

`SQLTreePanel.installDropTarget(textArea)` is called once during startup (after
`textArea = gettextArea()`) to install the drop handler on the query `JTextPane`.

---

### `src/SuiTb.java` — Modified

Two new toolbar buttons added after the existing `TbCancel` button:

| Button | Icon | Tooltip | Action |
|---|---|---|---|
| `TbSQLTree` | `imgs/schema.gif` | Show SQL Object Tree | `Sui.showSQLTree()` |
| `TbQueryTree` | `imgs/find.png` | Show Query File Tree | `Sui.showQueryTree()` |

New method `updateTreeButtons()` enables/disables each button based on which panel
is currently active, preventing the user from toggling to the already-visible panel.

---

### `src/QryPop.java` — Modified

- A new `JMenuItem` "SQL Object Tree" / "Hide SQL Object Tree" is added to the
  right-click pop-up menu.  Its label toggles depending on `Sui.isSQLTreeActive()`.
  - When the SQL tree is not active: calls `Sui.showSQLTree()` (the connection guard
    inside `showSQLTree()` displays a message if no connection is open).
  - When the SQL tree is active: calls `Sui.restoreFileTree()`.
- **ShowQ** now delegates to `Sui.showQueryTree()` instead of manipulating `jif`
  directly.
- **HideQ** now calls `Sui.getToolBar().updateTreeButtons()` so the toolbar buttons
  remain in sync when the query panel is hidden.

---

## Upgrade Notes

- No schema or configuration changes are required.
- The two new toolbar icons (`schema.gif`, `find.png`) must be present in the
  `imgs/` resource folder bundled with the JAR; they were added to the repository
  alongside this release.
- No new dependencies are introduced; all drag-and-drop and tree APIs are part of
  the standard Java SE Swing library.
