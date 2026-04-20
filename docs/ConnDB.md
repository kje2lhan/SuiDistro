# ConnDB — Logic Description

## Purpose

`ConnDB` is a JDBC connection factory. Each instance holds credentials and a URL for one database. It provides `getConn()` to obtain a `Connection`, `closeConn()` to release it, and `isConnValid()` to check whether a cached connection is still healthy.

A static LRU cache is maintained exclusively for BigQuery connections. Because BigQuery requires an OAuth round-trip to establish a connection, cached connections are reused for up to 10 hours and never explicitly closed. All other DBMS types always open a fresh connection on each `getConn()` call.

> **Note:** `DatabaseManager` delegates connection establishment to `ConnDB.getConn()`, so `SuiConnPref.pro` properties (including BigQuery OAuth settings) are always applied whether the caller uses `ConnDB` directly or via `DatabaseManager`.

---

## Class-Level Fields

| Field | Type | Description |
|---|---|---|
| `Uid` | `String` | Database username (final) |
| `Pw` | `String` | Database password (final) |
| `url` | `String` | JDBC URL, trimmed on construction (final) |
| `conn` | `Connection` | The most recently obtained connection for this instance |

---

## Static Cache

```
LinkedHashMap<String, ConnInfo>   connCache
```

Used **exclusively for BigQuery connections**. Non-BigQuery connections are never stored in or read from this cache.

- **Key**: `url + "|" + Uid` — uniquely identifies a (URL, user) pair.
- **Capacity**: max 20 entries. The `removeEldestEntry` override evicts the Least Recently Used entry once the map exceeds 20.
- **Access order**: constructed with `accessOrder = true`, so `get()` calls count as "use" for LRU purposes.
- **Constants**:
  - `MAX_CACHE_SIZE = 20`
  - `BIGQUERY_MAX_AGE_MS = 10 hours` — maximum age of a cached BigQuery connection before it is considered stale.

### `ConnInfo` (inner class)

Wraps a `Connection` with two extra fields:

| Field | Meaning |
|---|---|
| `conn` | The `Connection` object |
| `valid` | Result of `conn.isValid(2)` at connection time |
| `createdAt` | `System.currentTimeMillis()` at construction |

---

## Constructor

```java
ConnDB(String urlin, String user, String PwIn)
```

Simple value assignment. The URL is `trim()`-ed to strip accidental whitespace.  
No connection is actually opened at construction time — that is deferred to `getConn()`.

---

## `evictStaleBigQueryConnections()` (private static)

Scans every entry in `connCache` and removes any whose URL contains `"bigquery"` and whose age exceeds `BIGQUERY_MAX_AGE_MS` (10 hours).

- Uses `removeIf` on the entry set, so each removed entry is also deleted from the map.
- For each stale entry, `conn.close()` is called if the connection is non-null and not already closed. Any `SQLException` during close is silently ignored (the eviction proceeds regardless).
- Only called from `getConn()` and only when the current URL is a BigQuery URL.

---

## `getConn()` — Main Flow

```
getConn()
  │
  ├─ Build cache key  (url + "|" + Uid)
  ├─ Detect BigQuery  (url contains "bigquery", case-insensitive)
  │
  ├─ [BigQuery only]
  │     ├─ evictStaleBigQueryConnections()   ← prune expired entries
  │     └─ cache hit?  → return cached conn immediately
  │
  ├─ Build Properties object
  │     ├─ If credentials non-empty → set "user" / "password"
  │     └─ If SuiConnPref.pro available → merge extra driver properties
  │           (resolves "&suihome" token → actual Sui home directory)
  │
  ├─ DriverManager.getConnection(url, props)
  ├─ conn.setAutoCommit(false)
  ├─ Sui.PutTmpProp2(...)   ← stores password in temp props (for reconnect)
  ├─ conn.isValid(2)        ← 2-second validity check
  │
  └─ [BigQuery only]  store in cache (refreshes TTL on every call)
```

### Connection preferences (`SuiConnPref.pro`)

