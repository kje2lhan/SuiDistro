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

## DB2 — Common JDBC Properties

The IBM DB2 JDBC driver (`com.ibm.db2.jcc.DB2Driver`) accepts a long list of
connection properties that influence statement preparation, error reporting,
timestamp behaviour, and metadata semantics. The most useful ones for everyday
Sui use are listed below. All of them are set the same way: add a row in the
**JDBC Properties** tab with key `jdbc:db2.<propertyName>` (generic — applies to
every DB2 connection) or `jdbc:db2://host:port/db.<propertyName>` (specific —
applies to one URL only).

### Property reference

| Property | Typical value | Effect |
|---|---|---|
| `clientProgramName` | `Sui` or `Sui-<user>` | Free-form string (max 255 bytes) that DB2 records in `SYSIBMADM.MON_CURRENT_SQL` / `WLM_GET_WORKLOAD_OCCURRENCES` and shows in monitoring tools such as Data Server Manager. Lets a DBA see *which* tool is running a query, not just the OS user. |
| `deferPrepare` | `true` (default) / `false` | When `true`, `PreparedStatement.prepareStatement()` does **not** send a PREPARE to the server immediately; the PREPARE is folded into the first EXECUTE for one less network round-trip. Set to `false` when you want the PREPARE error reported at prepare time (e.g. when running ad-hoc SQL through Sui and you want syntax errors flagged before the row fetch starts). |
| `retrieveMessagesFromServerOnGetMessage` | `true` (recommended) / `false` (default) | Controls whether `SQLException.getMessage()` returns the full DB2 server-side message text (including substitution tokens and SQLCODE description) or just the short token form. **Strongly recommended to set to `true`** — without it, Sui will display cryptic messages like `DB2 SQL Error: SQLCODE=-204, SQLSTATE=42704, SQLERRMC=KJELL.NOSUCHTABLE` instead of the human-readable explanation. |
| `timestampFormat` | `0` (default) / `1` | When `1`, `ResultSet.getString()` on a TIMESTAMP column returns the JDBC-spec form `yyyy-mm-dd hh:mm:ss[.fffffffff]` instead of the DB2 native form `yyyy-mm-dd-hh.mm.ss.ffffff`. Set to `1` if you copy/paste timestamps from the result grid into other tools that expect the standard format. |
| `timestampPrecisionReporting` | `0` (default) / `1` | When `1`, `ResultSetMetaData.getPrecision()` and `getColumnDisplaySize()` report **26** for a TIMESTAMP(6) column (matching the textual width including punctuation) instead of the raw fractional-seconds precision (`6`). Affects how Sui sizes the TIMESTAMP columns in the result grid. |
| `useJDBC4ColumnNameAndLabelSemantics` | `1` (default) / `2` | Controls what `ResultSetMetaData.getColumnName()` and `getColumnLabel()` return. Value `1` follows the JDBC 4.0 spec: `getColumnName()` returns the underlying *column name* and `getColumnLabel()` returns the **AS** alias. Value `2` reverts to the older DB2 behaviour where both methods return the AS alias. Set to `2` if you have legacy reports that broke after upgrading the driver. |

### Examples

Generic — apply to every DB2 connection:

```
jdbc:db2.clientProgramName                      = Sui
jdbc:db2.deferPrepare                           = false
jdbc:db2.retrieveMessagesFromServerOnGetMessage = true
jdbc:db2.timestampFormat                        = 1
jdbc:db2.timestampPrecisionReporting            = 1
jdbc:db2.useJDBC4ColumnNameAndLabelSemantics    = 1
```

Specific — only the production database gets the marker name:

```
jdbc:db2://prod.example.com:50000/PAYROLL.clientProgramName = Sui-Prod
```

> **Tip:** `retrieveMessagesFromServerOnGetMessage=true` is the single most useful
> setting — it transforms otherwise opaque DB2 error messages into readable text
> in Sui's status bar and exception popups. Add it once as a generic
> `jdbc:db2.` row and forget about it.

---

## DB2 — SSL / TLS Setup

DB2 supports SSL/TLS for the JDBC client–server connection. Sui drives this
through the same **JDBC Properties** table — no Java command-line flags are
required.

### Step 1 — Server listens on an SSL port

