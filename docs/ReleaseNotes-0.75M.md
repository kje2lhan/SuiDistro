# Release Notes — Sui 0.75M

**Branch:** `Sui0.75K`  
**Base:** `Sui 0.75L` (SQL Dialect Converter)  
**Date:** 2026-05-09  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Connection Manager | New feature | New `ConnManager` dialog — unified connection profile editor replaces the old `connP` dialog |
| Connection Manager | New feature | Left panel: named connection list with New, Copy, Remove buttons |
| Connection Manager | New feature | Tab 1 (Connection): Alias, Driver, Server, Port, Database, SID, URL, User, Password, Auto-login, Test Connection |
| Connection Manager | New feature | Tab 2 (Driver / JAR): global driver catalog — Name, Driver Class, JAR path, Status (✔ Registered / ✔ On classpath / ✘ Not loaded); Browse JAR, Reload JARs |
| Connection Manager | New feature | Tab 3 (JDBC Properties): editable key/value table backed by `SuiConnPref.pro` |
| Connection Manager | New feature | URL auto-fills from driver template as Server/Port/Database/SID fields are typed |
| Connection Manager | New feature | URL field is also directly editable for custom or non-template URLs |
| Connection Manager | New feature | Driver auto-detected from URL prefix when loading legacy profiles |
| Connection Manager | New feature | "Test Connection" button — opens a live JDBC connection and reports success or error inline |
| Connection Manager | New feature | Password only written to disk when Auto-login is explicitly ticked (security gate) |
| Connection Manager | Migration | Auto-migrates legacy `connprop.pro` entries and old `SUI.JDBCURL.0.N` keys to new `SuiConnProp.pro` format on first Save |
| Main Panel | New feature | URL selection auto-fills userid from saved connection profile when field is blank |
| Main Panel | New feature | URL selection auto-fills password when `AUTOLOGIN=Y` and a saved password exists |
| Preferences → Keywords | New feature | New Keywords tab — editable table of F1 auto-completion shortcuts (Trigger / Expansion / Description) |
| F1 Auto-completion | New feature | Bundled `keyw.pro` — 30 default SQL keyword completions loaded from JAR |
| F1 Auto-completion | Enhancement | Keyword merge: bundled defaults as base; user edits in `SuiKeywProp.pro` override same-trigger entries |
| ConnDB | Bug fix | MariaDB: `ArrayIndexOutOfBoundsException` when port field is blank — stray colon stripped from URL |

---

## Detailed Changes by Area

---

### Connection Manager (new `ConnManager.java`)

The old `connP` dialog has been replaced by a fully redesigned **Connection Manager**
(`ConnManager.java`), accessible from the **File** menu as **Connection Manager…**.
It provides a single place to create, edit, and test all JDBC connection profiles, manage
driver JARs, and configure JDBC connection properties.

---

#### Layout

The dialog is 860 × 580 px and is split into two areas:

- **Left panel** — scrollable list of saved connection aliases.
  - **New** — adds a blank profile.
  - **Copy** — duplicates the selected profile (Auto-login flag is never copied).
  - **Remove** — marks the selected profile for deletion; removal is committed on Save.
- **Right area** — three-tab panel.

---

#### Tab 1: Connection

The primary editing form. Fields adapt dynamically based on the selected driver.

| Field | Notes |
|---|---|
| Alias | Unique name for this profile; shown in the main panel URL combobox |
| Driver | Combobox populated from `driver.pro` bundled in `Sui.jar` |
| Server | Hostname; hidden for drivers whose URL template has no `&server` placeholder |
| Port | Port number; hidden when not in the driver template |
| Database | Database / schema name; labelled "Project" for BigQuery |
| SID | Oracle SID; shown only for Oracle templates |
| URL | Auto-filled as Server/Port/Database/SID are typed. Fully editable — typing directly overrides the template. |
| User | JDBC user ID |
| Password | Echo-masked; **Show/Hide** toggle button |
| Auto-login | When ticked: password is written to `SuiConnProp.pro` on disk and auto-injected into the main panel on URL selection. **Never enabled by default.** |
| Test Connection | Opens a live `DriverManager.getConnection()` call; displays ✔ or the exception message inline |

