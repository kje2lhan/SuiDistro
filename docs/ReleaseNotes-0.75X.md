# Release Notes — Sui 0.75X

**Branch:** `Sui-0.75X`  
**Base:** `Sui 0.75V` (Diff highlight, freeze columns, in-app help, Query Sheet List sync)  
**Date:** 2026-06-08  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Query Sheets / Tabs | Bug fix | **Reshuffle/resort no longer corrupts sheet content.** Moving a sheet (drag in the Sheet List) ended with `TabbedPane.setSelectedIndex(...)`, which fired the tab `ChangeListener`. That listener flushed the *stale* editor text back into `SheetProp` — overwriting the slot `MoveTab` had just shuffled new data into. The result was duplicated content in some tabs and empty content in others. A new `Sui.suppressSheetFlush` guard now suppresses the flush during a structural move and reloads only the destination sheet's content |
| Query Sheets / Tabs | Bug fix | `MoveTab` now handles the case where the selection is already at the destination index (listener would not fire) by reloading the moved content explicitly, keeping the shared editor in sync |
| Query Sheet List | Bug fix | **Drag-reordering is disabled while a column sort is active.** When sorted, the visual row order no longer matches the tab order, so a drop position could not be mapped to a meaningful absolute tab number and a sheet could be moved to the wrong slot. `getSourceActions`, `createTransferable` and `canImport` now check `isSortActive()`; the user clicks **Reset** to clear the sort before reordering |
| Security | Bug fix | **OS command injection (CWE-78) removed from file launch/delete.** New `SafeExec` helper replaces `Runtime.getRuntime().exec("cmd /c start" + " " + path)` in `ExpXLS`, `ExpXLSRS` and `QueryRep`. Default actions now use the shell-free `Desktop` / `Files.deleteIfExists` APIs; a custom launch/delete command is run via the argument-array form of `ProcessBuilder` so the path is always a single, separate argument and shell metacharacters (`& | > ^`) in a result-cell path or generated file name can no longer execute arbitrary commands |
| Security / robustness | Bug fix | `nonSQL` inline-directive parsing now bounds-checks the `=` split before indexing `arr[1]` — a bare `#SET` or `#URL` directive with no value no longer throws `ArrayIndexOutOfBoundsException` |
| ConnDB / BigQuery | Enhancement | Stale BigQuery connections are now evicted even while the app is idle. `evictStaleBigQueryConnections()` is called periodically from the `Garabage` background thread (in addition to the existing opportunistic eviction on the next BigQuery connect), so the max-age limit is enforced without user activity |
| `#URL=` directive | New feature | **`#URL=` now also accepts a connection alias.** `#URL=ALIAS;` resolves the alias to its full JDBC URL (`SUI.CONN.<alias>.URL`) and seeds the alias's configured userid/password into the session credential store so the switch authenticates without a prompt. A full JDBC URL still works exactly as before; the value is tried as an alias first (full value, then first token) and falls back to a literal URL |
| Schema edit functions | Bug fix | **Add / Remove / Replace Schema no longer qualify CTE references.** Names declared in a `WITH ... AS (...)` clause are query-local aliases, not tables, but were being rewritten (e.g. `FROM mycte` → `FROM schema.mycte`). A new `collectCteNames()` helper detects CTE names and the three handlers skip them |
| In-app help | Bug fix | **Documentation popups are now readable.** `HelpDialog` previously inherited the look-and-feel `Panel.background` (a blue tint under some themes) with black text and no explicit HTML colors. The rendered HTML now carries a theme-aware stylesheet (readable text/background, distinct heading and link colors for light and dark themes) and the pane background matches it; fixed-light code blocks and table headers keep dark text |
| Query result window | New feature | **List unique values** added to the column header right-click menu. Collects every distinct value of the selected column with its occurrence count and opens it in a new Query Report window |
| Docs | Enhancement | **SQL Server** sections added to [ConnManager.md](ConnManager.md): *Common JDBC Properties*, *JDBC URL Format*, *Property reference*, *Examples*, *SSL / TLS Setup*, and a *Full SQL Server SSL example with Azure AD* |
| Version | Bump | `0.75V` → `0.75X` (`Ver` string, About dialog, `pom.xml`) |

---

## Details

### Query Sheet content corruption on reshuffle/resort (`Sui.java`, `TabbedPaneClassic.java`, `QuerySheetListPanel.java`)

The editor is a single shared `textArea`; each sheet's SQL lives in `SheetProp`
keyed by tab number (`SQLQUERY.1`, `SQLQUERY.2`, …). The tab `ChangeListener`
flushes the current editor text into the *previous* tab's slot, then loads the
newly-selected tab's slot.

`MoveTab` shuffles all the `SheetProp` slots between source and target and then
selected the destination tab. That selection fired the `ChangeListener`, whose
flush wrote the stale on-screen text over a freshly-shuffled slot — duplicating
the active sheet's content and destroying the data that had legitimately moved.
Repeated moves (especially the many moves a column re-sort can imply) compounded
the damage.