The DBA enables SSL on the DB2 server and exposes a dedicated SSL port (commonly
**50001**, distinct from the cleartext port **50000**). Verify the port with the
DBA before continuing.

### Step 2 — Add the SSL JDBC properties

Add the following rows to the **JDBC Properties** tab. The minimum set for a
trusted-CA setup is just two properties:

```
jdbc:db2.sslConnection      = true
jdbc:db2.sslTrustStoreType  = Windows-ROOT
```

| Property | Value | Effect |
|---|---|---|
| `sslConnection` | `true` | Tells the JCC driver to negotiate TLS on the socket. Without this the driver opens a cleartext connection regardless of which port you point it at. |
| `sslTrustStoreType` | `Windows-ROOT` | Uses the **Windows certificate store** (the same trust list as Edge / IE / Chrome) as the JDBC trust store. The Java runtime then trusts every CA root the OS trusts — no manual `keytool` import needed when your DBA's server certificate chains up to a public or enterprise CA already installed in Windows. |
| `sslTrustStoreLocation` | path to `.jks` / `.p12` | *Optional.* Use **only** if you do **not** use `Windows-ROOT` and want a private Java keystore instead. |
| `sslTrustStorePassword` | keystore password | *Optional.* Required only with `sslTrustStoreLocation`. The `Windows-ROOT` store is read-only and needs no password. |
| `sslVersion` | `TLSv1.2` / `TLSv1.3` | *Optional.* Force a specific TLS version. The driver negotiates the highest mutually supported version by default, so this is rarely needed. |

### Step 3 — Point the URL at the SSL port

Update the connection's **URL** (or the Server / Port fields, which auto-build the
URL) so the port matches the SSL listener — e.g.:

```
jdbc:db2://prod.example.com:50001/PAYROLL
```

### Step 4 — Test

Click **Test Connection** on the Connection tab. A green response confirms the
TLS handshake completed and the credentials were accepted.

### Why `Windows-ROOT`?

`sslTrustStoreType=Windows-ROOT` is the path of least resistance on a Windows
workstation:

- **No keystore file to manage.** You don't have to copy `.cer` files around,
  run `keytool -import`, or remember a keystore password.
- **Picks up enterprise CA pushes automatically.** When your IT department
  installs a new internal CA via Group Policy, JDBC trusts it immediately
  without any change to Sui or to a local keystore.
- **Survives Java upgrades.** The trust list is the OS's, not the JRE's
  `cacerts`, so reinstalling or upgrading Java does not invalidate the trust.

If you are on Linux/macOS or need to trust a private CA that is not in the OS
store, fall back to `sslTrustStoreLocation` + `sslTrustStorePassword` pointing
at a `.jks` or `.p12` file you build with `keytool`.

### Full DB2 SSL example

A typical production-ready DB2 SSL profile with all of the above looks like
this in the JDBC Properties tab:

```
jdbc:db2.sslConnection                          = true
jdbc:db2.sslTrustStoreType                      = Windows-ROOT
jdbc:db2.clientProgramName                      = Sui
jdbc:db2.retrieveMessagesFromServerOnGetMessage = true
jdbc:db2.timestampFormat                        = 1
```

…combined with a URL of `jdbc:db2://prod.example.com:50001/PAYROLL` on the
Connection tab.

---

## BigQuery — Common JDBC Properties

The Google / Simba BigQuery JDBC driver (`com.simba.googlebigquery.jdbc.Driver`)
accepts a long list of connection properties. The handful that matter most for
day-to-day Sui use are listed below.

All of them are set the same way as DB2: add a row in the **JDBC Properties** tab
with key `jdbc:big.<propertyName>` (generic — applies to every BigQuery
connection) or `jdbc:bigquery://…fullUrl.<propertyName>` (specific — applies to
one connection only).

> **Why `jdbc:big` and not `jdbc:bigquery`?** Sui matches each property key by
> the longest prefix that the target URL **starts with**. Since every BigQuery
> URL begins with `jdbc:bigquery://…`, the short prefix `jdbc:big` matches them
> all. Either spelling works; `jdbc:big` is just shorter to type.

### Property reference

