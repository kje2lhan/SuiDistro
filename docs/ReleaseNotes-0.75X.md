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

---

## Files Changed

| File | Change |
|---|---|
| `src/Sui.java` | `suppressSheetFlush` guard field; `MoveTab` guarded selection + explicit reload; version bump |
| `src/TabbedPaneClassic.java` | `ChangeListener` honours `suppressSheetFlush` |
| `src/QuerySheetListPanel.java` | `isSortActive()`; drag/drop gated while sorted |
| `src/SafeExec.java` | New — shell-free launch/delete helper (CWE-78) |
| `src/ExpXLS.java`, `src/ExpXLSRS.java`, `src/QueryRep.java` | Use `SafeExec` for launch/delete |
| `src/nonSQL.java` | Bounds-check `#SET` / `#URL` directive split |
| `src/ConnDB.java`, `src/Garabage.java` | Idle BigQuery connection eviction |
| `docs/ConnManager.md` | SQL Server JDBC properties & SSL/TLS setup |
| `pom.xml` | Version `0.75V` → `0.75X` |
