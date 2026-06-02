# Connection Manager

The **Connection Manager** is the central place in Sui for creating and maintaining JDBC
connection profiles. Open it from the menu bar: **File → Connection Manager…**

---

## Overview

The dialog is divided into two areas:

- **Left panel** — the list of all saved connection profiles (aliases).
- **Right panel** — a three-tab editor for the selected profile and global settings.

Changes are held in memory until you click **Save**. Clicking **Cancel** discards all
changes.

---

## Left Panel — Connection List

Each entry in the list represents one saved connection profile, identified by a short
**alias** name of your choosing (e.g. `MyDB2Prod`, `LocalMariaDB`).

| Button | Action |
|---|---|
| **New** | Adds a blank profile at the bottom of the list. |
| **Copy** | Duplicates the selected profile. The copy gets the name `Copy_of_<alias>`. Auto-login is never copied — you must re-enable it deliberately. |
| **Remove** | Marks the selected profile for deletion. It is actually removed from `SuiConnProp.pro` when you click **Save**. |

Click any alias in the list to load it into the editor on the right.

---

## Tab 1 — Connection

This tab holds the per-connection details.

### Alias

A short, memorable name for the connection. This is the label that appears in the
URL combobox on the main Sui panel. Choose something descriptive, for example
`DB2-Production`, `BQ-Analytics`, `SQLite-LocalTest`.

> Alias names must be unique. If you type a name that already exists, the existing
> profile will be silently overwritten on Save.

### Driver

A dropdown of all known JDBC drivers, loaded from the bundled `driver.pro` resource.
Selecting a driver updates the visible form fields and the URL template used to
auto-build the JDBC URL.

Drivers that need an external JAR (e.g. DB2, Oracle, MariaDB) will show
**✘ Not loaded** in the Driver/JAR tab until you point the catalog to the JAR file.
Drivers that are available on the classpath (e.g. SQLite, H2) will show
**✔ On classpath** without any additional configuration.

### Server, Port, Database / Project, SID

These fields are shown or hidden automatically depending on the selected driver:

| Field | Shown for |
|---|---|
| **Server** | Networked databases — DB2, MariaDB, MySQL, PostgreSQL, Oracle, SQL Server, … |
| **Port** | Same drivers; also always shown for BigQuery (defaults to 443) |
| **Database** | Most drivers — the database or schema name to connect to |
| **Project** | BigQuery only — your Google Cloud project ID |
| **SID** | Oracle only — the Oracle System Identifier |

SQLite and other file/URL-only drivers hide all four fields and let you type the JDBC
URL directly instead.

### URL

The full JDBC connection string.

- When the selected driver has a URL template (most drivers), this field is
  **computed automatically** from the Server/Port/Database/SID values as you type.
  The field has a grey background to indicate it is read-only in this mode.
- When the driver has no template, the field is **white and directly editable** — type
  or paste the complete JDBC URL yourself (e.g. `jdbc:sqlite:/home/user/mydb.db`).

The auto-computed URL is the value that is saved and used when connecting. If you
need to add extra parameters (e.g. `?useSSL=false`), switch to a driver that has no
template and type the URL manually, or use the **JDBC Properties** tab for per-prefix
properties.

> **Tip for BigQuery:** The URL template fills in the port automatically. You only
> need to enter the Project ID in the Database/Project field.

### User and Password

The JDBC user ID and password for this connection.

- The password field is masked (`***`). Click **Show** to reveal it and **Hide** to
  mask it again.
- The password is stored in memory only until Save. Whether it is written to disk
  depends on the **Auto-login** checkbox (see below).

### Auto-login

| State | Behaviour |
|---|---|
| **Off** (default) | Password is **never** written to `SuiConnProp.pro`. The sentinel value `null` is stored in its place. You must type your password each session. |
| **On** | Password **is** written to `SuiConnProp.pro` in plain text on Save. When you select this URL in the main panel, the password is injected into the Password field automatically. |

> **Security note:** `SuiConnProp.pro` is a plain-text file stored in your Sui home
> directory. Only enable Auto-login on machines and accounts where that file is
> adequately protected. See [CredentialHandling.md](CredentialHandling.md) for details.

### Test Connection

Click **Test Connection** to immediately open a JDBC connection using the current
URL, User, and Password values. The result appears inline below the button:

- **Green** — connection succeeded; the database product name and version are shown
  (e.g. `Connected: DB2/LINUXX8664 11.5.9.0`).
- **Red** — connection failed; the full exception message is displayed so you can
  diagnose the issue (wrong password, driver not loaded, host unreachable, etc.).