| Property | Typical value | Effect |
|---|---|---|
| `OAuthType` | `1` (**recommended**) / `0` / `2` / `3` | Selects the Google authentication flow. `0` = service-account P12 key file, `1` = **user account via browser** (interactive OAuth — driver pops up your default browser, you sign in to Google, and the resulting refresh token is cached), `2` = pre-generated refresh token (headless), `3` = Google Application Default Credentials (uses `gcloud auth application-default login`). For a desktop tool like Sui, **`OAuthType=1` is the strong recommendation**: no JSON or P12 key file to manage, no `gcloud` install required, and it works with both personal and corporate Google accounts. |
| `EnableSession` | `0` (default) / `1` | When `1`, the driver opens a BigQuery **session** for the connection. This is what lets you run `CREATE TEMP TABLE …`, `DECLARE` variables, multi-statement scripts, and other session-scoped SQL that BigQuery otherwise rejects. Recommended `1` for interactive query work in Sui; leave `0` only if you need strictly stateless one-shot queries. |
| `Location` | `US` / `EU` / `europe-west1` / `asia-northeast1` / … | The geographic location BigQuery should run the queries in. When omitted, the driver defaults to `US`. **Must** be set explicitly if your datasets live anywhere else — otherwise BigQuery returns *"Dataset … was not found in location US"* even though the dataset exists. Use the same string that appears in the BigQuery console for the dataset (`EU` for the multi-region, or the specific region name like `europe-north1`). |

### Examples

Generic — apply to every BigQuery connection:

```
jdbc:big.OAuthType     = 1
jdbc:big.EnableSession = 1
jdbc:big.Location      = EU
```

Specific — only the analytics project uses an EU location, everything else
inherits the default:

```
jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=my-analytics.Location = europe-west1
```

### First connect with `OAuthType=1`

1. Set `jdbc:big.OAuthType = 1` (and `EnableSession = 1`, `Location` if needed)
   in the **JDBC Properties** tab.
2. On the **Connection** tab, leave **User** and **Password** empty — they are
   not used in this flow.
3. Click **Test Connection** (or just connect normally from the main panel).
4. The driver opens your default browser to a Google sign-in page. Choose the
   account that has access to the project and approve the requested scopes.
5. The browser shows *"You may close this window"*. The driver caches a refresh
   token locally so subsequent connects do **not** open the browser again.
6. The connection completes and Sui shows the green *Connected: Google
   BigQuery …* response.

> **Tip:** If you switch Google accounts later (or revoke the cached token in
> your Google account settings), the next connect will pop the browser again to
> let you re-authorise. No configuration change is needed inside Sui.

---

## SQL Server — Common JDBC Properties

The Microsoft JDBC Driver for SQL Server (`com.microsoft.sqlserver.jdbc.SQLServerDriver`)
accepts a wide range of connection properties for authentication, encryption, and performance.
The most useful ones for Sui are listed below.

All of them are set the same way as DB2 and BigQuery: add a row in the **JDBC Properties**
tab with key `jdbc:sqlserver:<propertyName>` (generic — applies to every SQL Server connection)
or `jdbc:sqlserver://host:port;databaseName=db.<propertyName>` (specific — for one connection only).

### JDBC URL Format

```
jdbc:sqlserver://[serverName[\instanceName][:portNumber]][;property=value[;property=value]]
```

**Examples:**

```
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb
jdbc:sqlserver://localhost:1433;databaseName=mydb;integratedSecurity=true
jdbc:sqlserver://myserver\SQLEXPRESS:1433;databaseName=mydb
```

### Property reference

