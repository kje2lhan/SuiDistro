# Recovering from a Corrupted .pro File

## Overview

Sui stores its configuration in a set of Java `.properties`-format files (extension `.pro`) in the `SuiHome` directory. Sui maintains two layers of backup to help recover from accidental corruption:

1. **`.bak` file** — a single-generation rollback written during every save, kept alongside the live file in `SuiHome`.
2. **`SuiBup/` folder** — a timestamped snapshot of all `.pro` files copied at every clean shutdown, with files older than 30 days automatically deleted.

---

## The `.pro` Files

| File | Purpose |
|---|---|
| `SuiSys.pro` | Core application settings — query history, window layout, font, Look & Feel choice, max rows, and other UI preferences |
| `SuiSheetProp.pro` | SQL statements saved in each sheet (tab) of the Sui Query window |
| `SuiConnProp.pro` | All saved database connection definitions — JDBC URLs, usernames, driver references |
| `SuiConnPref.pro` | Optional per-URL JDBC driver properties (extra connection attributes, `&suihome` path tokens etc.) — user-maintained, not written by Sui at shutdown |
| `SuiCPProp.pro` | Classpath entries for dynamically loaded JDBC driver jars |
| `SuiKeywProp.pro` | SQL keyword highlighting definitions |
| `TmpProp.pro` | Temporary session values (passwords cached for reconnect etc.) |

---

## How Files Are Saved (Safe Write Pattern)

Each `.pro` file is saved using a write-to-temp-then-rename pattern to prevent partial writes from corrupting the live file:

```
1. Write new content → SuiSys.pro.tmp
2. Rename SuiSys.pro  →  SuiSys.pro.bak   (preserves the previous version)
3. Rename SuiSys.pro.tmp  →  SuiSys.pro   (atomic promotion)
4. If step 3 succeeds → delete SuiSys.pro.bak
   If step 3 fails    → rename SuiSys.pro.bak back to SuiSys.pro  (restore)
```

This pattern is used identically for `SuiConnProp.pro`, `SuiSheetProp.pro`, `SuiSys.pro`, `SuiCPProp.pro`, `SuiKeywProp.pro`, and `TmpProp.pro`.

> If you see a `.tmp` file alongside a `.pro` file and Sui is not running, it means a previous save was interrupted. The `.pro` file itself is still intact (the rename had not yet happened), so the `.tmp` can be safely deleted.

---

## Automatic Fallback on Load

When Sui starts it immediately tries to load each `.pro` file. If loading fails (file missing, truncated, or unparseable), it **automatically falls back to the `.bak` file** in the same directory:

```
Load SuiSheetProp.pro   → fails
  → try SuiSheetProp.pro.bak
      → succeeds: "Loaded from backup"
      → fails:    "Backup also failed"  (Sui starts with defaults)
```

The same two-step try/fallback is in place for `SuiSys.pro`, `SuiConnProp.pro`, and `SuiSheetProp.pro`. This means a single corruption event is almost always recovered automatically without user intervention.

---

## The `SuiBup/` Folder

At every clean shutdown, Sui copies all `.pro` files from `SuiHome` into `SuiHome/SuiBup/`. Files in `SuiBup/` that are older than **30 days** are automatically deleted at the same time.

```
ShutDown()
  ├─ Save all properties (StoreProf)
  ├─ Create SuiBup/ if it does not exist
  ├─ CopyDir(SuiHome → SuiBup, filter=".pro")   ← snapshot
  └─ DelFilesOlder(30 days, SuiBup/)             ← rotation
```

### Periodic saves and backups while Sui is running (`Garabage` thread)

Sui also runs a background utility thread (`Garabage`) that wakes up on a fixed interval (`Mil` milliseconds) and performs two periodic housekeeping tasks independently of shutdown:

| Counter | Action |
|---|---|
| Every 30th wake-up | Calls `Sui.StoreProf()` — saves all `.pro` files to disk (same safe-write pattern as shutdown) |
| Every 61st wake-up | Copies all `.pro` files to `SuiBup/` (same `CopyDir` call as shutdown, but **without** the 30-day rotation) |

This means that even in a long-running session that never cleanly shuts down, both the live `.pro` files and the `SuiBup/` snapshots are refreshed periodically. A crash between two periodic saves loses at most `30 × Mil` milliseconds of changes to the live files, and at most `61 × Mil` milliseconds of changes to the `SuiBup/` snapshots.

> **Note:** The in-session `SuiBup` copy does not run `DelFilesOlder` — old snapshot files in `SuiBup/` are only pruned at clean shutdown.

---

## Recovery Procedures

### Situation A — Sui starts but reports a corrupt file (automatic recovery)

