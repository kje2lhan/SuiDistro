# Release Notes — Sui 0.75A

**Branch:** `Sui075A`  
**Base:** `master` @ `079052c` (2026-03-22 — "Fix schema list")  
**Date:** 2026-04-04  
**Commits in this release:** 11

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| BigQuery connections | Feature | Keep-alive cache with 10-hour TTL |
| BigQuery result sets | Fix | Row limit enforced to prevent unbounded fetches |
| Connection shutdown | Feature | All cached connections closed at exit with elapsed-time log |
| DConnInf | Feature | Complete rewrite — shows ~80 JDBC metadata properties |
| JDBC compatibility | Fix | Guards for `AbstractMethodError` (JDBC 4.0/4.1) and `SQLException` (Mimer) |
| Garabage thread | Fix | Interrupt handling, stale comments, dead code removed |
| Store* methods | Fix | Race condition eliminated — all 7 methods now `synchronized` |
| Build versioning | Feature | Maven-filtered `build.properties` bakes version + timestamp into jar |
| About dialog | Feature | Shows `Build: <version> built <timestamp>` |
| DatabaseManager | Feature | New helper class added |
| Image assets | Housekeeping | All images moved from `src/` to `src/imgs/` |
| Unused classes | Housekeeping | 15 unused source files moved to `src/unused/` |
| POM dependencies | Security | 3 dependencies updated to remove known vulnerabilities |
| Documentation | New | 8 new documentation files created |

---

## Detailed Changes by File

### Source Code

#### `src/ConnDB.java` — BigQuery connection cache + shutdown close
- Added `ConnInfo` inner class holding `conn`, `valid`, and `createdAt` timestamp.
- Added static LRU cache (`LinkedHashMap`, max 20 entries) **exclusively for BigQuery connections**.
- Added `BIGQUERY_MAX_AGE_MS` constant (10 hours).
- Added `evictStaleBigQueryConnections()` — prunes cache entries older than 10 hours.
- `getConn()`: BigQuery connections are served from cache on repeat calls; TTL eviction runs first. Non-BigQuery connections always open fresh via `DriverManager`.
- `closeConn()`: BigQuery connections are intentionally **not** closed (cache reuse); all others close normally.
- **New** `closeAllConnections()` static method: closes every cached connection at shutdown, prints `Connection [url|uid] closed after X minutes` for each, then clears the cache.

#### `src/DConnInf.java` — Complete rewrite
- Now displays approximately 80 `DatabaseMetaData` properties grouped into sections: basic info, capacity limits, SQL grammar support, null sorting, identifier handling, feature flags, transaction support.
- Three JDBC-version-specific methods individually guarded:
  - `getRowIdLifetime()` — `catch (AbstractMethodError)` (JDBC 4.0)
  - `autoCommitFailureClosesAllResultSets()` — `catch (AbstractMethodError)` (JDBC 4.0)
  - `generatedKeyAlwaysReturned()` — `catch (AbstractMethodError)` (JDBC 4.1)
  - `locatorsUpdateCopy()` — `catch (SQLException)` (Mimer: "Optional feature not implemented")
- Results displayed in a `QueryRep` panel (600×700).

#### `src/RunIt.java` — BigQuery row limit + image path fixes
- Row limit now enforced for BigQuery result sets to prevent runaway memory use.
- Image references updated to `imgs/` subfolder.

#### `src/Garabage.java` — Thread safety and comment fixes
- `InterruptedException` now calls `break` immediately instead of falling through to the rest of the loop body — prevents a spurious partial save iteration after `ShutDown()` calls `interrupt()`.
- Removed redundant `i = 0` reset after the `(i % 30) == 0` periodic save block.
- Removed no-op `Thread.currentThread()` call.
- Comments corrected: "60:th time" → "every 30th wake-up"; "59:th time" → "every 61st wake-up"; typos "interupted" and "extarnalizes" fixed.

#### `src/Sui.java` — Synchronized saves + build info + shutdown + image paths
- All 7 `.pro` file save methods marked `synchronized` to eliminate the race condition between the Garabage background thread and the EDT:
  - `StoreProf()`, `StoreProp()`, `StoreSheetProp()`, `StoreConnProp()`, `StoreCPProp()`, `StoreKeywProp()`, `StoreTmpProp()`