When `Sui.isConnPrefAvailable()` returns `true`, the method iterates over all keys in the preferences file. Each key has the form `<url-prefix>.<driver-property>`. If the current JDBC URL starts with a key's prefix, the corresponding value is added to the `Properties` object passed to `DriverManager`.

A special token `&suihome` in a preference value is replaced with the Sui home directory path (backslashes and colons escaped for JDBC URL safety).

---

## `isConnValid()`

Looks up the cache entry for the current (url, user) pair and returns `cached.valid`. Returns `false` if no entry exists. Because only BigQuery connections are cached, this method effectively always returns `false` for non-BigQuery connections. It does **not** retest the live connection.

---

## `closeConn()`

| URL type | Behaviour |
|---|---|
| BigQuery | Returns immediately — BigQuery connections are intentionally kept open and reused from the cache. |
| All others | Closes `conn` if it is non-null and not already closed. |

For BigQuery, the connection is never removed from the cache on close — it stays available for reuse until TTL-based eviction removes it. Non-BigQuery connections are not in the cache at all.

---

## `closeAllConnections()` (static)

Called once during application shutdown (from `Sui.ShutDown()`). Closes every connection that is still open in the cache — including BigQuery connections that `closeConn()` would otherwise skip — and logs a message for each one:

```
Connection [url|uid] closed after X minutes
```

The elapsed time is derived from `ConnInfo.createdAt`, giving the number of full minutes between when the connection was established and when shutdown occurred. After the loop, `connCache` is cleared.

```
closeAllConnections()
  │
  ├─ for each entry in connCache
  │     ├─ skip if conn is null or already closed
  │     ├─ compute minutes = (now - info.createdAt) / 60000
  │     ├─ conn.close()
  │     └─ println "Connection [key] closed after X minutes"
  │           (any SQLException during close is silently ignored)
  │
  └─ connCache.clear()
```

This ensures that no database server-side sessions are leaked when the user closes Sui.

---

## Design Notes

- **BigQuery caching only**: The cache is exclusively for BigQuery. Every non-BigQuery `getConn()` call opens a fresh `DriverManager` connection — no lookup, no store. This keeps the cache small and avoids inadvertently reusing stale connections for DBMS types that expect short-lived sessions.
- **BigQuery TTL**: BigQuery JDBC connections carry an OAuth handshake that makes them much slower to establish. The 10-hour TTL prevents indefinite reuse of an expired token, while the "never close" policy avoids unnecessary re-authentication.
- **`autoCommit = false`**: All connections disable auto-commit, so callers are responsible for explicit `commit()` / `rollback()`.
- **Shutdown cleanup**: `closeAllConnections()` provides a final sweep at shutdown — closing all cached connections (including BigQuery) regardless of type, so no server-side sessions are orphaned after Sui exits.

---

## Future Improvements

### Configurable connection-keep policy (replace BigQuery hardcoding)

Currently the string `"bigquery"` is embedded in the logic at three points: eviction, cache lookup, and `closeConn()`. A cleaner design would externalise this into a per-URL (or per-driver) policy, so other DBMS types that share the same characteristics (slow authentication, long-lived tokens) can benefit without code changes.

Possible approaches:

| Approach | Description |
|---|---|
| **Property flag in `SuiConnPref.pro`** | Add a `sui.keepAlive=true` key under a URL prefix. `ConnDB` reads it during `getConn()` and replaces the `isBigQuery` checks with `isKeepAlive`. No hardcoded strings anywhere. |
| **`driver.pro` entry** | Extend the existing driver properties file with a `keepAlive` attribute per driver entry. `ConnDB` consults it via `Sui.GetDriverProp()` at connection time. |
| **Static set in `ConnDB`** | A `Set<String> KEEP_ALIVE_PATTERNS` constant that can be populated from configuration at startup — easily extensible without touching core logic. |

The recommended approach is **property flag in `SuiConnPref.pro`** since that file is already read during `getConn()` and gives per-URL control without any new infrastructure. The TTL (`BIGQUERY_MAX_AGE_MS`) could similarly become a per-URL property (`sui.maxAgeHours=10`), defaulting to the current 10-hour value when not specified.