**URL auto-fill:** As the user types into Server, Port, Database, or SID the URL field is
continuously recomputed by substituting the values into the driver's URL template
(e.g. `jdbc:db2://&server:&port/&dbname`). The URL field can also be edited directly
at any time; the individual fields are then not re-parsed back (they retain their
last values).

**Driver auto-detection:** When a legacy profile is loaded that has a URL but no
individual server/port/database fields, `ConnManager` reverse-parses the URL using the
best-matching driver template and populates the fields automatically.

---

#### Tab 2: Driver / JAR

A global driver catalog that is independent of the currently selected connection.
Changes here apply to *all* connections that use the affected driver class.

| Column | Notes |
|---|---|
| Name | Display name — editable |
| Driver Class | Fully qualified class name — editable |
| JAR / Path | Path to the driver JAR; supports `*.jar` glob patterns to load all JARs in a folder |
| Status | ✔ Registered / ✔ On classpath / ✔ In JAR / ✘ Not loaded — colour-coded green/red |

**Buttons:**
- **Add** — adds a blank custom driver row.
- **Remove** — removes the selected row.
- **Browse JAR…** — file chooser pre-seeded to the current JAR's directory.
- **Reload JARs** — persists the current JAR paths to `SuiConnProp.pro` then calls
  `Sui.reloadDriverJars()` to make them available immediately; refreshes the Status
  column in a background thread.

The Status column is probed in priority order: DriverManager registry → system
classloader (bundled/JDK) → application UCL (SuiCPProp.pro external JARs). When a
driver is found via the UCL but no explicit JAR path is stored, `ConnManager` scans
each `SUI.CLASSPATH.N` entry to identify the originating JAR and back-fills the path.

---

#### Tab 3: JDBC Properties

An editable two-column table (`Property Key` / `Value`) backed by `SuiConnPref.pro`.
Keys follow the format `url-prefix.property-name` and are matched by URL prefix at
connect time (existing behaviour of `SuiConnPref.pro`).

Buttons: **Add Row** / **Delete Row**.

---

#### Save / Cancel

- **Save** — commits the current form to `connData`, writes all
  `SUI.CONN.ALIAS.N` / `SUI.CONN.<alias>.*` keys to `SuiConnProp.pro`,
  writes `SUI.CONN.<class>.LOC` JAR paths, writes `SuiConnPref.pro`, and
  calls `Sui.reloadDriverJars()` so new JARs are immediately usable.
  The main panel URL combobox is refreshed after save.
- **Cancel** — discards all changes.

---

#### Legacy migration

On first open, `ConnManager` checks for two legacy data sources and offers to migrate them:

| Legacy source | Keys | Action |
|---|---|---|
| `connprop.pro` | `SUI.CONN.ALIAS.N`, `SUI.CONN.<alias>.*` | Loaded as-is; written to `SuiConnProp.pro` on Save |
| Old JDBC Resources | `SUI.JDBCURL.0.N` | URL-only entries; driver detected by prefix; alias auto-derived from URL path/segment; notified via dialog |

On Save the old `SUI.JDBCURL.0.N` / `SUI.DBDRIVER.N` keys are erased from
`SuiConnProp.pro` after the migrated data has been written in the new format.

---

#### Property storage (`SuiConnProp.pro`)

```
SUI.CONN.ALIAS.1=MyDB2
SUI.CONN.MyDB2.URL=jdbc:db2://myhost:50000/SAMPLE
SUI.CONN.MyDB2.DRIVER=com.ibm.db2.jcc.DB2Driver
SUI.CONN.MyDB2.CONNM=DB2 (IBM JCC)
SUI.CONN.MyDB2.USERID=db2admin
SUI.CONN.MyDB2.PW=null          ← "null" when Auto-login is off
SUI.CONN.MyDB2.AUTOLOGIN=N
SUI.CONN.MyDB2.SERVER=myhost
SUI.CONN.MyDB2.PORT=50000
SUI.CONN.MyDB2.DBNAME=SAMPLE
SUI.CONN.com.ibm.db2.jcc.DB2Driver.LOC=/opt/drivers/db2jcc4.jar
```