**Fix:** a `volatile boolean Sui.suppressSheetFlush` guard. While set, the
`ChangeListener` skips the flush and only loads the destination sheet; `MoveTab`
wraps its final selection in the guard (with a `finally` reset) and reloads the
content explicitly when the selection index does not change.

### Sheet List drag while sorted (`QuerySheetListPanel.java`)

Added `isSortActive()` (true when any `RowSorter` sort key is set). Drag start
and drop import are both gated on it, so reordering is only possible in true tab
order.

### Shell-free file launch/delete (`SafeExec.java`, `ExpXLS.java`, `ExpXLSRS.java`, `QueryRep.java`)

`SafeExec.launch(configuredCmd, path)` and `SafeExec.delete(configuredCmd, path)`:

- For the default `cmd /c start` / `cmd /c del`, use `Desktop.open(File)` /
  `Files.deleteIfExists(...)` — no shell involved.
- For a user-configured command, split the command on whitespace and append the
  path as a separate `ProcessBuilder` argument, never concatenated into a string
  a shell would re-parse.

### Idle BigQuery eviction (`ConnDB.java`, `Garabage.java`)

`evictStaleBigQueryConnections()` was made package-visible and is now invoked on
each `Garabage` wake-up so cached BigQuery connections older than the configured
max age are closed even when the user is inactive.

### `#URL=` alias support (`nonSQL.java`)

The `#URL=` inline directive now resolves a connection alias in addition to a
literal JDBC URL. Resolution order:

1. The full trimmed value is looked up as an alias (`SUI.CONN.<value>.URL`) —
   this allows aliases containing spaces.
2. Otherwise the first whitespace token is looked up as an alias.
3. If neither matches a configured alias, the first token is used verbatim as a
   literal JDBC URL (original behavior).

When an alias resolves, its `SUI.CONN.<alias>.USERID` / `.PW` are written into
the session credential store (`SUI.USERID.<url>` and `SUI.PW.<userid>.<url>`)
before the switch, so `RunIt` can connect with the alias credentials without a
prompt. Broadcast scripts still emit full URLs and are unaffected.
See [InlineDirectives.md](InlineDirectives.md).

### Schema edit functions skip CTEs (`QryPop.java`)

Add Schema / Remove Schema / Replace Schema matched every identifier after
`FROM` / `JOIN` / `INTO` / `UPDATE` / `TABLE`, including references to CTEs
declared in a `WITH ... AS (...)` clause. A new `collectCteNames(sql)` helper
scans for `WITH name AS (`, `, name AS (` and `WITH name (cols) AS (` and the
three handlers now leave any matched reference whose name is a known CTE
unqualified while still qualifying real tables.

### Readable in-app help (`HelpDialog.java`)

The help pane set its background to `UIManager.getColor("Panel.background")`
while the rendered HTML defined no colors — yielding black text on a blue panel
under some look-and-feels. The HTML now embeds a theme-aware stylesheet
(`Sui.isDarkTheme()`): readable body text/background, distinct heading and link
colors for both themes; code blocks and table headers (fixed light backgrounds)
are forced to dark text. The editor pane background now matches the HTML body.

### List unique values (`QueryRep.java`)

New **List unique values** item on the column header right-click menu. It scans
the selected column, collects each distinct value (first-seen order) with its
occurrence count, and opens the result in a new Query Report window titled
`Unique values of <column> (<n>)`.

---

## Files Changed

| File | Change |
|---|---|
| `src/Sui.java` | `suppressSheetFlush` guard field; `MoveTab` guarded selection + explicit reload; version bump |
| `src/TabbedPaneClassic.java` | `ChangeListener` honours `suppressSheetFlush` |
| `src/QuerySheetListPanel.java` | `isSortActive()`; drag/drop gated while sorted |
| `src/SafeExec.java` | New — shell-free launch/delete helper (CWE-78) |
| `src/ExpXLS.java`, `src/ExpXLSRS.java`, `src/QueryRep.java` | Use `SafeExec` for launch/delete |
| `src/nonSQL.java` | Bounds-check `#SET` / `#URL` directive split; `#URL=` alias resolution + credential seeding |
| `src/QryPop.java` | `collectCteNames()`; Add/Remove/Replace Schema skip CTE references |
| `src/HelpDialog.java` | Theme-aware HTML stylesheet + matching pane background for readable docs |
| `src/QueryRep.java` | Use `SafeExec` for launch/delete; **List unique values** column menu item |
| `src/ConnDB.java`, `src/Garabage.java` | Idle BigQuery connection eviction |
| `docs/ConnManager.md` | SQL Server JDBC properties & SSL/TLS setup |
| `docs/InlineDirectives.md` | `#URL=ALIAS` form documented |
| `SuiNews.txt` | `#URL=ALIAS` note |
| `pom.xml` | Version `0.75V` → `0.75X` |