| Property | Typical value | Effect |
|---|---|---|
| **Authentication** | | |
| `authentication` | `ActiveDirectoryIntegrated` / `ActiveDirectoryInteractive` / `ActiveDirectoryServicePrincipal` / `ActiveDirectoryManagedIdentity` / `SqlPassword` | Authentication mode (version 6.0+). `ActiveDirectoryIntegrated` = Microsoft Entra (Azure AD) with integrated Windows auth; `ActiveDirectoryInteractive` = browser-based interactive sign-in; `ActiveDirectoryServicePrincipal` = service principal (client ID in `user`, secret in `password`); `SqlPassword` = SQL login. Default is `NotSpecified` (plain SQL auth). **Note:** `ActiveDirectoryPassword` still works but is **deprecated**. Any non-`NotSpecified` value enables TLS by default. |
| `integratedSecurity` | `true` / `false` | When `true`, authenticates using **Windows credentials** instead of a SQL user/password — you leave `user` and `password` empty and SQL Server signs you in as your current Windows account. This is purely an **authentication** mechanism (it has **no** effect on TLS / certificate trust — see the note below). With `authenticationScheme=NativeAuthentication` (default) the driver loads the native DLL `mssql-jdbc_auth-<version>-<arch>.dll` (Windows only, must be on `java.library.path`); with `authenticationScheme=JavaKerberos` no DLL is needed (pure-Java Kerberos, works cross-platform). Omit for SQL authentication. |
| `authenticationScheme` | `NativeAuthentication` / `JavaKerberos` / `NTLM` | How integrated security is performed. `NativeAuthentication` (default) uses the Windows-only native DLL. `JavaKerberos` uses pure-Java Kerberos (requires a `krb5.conf` and a fully-qualified `serverName`). `NTLM` (version 7.4+) uses NTLM with the `domain`, `user`, and `password` properties. Only relevant when `integratedSecurity=true`. |
| `user` | username | SQL Server login username (for SQL authentication) or Azure AD UPN (for Azure AD modes). |
| `password` | password | SQL Server login password (for SQL authentication) or Azure AD password. |
| **Encryption & Security** | | |
| `encrypt` | `true` / `false` / `strict` | Enables TLS/SSL encryption. `true` = encrypt (driver verifies cert if server has one); `strict` = encrypt and always verify certificate (fail if invalid). **Recommended: `strict` for production.** |
| `trustServerCertificate` | `true` / `false` | If `false` (default), the driver validates the server's SSL certificate against the Java trust store. If `true`, all certificates are accepted — **only for development environments**. Not recommended for production. |
| `hostNameInCertificate` | hostname pattern | Expected hostname in the server's SSL certificate (e.g. `*.database.windows.net`). Verifies that the certificate matches the actual server you are connecting to. |
| `trustStore` | file path | Path to a Java keystore (`.jks` or `.p12`) containing trusted CA certificates. If omitted, the JRE's built-in `cacerts` is used. |
| `trustStorePassword` | keystore password | Password for the trust store (if `trustStore` is used). |
| `trustStoreType` | `JKS` / `PKCS12` | Type of the trust store. Default: `JKS`. Use `PKCS12` for FIPS environments. |
| `clientCertificate` | file path | Path to the client certificate file for client certificate authentication. Supports PFX, PEM, DER, and CER formats. |
| `clientKey` | file path | Path to the private key file for PEM, DER, and CER client certificates. |
| `clientKeyPassword` | password | Password to access the `clientKey` file's private key. |
| **Connection Timeouts** | | |
| `loginTimeout` | seconds (0-65535) | Connection login timeout. Default: 30 (version 11.2+) or 15 (10.2 and earlier). 0 = use the system default. |
| `socketTimeout` | milliseconds | Socket read timeout. Default: 0 (infinite). |
| **Performance & Buffering** | | |
| `responseBuffering` | `adaptive` / `full` | How the driver buffers result rows: `adaptive` (default) = buffer the minimum needed; `full` = read the entire result set into memory when the statement executes. |
| `selectMethod` | `direct` / `cursor` | `direct` (default) = keep all result rows in client memory (fastest for processing all rows). `cursor` = create a server cursor keeping only a limited number of rows in client memory — use for very large result sets that don't fit in client memory. |
| `disableStatementPooling` | `true` / `false` | Whether prepared-statement pooling is disabled. Default: `true` (pooling off). Set to `false` together with a non-zero `statementPoolingCacheSize` to enable pooling. |
| `statementPoolingCacheSize` | int | Size of the prepared-statement handle cache (version 6.4+). Default: 0 (pooling disabled). Set > 0 and `disableStatementPooling=false` to enable. |
| `useBulkCopyForBatchInsert` | `true` / `false` | When `true`, uses SQL Server **bulk copy API** for fully-parameterized batch inserts — significantly faster for large inserts (version 9.2+). Default: `false`. |
| **Other** | | |
| `databaseName` | database name | Name of the database to connect to. Required. |
| `instanceName` | instance name | SQL Server named instance (for on-premises, e.g. `SQLEXPRESS`). |
| `portNumber` | port (1-65535) | Port number, default 1433. |
| `applicationName` | string (<=128 char) | Application name visible in SQL Profiler and SQL Server Management Studio activity logs. Default: `Microsoft JDBC Driver for SQL Server`. Set to `Sui` for easier tracking. |
| `sendTimeAsDatetime` | `true` / `false` | When `true` (default), `java.sql.Time` values are sent to the server as SQL Server `datetime`; when `false`, they are sent as SQL Server `time`. |
| `queryTimeout` | seconds | Query execution timeout. Default: -1 (infinite). |
| `lockTimeout` | milliseconds | Lock timeout. Default: -1 (wait indefinitely); 0 = no wait. |
| `sslProtocol` | `TLS` / `TLSv1.2` / `TLSv1.1` / `TLSv1` | TLS protocol to use for the secure connection (version 6.4+). Default: `TLS` (negotiates the highest available). |