---

### Main Panel — Userid Pre-fill from Connection Profile

When the user selects a URL in the main panel URL combobox, Sui now attempts to
pre-fill the **Userid** field automatically.

**Logic (evaluated in order):**

1. If the session cache already holds a userid for this URL (`SUI.USERID.<url>`),
   that value is used (existing behaviour preserved).
2. Otherwise, if the Userid field is currently **blank**, the matching saved
   connection profile is looked up in `SuiConnProp.pro` by URL and its
   `SUI.CONN.<alias>.USERID` value is applied.
3. If the field already contains a value entered by the user it is left untouched.

**New helper in `Sui.java`:**

```java
public static String getConnUseridForUrl(String url) {
    for (int i = 1; ; i++) {
        String alias = GetConnProp("SUI.CONN.ALIAS." + i, null);
        if (alias == null || alias.isEmpty()) break;
        if (url.equals(GetConnProp("SUI.CONN." + alias + ".URL", "")))
            return GetConnProp("SUI.CONN." + alias + ".USERID", "");
    }
    return "";
}
```

---

### Main Panel — Password Pre-fill with AutoLogin Gate

Password pre-fill from a saved profile is gated behind the **AUTOLOGIN** flag so
that saved passwords are never silently injected unless the user has explicitly
opted in.

**Logic:**

- Fires only when the **Password** field is currently empty.
- Looks up the matching alias in `SuiConnProp.pro` by URL.
- Reads `SUI.CONN.<alias>.AUTOLOGIN`; skips the alias unless the value is `Y`.
- Reads `SUI.CONN.<alias>.PW`; skips if empty or the sentinel literal `"null"`.
- If all checks pass, the password is written to the Password field.

**New helper in `Sui.java`:**

```java
public static String getConnAutoPasswordForUrl(String url) {
    for (int i = 1; ; i++) {
        String alias = GetConnProp("SUI.CONN.ALIAS." + i, null);
        if (alias == null || alias.isEmpty()) break;
        if (url.equals(GetConnProp("SUI.CONN." + alias + ".URL", ""))) {
            if (!"Y".equals(GetConnProp("SUI.CONN." + alias + ".AUTOLOGIN", "N"))) break;
            String pw = GetConnProp("SUI.CONN." + alias + ".PW", "");
            return (pw.isEmpty() || "null".equals(pw)) ? "" : pw;
        }
    }
    return "";
}
```

Both helpers iterate `SuiConnProp.pro` entries at call time; no caching is involved
so changes to the profile file are reflected immediately.

---

### Preferences → Keywords Tab (new `PropmKeyw.java`)

A new **Keywords** tab has been added to the Preferences dialog (after the **C Path** tab).
It provides a graphical editor for the F1 auto-completion shorthand entries stored in
`SuiKeywProp.pro`.

#### Layout

- **3-column editable `JTable`**: Trigger | Expansion | Description
  - *Trigger*: the short keyword the user types before pressing F1 (e.g. `sel`)
  - *Expansion*: the full SQL text inserted (e.g. `SELECT * FROM `)
  - *Description*: optional tooltip shown in the completion popup
- **Toolbar buttons**: Add Row, Delete Row, Move Up, Move Down

#### Load behaviour (`load()`)

All `KEY.N` entries are read from the live `KeywProp` `Properties` object (which
already holds the merged bundled + user keywords at startup), parsed on the
comma separator, and displayed in the table.

#### Save behaviour (`apply()`)

When the user clicks **OK** or **Apply**:

1. All `KEY.*` keys are removed from `KeywProp`.
2. Table rows are re-numbered sequentially (blank-Trigger rows are skipped).
3. Each row is serialised as `trigger,expansion,description` and written back as
   `KEY.N`.
4. `Sui.StoreKeywProp()` is called to persist the changes to `SuiKeywProp.pro`
   in `SuiHome`.

#### Integration in `PropmAll.java`

- `PropmKeyw pk` field added.
- `pk = new PropmKeyw()` in constructor.
- `tp.add("Keywords", pk.getPanel())` inserts the tab after **C Path**.
- `pk.apply(); Sui.StoreKeywProp();` called in both **OK** and **Apply** handlers.

