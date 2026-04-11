# Release Notes — Sui 0.75B

**Branch:** `master`  
**Base:** `5b14649` (2026-04-04 — Merge PR #27 "Sui075A")  
**Date:** 2026-04-07  
**Commits in this release:** 7 (PRs #29, #31 + direct commits `12706f7`, `6cf65cc`, `940bbc3`)

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Security | Fix | Command injection in "Send query to" mail feature eliminated |
| BigQuery / SuiConnPref | Fix | `DatabaseManager` now delegates to `ConnDB`, ensuring `SuiConnPref.pro` properties are applied |
| Preferences persistence | Fix | Connection and classpath properties now saved immediately when preferences dialog is closed |
| Resource management | Fix | `FileOutputStream` in `StoreProf()` wrapped in try-with-resources — eliminates file-handle leak |
| Internal | Refactor | `StoreConnProp()` / `StoreCPProp()` made package-private; removed redundant calls from `StoreProf()` |
| Documentation | New | `docs/CredentialHandling.md` — full description of userid/password handling |
| Documentation | Update | `docs/ConnDB.md` — note added on `DatabaseManager` / `ConnDB` delegation |
| Documentation | Update | `README.md` — Sui 0.75A section added |

---

## Detailed Changes by File

### Source Code

#### `src/Sui.java` — Security fix + resource leak fix + internal refactor

**Security — command injection eliminated (`MailMenuItem`)**
- The "Send query to" menu item previously built a shell command string using
  `Runtime.getRuntime().exec("cmd.exe /c start ...")`, concatenating unsanitised
  query text directly into the command. Any shell metacharacter in the SQL editor
  could trigger arbitrary command execution on the local machine.
- Replaced with `Desktop.getDesktop().mail(URI)` using a properly constructed
  `java.net.URI` object. The query body is passed as the URI query component —
  no shell is involved.
- Added `import java.net.URI`.

**Resource leak fix — `StoreProf()`**
- `FileOutputStream` for `QueryList<Desktop>.pro.tmp` was not in a try-with-resources
  block; a failure in `QueryProp.store()` would leave the file handle open and the
  temporary file locked.
- Replaced bare `new FileOutputStream` + manual `.close()` with a try-with-resources
  block — the stream is now always closed, even on exception.

**Internal — `StoreConnProp()` / `StoreCPProp()` visibility and call sites**
- Both methods changed from `private` to package-private so that `PropmAll` and
  `Propmc` can call them directly (see below).
- Removed the calls to `StoreConnProp()` and `StoreCPProp()` from `StoreProf()`.
  These property files are now saved only when the user explicitly saves preferences,
  not on every application shutdown profile store.

**Cosmetic**
- About dialog: corrected capitalisation from `"SUI 0.75AA"` to `"Sui 0.75AA"`.

---

#### `src/DatabaseManager.java` — Use `ConnDB` instead of `DriverManager` directly

- `DatabaseManager` previously called `DriverManager.getConnection(url, user, password)`
  directly, bypassing the connection-preference layer in `ConnDB`. This meant that
  properties from `SuiConnPref.pro` (including BigQuery OAuth settings applied via
  `SuiConnPref`) were silently ignored for any caller that went through
  `DatabaseManager`.
- Refactored to hold a `ConnDB` instance and delegate to `cDB.getConn()`.
  `ConnDB.getConn()` sets `autoCommit=false` on new connections and handles the
  BigQuery LRU cache, so both behaviours are preserved.
- `close()` now calls `cDB.closeConn()` instead of `conn.close()` directly, ensuring
  BigQuery connections are returned to the cache rather than closed.
- Added clarifying comment: `ConnDB.getConn()` sets `autoCommit=false` on newly
  created connections and returns cached BigQuery connections that already have
  `autoCommit=false`.

---

#### `src/PropmAll.java` — Persist connection and classpath properties on save

- Both the **OK** (save and close) and **Apply** (save without closing) action listeners
  now call `Sui.StoreCPProp()` after `Sui.StoreProp()`.
- Previously, changes made in the classpath panel of the preferences dialog were not
  written to `SuiCPProp.pro` until application shutdown.

---

#### `src/Propmc.java` — Persist connection and classpath properties on save

- The **Save** and **Save and Close** button action listeners now call
  `Sui.StoreConnProp()` and `Sui.StoreCPProp()` after updating the URL/driver lists.
- Previously, JDBC resource changes (new connections, driver entries) were only
  written to `SuiConnProp.pro` at shutdown, meaning changes were lost if the
  application crashed or was force-killed.

---

### Documentation

#### `docs/CredentialHandling.md` — New file

Complete description of how user IDs and passwords are handled throughout the
application. Covers:

- Startup loading from `SuiSys.pro`
- The connect flow and in-memory session cache (`TmpProp2`)
- Alt-key profiles (Alt+0…9)
- The only path to disk: user-initiated save via the Login/Preferences dialog
- Summary table of all credential stores (object, file, persistence)
- Security recommendations for corporate environments

> **Key finding documented:** `TmpProp2` (the per-session password cache used by
> tab switching, `AppendToTable`, `SQLSeqComp`, etc.) is **never written to disk**.
> The password only reaches disk if the user explicitly saves it via
> Sui Preferences → Login.

#### `docs/ConnDB.md` — Updated

Added a note clarifying that `DatabaseManager` delegates connection establishment to
`ConnDB.getConn()`, so `SuiConnPref.pro` properties (including BigQuery OAuth
settings) are always applied whether the caller uses `ConnDB` directly or via
`DatabaseManager`.

#### `README.md` — Updated

Added Sui 0.75A section summarising the features and fixes in that release.

---

## Security Notes

| Issue | Severity | Fix |
|-------|----------|-----|
| Command injection in "Send query to" (`MailMenuItem`) | High | `Runtime.exec` replaced with `Desktop.getDesktop().mail(URI)` |
| File handle leak in `StoreProf()` | Medium | try-with-resources added for `FileOutputStream` |

---

## Upgrade Notes

- No property file format changes. Existing `SuiSys.pro`, `SuiConnProp.pro`, and
  `SuiCPProp.pro` files are fully compatible.
- Users who experienced JDBC connection-preference settings (from `SuiConnPref.pro`)
  being ignored when queries run via `RunIt` should see these applied correctly after
  this release.
- Connection and classpath preferences are now saved immediately when the preferences
  dialog is closed, rather than at application shutdown. This means changes survive an
  unexpected application termination.