Sui will fall back to the `.bak` automatically and print a message to the console. No manual action is needed unless the `.bak` is also bad (see Situation B).

---

### Situation B — Both the `.pro` and the `.bak` are corrupt

Use a file from `SuiBup/`. The files there are plain text Java properties files and can be opened in any text editor.

#### Recover `SuiSys.pro` (application settings)

1. Close Sui if it is running.
2. Open `SuiHome\SuiBup\` in File Explorer and sort by date.
3. Copy the most recent `SuiSys.pro` from `SuiBup\` to `SuiHome\`.
4. Also copy it to `SuiHome\SuiSys.pro.bak` if you want the fallback slot populated.
5. Start Sui — it loads the restored file. You may lose settings changed since that snapshot, but all earlier preferences (query history, window layout, etc.) will be restored.

#### Recover `SuiSheetProp.pro` (SQL statements per sheet)

1. Close Sui if it is running.
2. Copy the most recent `SuiSheetProp.pro` from `SuiHome\SuiBup\` to `SuiHome\`.
3. Start Sui — the SQL statements saved in each sheet tab of the Query window will be restored to the state at the snapshot time.

   > If no snapshot is useful, simply delete `SuiSheetProp.pro` and `SuiSheetProp.pro.bak`. Sui will start with empty sheets and create a fresh file on next shutdown.

#### Recover `SuiConnPref.pro` (per-URL driver connection preferences)

`SuiConnPref.pro` is different from the other files in two important ways:

- Sui **never writes it** — it is created and maintained manually by the user.
- It has **no `.bak` fallback** — if it is missing or unreadable on startup, Sui simply sets `ConnPrefIsAvailable = false` and continues without connection preferences (no error, no crash).

This means:
- If it is corrupted or accidentally deleted, Sui will start normally but will no longer inject the extra driver properties when opening connections.
- The only source of recovery is a snapshot in `SuiBup/` (since `CopyDir` copies all `.pro` files at shutdown).

**Recovery steps:**
1. Close Sui if it is running.
2. Copy the most recent `SuiConnPref.pro` from `SuiHome\SuiBup\` to `SuiHome\`.
3. Start Sui — per-URL connection preferences will be active again.

   > If no `SuiBup/` snapshot exists (e.g. Sui was never shut down cleanly after the file was created), the file must be recreated manually. See `ConnDB.md` for the key syntax and the `&suihome` token.

---

#### Recover `SuiConnProp.pro` (connection definitions)

`SuiConnProp.pro` is the most critical file — it holds all your saved JDBC URLs and usernames. Losing it means re-entering every connection manually.

1. Close Sui if it is running.
2. Open `SuiHome\SuiBup\` and locate the most recent `SuiConnProp.pro`. You can open it in a text editor to verify your connection entries are present — each entry looks like:
   ```
   SUI.URL.0=jdbc\:db2\://myhost\:50000/MYDB
   SUI.UID.0=db2admin
   SUI.DRIVER.0=com.ibm.db2.jcc.DB2Driver
   ```
3. Copy the chosen `SuiConnProp.pro` from `SuiBup\` to `SuiHome\`.
4. Also copy it to `SuiHome\SuiConnProp.pro.bak`.
5. Start Sui — all connection definitions from that snapshot will be available.

   > If you added new connections between the snapshot date and the corruption event, those will be lost. Check `SuiConnProp.pro.bak` first — it may be more recent than the `SuiBup/` snapshot if the file was saved correctly at least once after you added those connections.

---

## File Location Quick Reference

Assuming `SuiHome = C:\Users\kjell\AppData\Sui\`:

| File | Path |
|---|---|
| Live file | `C:\Users\kjell\AppData\Sui\SuiConnProp.pro` |
| Single-generation backup | `C:\Users\kjell\AppData\Sui\SuiConnProp.pro.bak` |
| Snapshot folder | `C:\Users\kjell\AppData\Sui\SuiBup\` |
| Interrupted save artifact | `C:\Users\kjell\AppData\Sui\SuiConnProp.pro.tmp` (safe to delete) |

---

## Summary

| Layer | Written | Covers | Retention |
|---|---|---|---|
| `.bak` file (in SuiHome) | Every save (shutdown + periodic) | Previous single version | Until next save overwrites it |
| `SuiBup/` snapshot (shutdown) | Every clean shutdown | All `.pro` files + 30-day rotation | 30 days rolling |
| `SuiBup/` snapshot (periodic) | Every 61st `Garabage` wake-up | All `.pro` files, no rotation | Until next clean shutdown prunes old files |
| Periodic `.pro` save | Every 30th `Garabage` wake-up | All `.pro` files in SuiHome | Overwrites previous with `.bak` preserved |
| Automatic startup fallback | On load failure | `.bak` only | N/A — read only |