---

### F1 Auto-completion — Bundled Keyword Defaults (`keyw.pro`)

Prior to this release the F1 shorthand completion provider had no entries unless
the user had previously saved a `SuiKeywProp.pro` file. Pressing F1 with no saved
file silently did nothing.

A bundled resource file `keyw.pro` is now included in the JAR (`src/keyw.pro`).
It contains 30 default SQL keyword completions covering the most common patterns:

| Range | Examples |
|---|---|
| `KEY.1`–`KEY.6` | `sel` (SELECT \*), `selw` (SELECT \* WHERE), `insto` (INSERT INTO … VALUES), `upd` (UPDATE … SET), `del` (DELETE FROM … WHERE), `delf` (DELETE FROM) |
| `KEY.7`–`KEY.12` | `ct` (CREATE TABLE), `cv` (CREATE VIEW), `ji` (JOIN … ON), `lj` (LEFT JOIN), `rj` (RIGHT JOIN), `fj` (FULL OUTER JOIN) |
| `KEY.13`–`KEY.18` | `gb` (GROUP BY), `ob` (ORDER BY), `hav` (HAVING), `uw` (UNION), `uwa` (UNION ALL), `ex` (EXISTS subquery) |
| `KEY.19`–`KEY.24` | `cas` (CASE WHEN THEN ELSE END), `cte` (WITH cte AS (…) SELECT), `wf` (ROW\_NUMBER() OVER PARTITION BY), `ins` (INSERT INTO … SELECT FROM), `trunc` (TRUNCATE TABLE), `cr` (CREATE SCHEMA) |
| `KEY.25`–`KEY.30` | `cnt` (SELECT COUNT(\*) FROM), `dis` (SELECT DISTINCT), `betw` (BETWEEN … AND), `ins2` (IN (SELECT … FROM WHERE)), `lim` (SELECT … FROM LIMIT), `top` (SELECT TOP … FROM) |

---

### F1 Auto-completion — Keyword Merge at Load Time

`Sui.LoadProp()` now merges bundled defaults with the user-customised file so
that new defaults are available on first run and user edits are preserved on
subsequent runs.

**Merge algorithm:**

1. Load `keyw.pro` from the JAR resource — all 30 entries populate an ordered map
   keyed by *trigger*.
2. Load the user's file (first candidate found wins):
   - `SuiHome/SuiKeywProp.pro`
   - `SuiHome/keyw.pro`
   - `SuiHome/SuiKeywProp.pro.bak`
3. For each entry in the user file: if the trigger already exists in the map the
   user's expansion **replaces** it (user wins); new triggers are appended.
4. The merged map is re-numbered sequentially into `KeywProp` as `KEY.1`, `KEY.2`, …

**Effect:**

- First run (no user file): all 30 bundled defaults are active immediately.
- Subsequent runs: user edits override matching triggers; any bundled triggers the
  user has not edited remain available.
- Deleting a trigger in the Keywords tab removes it from the user file and it
  disappears from the merge (bundled triggers can be removed by the user this way).

---

### ConnDB — MariaDB Blank-port URL Sanitization

`ConnDB.java` now sanitizes the JDBC URL before passing it to
`DriverManager.getConnection()`.

**Problem:** The built-in MariaDB URL template is
`jdbc:mariadb://&server:&port/&dbname`. When the user leaves the `&port`
substitution variable blank the rendered URL becomes
`jdbc:mariadb://hostname:/dbname`, which the MariaDB driver rejects with an
`ArrayIndexOutOfBoundsException` when trying to parse the empty port token.

**Fix — `sanitizeUrl()`:**

```java
private static String sanitizeUrl(String url) {
    if (url == null) return url;
    // "://host:/" → "://host/"  (blank port from template &server:&port)
    return url.replaceFirst("(://[^/:]+):/", "$1/");
}
```

The regex matches `://hostname:/` (any host with an empty port segment) and
replaces it with `://hostname/`, which is a valid portless MariaDB URL and
connects on the default port (3306).

---