The test runs in a background thread so the dialog stays responsive while connecting.

---

## Tab 2 — Driver / JAR

This tab manages the **global driver catalog** — the mapping from driver class names to
their JAR files. Changes here affect *all* connections that use the same driver class.

The table has four columns:

| Column | Description |
|---|---|
| **Name** | Human-readable display name (editable) |
| **Driver Class** | Fully qualified Java class name (editable) |
| **JAR / Path** | Path to the driver JAR file. Supports `*.jar` glob patterns to load all JARs in a folder (useful for multi-JAR drivers). |
| **Status** | ✔ Registered / ✔ On classpath / ✔ In JAR / ✘ Not loaded — colour-coded |

The status column is probed automatically at these levels (in order):

1. **✔ Registered** — the driver is already registered with `DriverManager` (was loaded
   in a previous connection this session).
2. **✔ On classpath** — the class is available in the system classloader (bundled in
   `Sui.jar` or part of the JDK, e.g. SQLite).
3. **✔ In JAR** — found in one of the external JARs listed in `SuiCPProp.pro`.
4. **✘ Not loaded** — the class was not found anywhere. You need to provide a JAR path.

### Buttons

| Button | Action |
|---|---|
| **Add** | Inserts a blank row for a custom driver not in the bundled list. |
| **Remove** | Deletes the selected row from the catalog. |
| **Browse JAR…** | Opens a file chooser pre-set to the directory of the currently entered path. Select the driver `.jar` file; the path is written into the JAR/Path column. |
| **Reload JARs** | Saves all current JAR paths to `SuiConnProp.pro` then reloads every driver from its JAR immediately — no restart needed. The Status column refreshes in the background. |

### Setting up a new driver JAR

1. Select the driver row (or click **Add** to create one).
2. Click **Browse JAR…** and navigate to the `.jar` file (e.g. `db2jcc4.jar`).
3. Click **Reload JARs** — the Status column should change to ✔.
4. Click **Save** to persist the JAR path.

For drivers that come as multiple JARs in one folder, enter the folder path with a
glob: `C:\drivers\oracle\*.jar`. The Reload and Save actions expand the glob.

---

## Tab 3 — JDBC Properties

A key/value table backed by `SuiConnPref.pro`. These properties are passed directly to
`DriverManager.getConnection()` when the JDBC URL matches the key prefix.

**Key format:** `url-prefix.property-name`

When Sui opens a connection, it scans every entry in this table and includes all entries
whose key prefix matches the beginning of the target JDBC URL. This means you can
define properties at two levels of specificity: **specific** (targeting one exact
connection URL) or **generic** (targeting all connections that share the same driver
prefix).

---

### Specific properties — one connection only

Prefix the key with the full JDBC URL of the target connection, then append a dot and
the property name. Only connections whose URL starts with that full string will pick up
the property.

**Example — set the default schema to `kjell` for one particular DB2 database:**

```
jdbc:db2://localhost:50000/sample.currentSchema = kjell
```

When Sui connects to `jdbc:db2://localhost:50000/sample`, the prefix
`jdbc:db2://localhost:50000/sample` matches exactly, so `currentSchema=kjell` is passed
to the driver. A different DB2 database — say `jdbc:db2://prodserver:50000/finance` —
does *not* match this prefix and therefore does not receive the property.

This is useful for settings that should only apply to one specific database instance,
such as a default schema, a particular isolation level, or a connection-level time zone.

---

### Generic properties — all connections for a driver

Prefix the key with only the `jdbc:<subprotocol>` part of the URL (no host, port, or
database). Every connection whose URL begins with that short prefix will receive the
property.

**Example — apply a timestamp format preference to all DB2 connections:**

```
jdbc:db2.timestampFormat = 1
```

When Sui connects to *any* `jdbc:db2://…` URL, the prefix `jdbc:db2` matches, so
`timestampFormat=1` is injected for every DB2 connection regardless of host or database.

Other generic examples:

```
jdbc:postgresql.sslmode        = require
jdbc:mariadb.connectTimeout    = 10000
```

---

### Precedence — most specific prefix wins

When Sui evaluates the table, it finds *all* entries whose prefix matches the target
URL, then applies only the **longest matching prefix** for each property name. A more
specific entry therefore always silently overrides a more generic one for the same
property, regardless of the order the rows appear in the table.

**Example:** both of the following match `jdbc:db2://localhost:50000/sample`:

```
jdbc:db2.currentSchema                       = PUBLIC
jdbc:db2://localhost:50000/sample.currentSchema = kjell
```