### Examples

Generic — apply to every SQL Server connection:

```
jdbc:sqlserver.encrypt                   = strict
jdbc:sqlserver.trustServerCertificate    = false
jdbc:sqlserver.applicationName           = Sui
jdbc:sqlserver.disableStatementPooling   = false
jdbc:sqlserver.statementPoolingCacheSize = 250
```

Specific — properties for one Azure SQL Server connection:

```
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb.authentication = ActiveDirectoryPassword
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb.encrypt       = strict
```

### SQL Server SSL / TLS Setup

> **Authentication vs. encryption — a common confusion.** `integratedSecurity`
> (Windows / Kerberos login) and TLS certificate trust are **independent**.
> Turning on integrated security does **not** make the driver trust the Windows
> certificate store, and unlike DB2 there is **no** `Windows-ROOT` option for the
> SQL Server driver. TLS certificate validation always goes through the **Java**
> trust store, following this search order:
>
> 1. the file named by the `trustStore` property (or the JVM system property
>    `javax.net.ssl.trustStore`), then
> 2. `<java-home>/lib/security/jssecacerts`, then
> 3. `<java-home>/lib/security/cacerts` (the JRE's bundled CA list).
>
> So a public-CA certificate (e.g. Azure SQL's) is trusted out of the box because
> its root is already in `cacerts`. A **private / enterprise CA** is *not* in
> `cacerts` — you must either import it with `keytool` and point `trustStore` at
> that file, or (on Windows) bridge the OS store into Java with a custom
> `trustManagerClass`. Importing the one server certificate is by far the simpler
> route.

For on-premises SQL Server with SSL enabled:

1. **Enable encryption in the URL or JDBC Properties:**

```
jdbc:sqlserver.encrypt = strict
```

2. **Point to the SSL port** (typically **1433** for cleartext, **custom port** for SSL):

```
jdbc:sqlserver://prodserver:1433;databaseName=mydb
```

3. **Trust the certificate** — Use a Java keystore with imported certificates:

   ```
   jdbc:sqlserver.trustStore         = C:\path\to\truststore.jks
   jdbc:sqlserver.trustStorePassword = keystorepassword
   ```

   > **Note:** The SQL Server JDBC driver uses `trustStore` (not `trustStoreLocation` — that is the DB2/JCC naming).
   > SQL Server does not have a built-in `Windows-ROOT` option like DB2. If you need to trust
   > an enterprise CA on Windows, import its certificate into a Java keystore using `keytool`, then
   > point `trustStore` at that file. Alternatively, set JVM system properties outside of Sui:
   > `-Djavax.net.ssl.trustStore=<path> -Djavax.net.ssl.trustStorePassword=<password>`

4. **Verify hostname** (optional but recommended):

```
jdbc:sqlserver.hostNameInCertificate = *.yourdomain.com
```

### Full SQL Server SSL example with Azure AD

A production-ready Azure SQL profile with encryption and Microsoft Entra (Azure AD) authentication:

```
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb.authentication           = ActiveDirectoryPassword
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb.encrypt                 = strict
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb.hostNameInCertificate   = *.database.windows.net
jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb.applicationName         = Sui
```

Combined with a URL of `jdbc:sqlserver://myserver.database.windows.net:1433;databaseName=mydb` and user credentials on the **Connection** tab.

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