- About dialog updated to show `Build: <version> built <timestamp>` (via `BuildInfo.getBuildId()`).
- `ShutDown()` now calls `ConnDB.closeAllConnections()` before `System.exit(0)`.
- All image references updated to `imgs/` subfolder.

#### `src/BuildInfo.java` — New file
- Reads `build.properties` from classpath at class-load time (static initialiser).
- Exposes `getVersion()`, `getTimestamp()`, `getBuildId()` static methods.
- Gracefully falls back to `"unknown"` if the resource is missing.

#### `src/build.properties` — New file
- Maven filter template:
  ```
  build.version=${project.version}
  build.timestamp=${maven.build.timestamp}
  ```
- Replaced with actual values by Maven resource filtering at build time.

#### `src/DatabaseManager.java` — New file
- New helper class for database management operations.

#### Image assets — `src/` → `src/imgs/`
- All ~170 image files (`.gif`, `.png`) moved to `src/imgs/`.
- Path references updated in: `FavPop`, `FavQry`, `Propm`, `PropmAll`, `QryPop`, `QueryRep`, `RunIt`, `ShowQryBox`, `Sui`, `SuiTb`, `Propmc`, `Propmcp`, `PropmMisc`, `PropmSheetA`.

#### Unused classes — `src/` → `src/unused/`
15 source files moved, no longer part of the active build:

| File |
|---|
| `DirectoryReader.java` |
| `DirectoryWriter.java` |
| `GetJar.java` |
| `ImpXLSt.java` |
| `JComboBox.java` |
| `LineNumbering.java` |
| `LoadFromJar.java` |
| `PrintComponents.java` |
| `PropEdit.java` |
| `PropcS.java` |
| `PropmCAll.java` |
| `Propmap.java` |
| `ResultsModel.java` |
| `RowHeaderExample.java` |
| `SrchAdapter.java` |
| `SrchSheet.java` |
| `SymbThd.java` |
| `TImpXLS.java` |
| `TextFilter.java` |
| `TextPrinter.java` |
| `URLClassLoad.java` |

---

### Build (`pom.xml`)

- Version changed from `0.0.1-SNAPSHOT` to **`0.75A`**.
- Added `<maven.build.timestamp.format>yyyy-MM-dd HH:mm</maven.build.timestamp.format>` property.
- Resource block split: `build.properties` filtered separately so Maven tokens are substituted; all other resources left unfiltered.
- **3 dependency versions updated** to remove known security vulnerabilities.

---

### Documentation (all new files)

| File | Contents |
|---|---|
| `USAGE.md` | End-user usage guide |
| `docs/ConnDB.md` | ConnDB connection factory logic, BigQuery caching, TTL eviction, `closeAllConnections()` shutdown procedure |
| `docs/SuiHome.md` | Sui home directory resolution chain, `Sui.ini` syntax, symbolic token expansion, Look and Feel / FlatLaf configuration |
| `docs/ProFileRecovery.md` | All `.pro` files described, SuiBup backup folder, Garabage periodic save/backup schedule, recovery procedures |
| `docs/hierarchy-Sui.md` | Sui class call and dependency hierarchy |
| `docs/hierarchy-RunIt.md` | RunIt class call hierarchy |
| `docs/hierarchy-RunItB.md` | RunItB class call hierarchy |
| `docs/unreferenced-classes.md` | Classes with no detected callers in the active source tree |

---

## Commit Log

| Hash | Date | Message |
|---|---|---|
| `3c4a162` | 2026-04-01 | Keep connections for BigQuery |
| `208f34a` | 2026-04-01 | Set limit for BigQuery |
| `732ede7` | 2026-04-01 | Created subfolder for images |
| `27be3fb` | 2026-04-04 | Additional ConnDB caching fixes; DConnInf complete rewrite |
| `18c715a` | 2026-04-04 | Doc describing setting SuiHome |
| `988fb60` | 2026-04-04 | Added section about look and feel |
| `e09d3a6` | 2026-04-04 | Added Profile Recovery description |
| `c2f78a6` | 2026-04-04 | Fixed Garabage class (interrupt, dead code, comments) |
| `0e685af` | 2026-04-04 | Fixed Sui version and build info |
| `50d7ca1` | 2026-04-04 | Added logic to close connections in cache at close down |
| `580c5d5` | 2026-04-04 | Fixed POM dependencies to avoid vulnerabilities |