Sui sets `currentSchema=kjell` because the second prefix is longer. The generic row
still applies to all *other* DB2 connections that do not have a specific override.

---

Use JDBC Properties for driver-specific settings that cannot be embedded in the URL,
such as:
- Default schema or catalog (`currentSchema`, `searchPath`, …)
- SSL/TLS options (`sslmode`, `sslcert`, …)
- Connection timeouts
- Character set overrides
- BigQuery OAuth settings
- Timestamp and date format preferences

---

### Buttons

| Button | Action |
|---|---|
| **Add Row** | Inserts a blank row at the bottom of the table. |
| **Delete Row** | Removes the selected row. |

---

## Save and Cancel

**Save** performs the following in order:
1. Commits any in-progress cell edits in all three tabs.
2. Writes all `SUI.CONN.ALIAS.N` and `SUI.CONN.<alias>.*` keys to `SuiConnProp.pro`.
3. Writes driver JAR paths (`SUI.CONN.<class>.LOC`) and any custom driver entries
   (`SUI.CONN.CUSTDRV.N`) to `SuiConnProp.pro`.
4. Writes the JDBC Properties table to `SuiConnPref.pro`.
5. Calls `Sui.reloadDriverJars()` so newly configured JARs take effect immediately.
6. Refreshes the URL combobox and driver list in the main Sui panel.

**Cancel** closes the dialog without writing anything to disk.

---

## Migrating from Earlier Versions

If you have connection data from an older version of Sui, the Connection Manager
migrates it automatically on first open:

### Legacy `connprop.pro`

If `SuiConnProp.pro` has no entries but the old `connprop.pro` file is present, all
profiles are loaded from it and a message like:

> *3 connection(s) loaded from legacy connprop.pro. Click Save to migrate them.*

…is shown. Click **Save** to write them to `SuiConnProp.pro` in the new format.

### Old JDBC Resources list (`SUI.JDBCURL.0.N`)

URLs previously managed via the **Manage All JARs…** dialog are also imported. For
each URL:
- The driver is detected by matching the URL prefix against the built-in template
  list.
- A short alias is derived from the URL (e.g. the database name segment).
- The profile appears in the list without credentials — you will be prompted to review
  it.

A message like:

> *2 URL(s) loaded from the legacy JDBC Resources list. Set the alias and user
> credentials, then click Save.*

…is shown. Fill in any missing details and click **Save**.

After saving, the old `SUI.JDBCURL.0.N` keys are erased from `SuiConnProp.pro`.

---

## Workflow — First-time Setup

1. Open **File → Connection Manager…**.
2. Click **New**.
3. Type an **Alias** (e.g. `MyDatabase`).
4. Select your **Driver** from the dropdown.
5. Fill in **Server**, **Port**, and **Database** (or **Project** for BigQuery).
   Watch the **URL** field update automatically.
6. Enter your **User** name.
7. Switch to the **Driver / JAR** tab. If the Status shows **✘ Not loaded**,
   click **Browse JAR…**, select the JAR, then click **Reload JARs**.
8. Switch back to **Connection** and click **Test Connection** to verify.
9. If the test is green, click **Save**.

Your new alias now appears in the URL combobox on the main Sui panel.

---

## Storage

Connection profiles are stored in `SuiConnProp.pro` in the Sui home directory.
JDBC connection properties are stored in `SuiConnPref.pro` in the same location.

See [SuiHome.md](SuiHome.md) for the location of the Sui home directory on your system.

---

## Tips

- **Multiple environments:** Create separate profiles for development, test, and
  production with the same driver but different server/database names and aliases
  (e.g. `MyApp-Dev`, `MyApp-Test`, `MyApp-Prod`). Switch between them instantly from
  the main panel URL combobox.

- **Shared driver JARs:** All profiles using the same driver class share one JAR path
  entry. Update the path once in the Driver/JAR tab and it applies to every profile.

- **Glob patterns for multi-JAR drivers:** Some drivers (e.g. Oracle with `ojdbc11.jar`
  + `orai18n.jar`) require multiple JARs. Enter `C:\drivers\oracle\*.jar` in the
  JAR/Path column to load all of them at once.

- **No restart needed:** After adding a new driver JAR and clicking **Reload JARs**
  (or **Save**), the driver is available immediately. You do not need to restart Sui.

- **Passwords and Auto-login:** If you want Sui to pre-fill the password on the main
  panel when you select a URL, tick **Auto-login** in the connection profile. Without
  it, the password field is always blank on startup and you type it manually each
  session — which is the safer default for shared or portable installations.
