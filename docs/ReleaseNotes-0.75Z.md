# Release Notes — Sui 0.75Z

**Branch:** `Sui075Z`  
**Base:** `Sui 0.75Y` (CSV compare, test report, query stats, export tracking)  
**Date:** 2026-10-17  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Mainframe | New feature | **Mainframe integration via Zowe / z/OSMF.** New *File* menu entries: *Zowe Connection Manager…*, *Open Mainframe Dataset…*, *Save Query to Mainframe…* and *Mainframe Explorer…*. Read and write sequential datasets and PDS members without a 3270 terminal. Requires Java 11+ and the optional `Zui.jar` integration library (see [Requirements](#requirements-and-gating)) |
| Mainframe | New feature | **Mainframe Explorer** — an ISPF 3.4-style dataset list. Enter a dsname level (`KJE2.**`, `KJE2.*.CNTL`, …), drill into PDS/PDSE member lists, and **Browse** (read-only result grid) or **Edit** (load into the query editor) any dataset or member. Recently used levels are remembered per alias. See [MainframeExplorer.md](MainframeExplorer.md) |
| Mainframe | New feature | **Save Query to Mainframe** writes the editor content (or only the selection) to an existing dataset/member. The SQL is formatted with the *Ext Format SQL* settings and wrapped to **72 columns**. Only existing targets can be written, and every overwrite must be confirmed |
| Query Result window | New feature | **Save result to mainframe.** When the integration is available, a new toolbar button writes the result (or the selected rows/columns) to a mainframe dataset as CSV. It uses the configured delimiter and quote characters and writes a header row, the same as *Export CSV* |
| Mainframe | New feature | **TLS certificate handling for Zowe connections.** Each alias selects a certificate source: `WINDOWS-ROOT` (Windows certificate store; default on Windows), `JAVA` (default truststore) or `CUSTOM` (a `.jks` / `.p12` file). A *Validate TLS certificate* toggle accepts self-signed certificates for dev/test |
| Connection Manager | New feature | **Credential groups.** A new optional *Group* field links aliases that share a userid/password. After a successful connect to one alias in a group, its credentials are filled in automatically when switching to another alias in the same group that has not yet been connected this session |
| Connection Manager | Enhancement | **Apply button** saves all changes without closing the dialog. **Remove** is renamed **Delete** and now removes the connection from `SuiConnProp.pro` immediately, after a confirmation warning that it cannot be undone |
| Drivers | New feature | **Google BigQuery JDBC driver (`BigQuery-Google`).** Google's open-source driver (`com.google.cloud.bigquery.jdbc.BigQueryDriver`) is bundled in the default build. Pick *BigQuery-Google* in the Driver dropdown; no external JAR is needed. The Simba *BigQuery* driver is still supported |
| Build | Enhancement | **Four Maven build profiles:** `full` (default: BigQuery + Db2), `nobq`, `nodb2` and `minimal`. Each produces `Sui075-<version>-<variant>-jar-with-dependencies.jar`. Drivers left out can still be added later through the *Driver / JAR* tab. The Db2 JCC driver (`com.ibm.db2:jcc`) is now bundled in the `full` build |
| Build / Security | Enhancement | Pinned transitive dependencies of the BigQuery driver to patched versions: `jackson-*` **2.22.3** and `httpclient5` **5.6.3**. The unused `fdb-java` dependency was removed |
| Dialect converter | Enhancement | **DB2 → BigQuery converter, many more conversions.** Added `OFFSET … FETCH`, `TO_CHAR` / `TO_DATE` / `TO_TIMESTAMP` / `TO_NUMBER`, `SUBSTRING … FROM … FOR`, `REGEXP_*`, `POSITION`, `DAYNAME` / `MONTHNAME`, `BIT*` functions, `DEC`, and more. Set operators now always get the explicit `DISTINCT`/`ALL` that BigQuery requires. The CTE column-list rewrite no longer depends on a SQL parser |
| Ext Format SQL | New feature | **Max output line length** (`SUI.FMT2.MAXLINELEN`, 0 = off) wraps formatted lines that exceed the limit. Lines break after a comma, before `AND`/`OR`/`WHEN`/`THEN`/`ELSE`/`END`, or after an operator. If no such point exists, the line is cut at the limit, but never inside a string literal. The former *Max line length* field is relabelled *Max inline expr. length*, which matches what it actually controls |
| Result Set Compare | Enhancement | **CSV Compare matches numbers by value.** `1.50`, `1.5` and `001.5` are treated as equal, both in key matching and in cell comparison |
| Query Result window | Enhancement | **Ctrl+click multi-selection.** The result grid now allows non-contiguous selection. *Transpose selected rows* works directly on the Ctrl+clicked rows, and the old *Mark row for compare* step is removed |
| Query editor | Enhancement | **Panel toggles in the right-click menu.** Single *Show / Hide* toggles for the SQL Object Tree, Query Tree, Query Sheet Overview, Query Toolbar and Query Tabs. Panels that share a dock slot hide each other automatically |
| Main window | New feature | **Help button on the toolbar.** A new *(i)* button at the right end of the main toolbar opens a menu with links to every user help page: Query Sheets & Tabs, Inline Directives, Additional Edit Functions, Query Result Window, Result Set Compare, Connection Manager, Credential Handling, Mainframe Explorer, Sui Home Directory, Profile Recovery and the Changelog |
| Startup | Bug fix | **The main window always appears.** The UI is now built on the Swing event thread, which fixes a main window that intermittently never appeared. Auto-login now connects on a background thread after the window is shown, so a slow or unreachable database no longer blocks startup. A failure during startup is reported in a dialog instead of leaving an invisible process running |
| Startup | Enhancement | **Startup timing log.** `[startup] …` checkpoint lines in the System Log show per-phase and cumulative times (property merge, JAR loading, driver registration, auto-connect). Set `SUI.LOGSTARTUPTIMING=N` to turn them off |
| Query editor | Bug fix | **Undo/Redo fixed.** Syntax-highlight colour changes no longer land on the undo stack, so Ctrl+Z undoes your text instead of "doing nothing". Undo history is also cleared when the editor content is replaced (tab switch, file load), so undo can no longer jump into another sheet's text |
| Query editor | Bug fix | **Line-number gutter.** Line numbers are no longer clipped when the query font is larger than the default or under fractional display scaling, and they are right-aligned. Toggling line numbers on and off no longer accumulates listeners |
| Connection Manager | Bug fix | The *Group* field no longer keeps showing the previously viewed connection's group for a connection that has none |
| Db2 | Bug fix | `DB2SQLCA` (extended Db2 error messages) now uses reflection only, so Sui compiles and runs without the Db2 JCC driver (`nodb2` / `minimal` builds) |
| Version | Bump | `0.75X` → `0.75Z` (`Ver` string, About dialog, `pom.xml`). The *Sui version* cell stamped into Excel exports, stale at `0.75N`, is now `0.75Z` |

---

## Details

### Mainframe integration (`ZoweConnManager`, `ZoweOpenDataset`, `ZoweSaveDataset`, `ZoweDatasetList`, `ZoweService`)

Sui has **no compile-time dependency** on the mainframe library. Every call goes
through reflection in `ZoweService`, using Sui's extended class loader
(`Sui.ucl`). The integration JAR is listed in `SuiCPProp.pro`:

```
SUI.CLASSPATH.1=file:///C:/path/to/Zui.jar
```

**Zowe Connection Manager** follows the layout of the JDBC Connection Manager: an
alias list on the left and an edit form on the right. Profiles are stored in
`zoweconfig.pro`:

| Key | Purpose |
|---|---|
| `SUI.ZOWE.ALIAS.N` | Alias (1-based) |
| `SUI.ZOWE.<alias>.SERVER` / `.PORT` | z/OSMF host and port (default 443, validated 1–65535) |
| `SUI.ZOWE.<alias>.CODEPAGE` | Mainframe code page, e.g. `IBM-1047` |
| `SUI.ZOWE.<alias>.USER` | Default user id |
| `SUI.ZOWE.<alias>.REJECTUNAUTHORIZED` | TLS validation (default `true`) |
| `SUI.ZOWE.<alias>.CERTSOURCE` | `WINDOWS-ROOT` \| `JAVA` \| `CUSTOM` |
| `SUI.ZOWE.<alias>.CUSTOMTRUSTSTORE` | Truststore path, used when `CERTSOURCE=CUSTOM` |

Passwords are kept **in memory only** (`<alias>.pw` in `TmpProp2`), the same
way database passwords are. Open, Save and the Explorer share one per-alias
dataset history (`<alias>.DSHIST.<n>`), so a dataset loaded with *Edit* already
appears in the *Save Query to Mainframe* dropdown.

Dataset names are checked before any request: `MY.SEQ.DATA` or
`MY.PDS.LIB(MEMBER)`. Dsname levels may contain only letters, digits, dots and
`*`, and must contain at least one dot. z/OSMF and network errors, including the
HTTP status and response body, appear in red in the status line and in a dialog.

### Requirements and gating (`Sui.java`)

The four mainframe menu items are added only when **both** conditions hold at
startup:

1. The JRE is **Java 11 or later** (`Sui.isJava11OrLater()`, which parses
   `java.specification.version`). The detected version is written to the
   System Log.
2. The integration class `com.sui.mainframe.connection.ZosConnectionConfig`
   can be loaded (`Sui.isZoweAvailable()`).

If either check fails, all mainframe items are hidden. The menu shows no entries
that would only open a warning when clicked. *Open*, *Save* and *Explorer*
also show a hint pointing to the Zowe Connection Manager until at least one
alias is configured.

### Credential groups (`ConnManager.java`, `Sui.java`)

The new `SUI.CONN.<alias>.GROUP` property is an editable combo box listing the
existing group labels. After every successful connect, the credentials are
recorded in memory as `SUI.GROUPUID.<group>` and `SUI.GROUPPW.<group>`. When
the user switches URL, the group credentials are applied only if the target URL
has **not** been connected earlier in the session. A URL's own session history
always wins. The rule runs before the Connection Manager profile lookup, so it
also applies when `SUI.SETPWBLANK=Y` is set or the target has no stored password.
See [CredentialHandling.md](CredentialHandling.md#credential-groups).

### Startup rework (`Sui.java`)

- `main()` now creates `Sui` inside `SwingUtilities.invokeLater`. If
  construction throws, an error dialog is shown and the process exits.
- `Startit()` no longer calls `ConnDB()` synchronously for auto-login. It sets
  `autoConnectPending` instead. At the end of the constructor, `connectAsync()`
  runs the JDBC connect on a daemon `Sui-Connect` thread, and the UI bookkeeping
  (`finishConnect()`) runs back on the event thread. While connecting, the
  window title reads *Connecting…* and the status label shows the target URL.
- The prompt *No connections configured — open Connection Manager?* is deferred
  until the main window has been painted.

### DB2 → BigQuery dialect converter (`SqlDialectConverter.java`)

New and changed conversions:

| DB2 | BigQuery |
|---|---|
| `OFFSET n ROWS FETCH FIRST m ROWS ONLY` | `LIMIT m OFFSET n` |
| `FETCH FIRST ROW ONLY` / `FETCH NEXT …` | `LIMIT 1` / `LIMIT n` |
| `CHAR(x, n)` / `VARCHAR(x, n)` | `CAST(x AS STRING)` (length dropped, with a warning) |
| `BIGINT()`, `SMALLINT()`, `REAL()`, `DEC()` | `CAST` / `NUMERIC` as for `INTEGER`, `DOUBLE` and `DECIMAL` |
| `TO_CHAR(d, fmt)` | `FORMAT_DATE` / `FORMAT_TIMESTAMP` |
| `TO_DATE` / `TO_TIMESTAMP` | `PARSE_DATE` / `PARSE_TIMESTAMP` |
| `TO_NUMBER(x)` | `CAST(x AS NUMERIC)` |
| `SUBSTRING(x FROM s FOR l)` | `SUBSTR(x, s, l)` |
| `REGEXP_LIKE` / `REGEXP_SUBSTR` | `REGEXP_CONTAINS` / `REGEXP_EXTRACT` |
| `POSITION(a IN b)` | `STRPOS(b, a)` |
| `DAYNAME` / `MONTHNAME` / `WEEK_ISO` | `FORMAT_DATE('%A' / '%B')` / `EXTRACT(ISOWEEK …)` |
| `SPACE`, `CEILING`, `LOG` | `REPEAT(' ', n)`, `CEIL`, `LN` |
| `BITAND`/`BITOR`/`BITXOR`/`BITNOT`/`BITANDNOT` | `&`, `\|`, `^`, `~` |
| `MINUS` / bare `UNION`/`INTERSECT`/`EXCEPT` | `EXCEPT DISTINCT` / `… DISTINCT` |

The converter adds warnings for constructs that have no direct equivalent:
sequences (`NEXT VALUE FOR`), `NEXT_DAY`, `DAYOFWEEK_ISO`, the `HASH*` functions,
`TRIM(LEADING|TRAILING …)`, extra `REGEXP_REPLACE` arguments, and
`INTERSECT ALL` / `EXCEPT ALL`.

The **CTE column-list rewrite** (`WITH x(a, b) AS (…)` → aliases injected into
the body) is now string-based instead of JSQLParser-based. DB2 input with host
variables or vendor syntax no longer makes the rewrite fail silently. It also
handles set-operation bodies, where aliases go on the first branch. When the
column list cannot be converted (`SELECT *`, a count mismatch, or a `VALUES`
body), a warning is issued and the CTE is left unchanged.

### Ext Format SQL line wrapping (`FormSQL2.java`, `PropmSQL.java`)

`wrapLongLines()` runs after formatting. Continuation lines are indented two
spaces beyond the original line. `-- comments` are never wrapped. The new
`FormSQL2.formatToWidth(sql, width)` forces a given width; *Save Query to
Mainframe* uses it with width 72. If formatting fails, the original text is
wrapped instead.

### Help menu on the main toolbar (`SuiTb.java`)

The help documents are listed in a single `HELP_DOCS` table in `SuiTb`. Adding a
new help page takes one row. Each entry opens the Markdown document in the
in-app `HelpDialog` viewer.

---

## Files Changed

| File | Change |
|---|---|
| `src/ZoweConnManager.java` | New — Zowe connection profiles, TLS/certificate-source settings, port validation |
| `src/ZoweOpenDataset.java` | New — *Open Mainframe Dataset* dialog |
| `src/ZoweSaveDataset.java` | New — *Save to Mainframe Dataset* dialog (existing targets only, overwrite confirm, optional 72-column formatting) |
| `src/ZoweDatasetList.java` | New — Mainframe Explorer (dataset/member list, Browse/Edit, level history) |
| `src/ZoweService.java` | New — reflection bridge to the integration JAR (read / write / listDatasets / listMembers, certificate source) |
| `src/Sui.java` | Mainframe menu items + Java 11 / availability gating; `zoweconfig.pro` load/store; `getQueryLines()`; credential-group session cache; EDT startup, `connectAsync()` / `finishConnect()`; startup timing log; undo/redo fixes; single line-number gutter instance; panel-visibility helpers; version bump |
| `src/QueryRep.java` | *Save to mainframe* toolbar button + `getMainframeCsvLines()`; multiple-interval selection; *Transpose selected rows* replaces mark-and-transpose |
| `src/QryPop.java` | Show/Hide toggles for SQL Object Tree, Query Tree, Sheet Overview, Query Toolbar, Query Tabs |
| `src/ConnManager.java` | *Group* field; *Apply* button; immediate *Delete*; group-combo display fix |
| `src/SuiTb.java` | Help *(i)* button with popup menu of all help documents |
| `src/SqlDialectConverter.java` | New conversions and warnings; string-based CTE rewrite; set-operator qualifiers |
| `src/FormSQL2.java` | Max output line length wrapping; `formatToWidth()` |
| `src/PropmSQL.java` | *Max output line length* setting; relabelled *Max inline expr. length* |
| `src/CsvCompare.java` | Numeric-value equality and key normalisation |
| `src/TextLineNumber.java` | Width from text-component font metrics, padding, right alignment |
| `src/DB2SQLCA.java` | Reflection-only access to `com.ibm.db2.jcc` classes |
| `src/ExpXLS.java`, `src/ExpXLSRS.java` | Version stamp `0.75Z` |
| `src/driver.pro`, `src/url.pro` | `BigQuery-Google` driver and URL template |
| `pom.xml` | `full` / `nobq` / `nodb2` / `minimal` profiles; BigQuery JDBC + Db2 JCC dependencies; CVE overrides; version `0.75Z` |
| `docs/MainframeExplorer.md` | New |
| `docs/ConnManager.md` | *Group* field; BigQuery-Google setup; driver/profile notes |
| `docs/CredentialHandling.md` | *Credential groups* section |
| `docs/AdditionalEditFunctions.md` | *Panel visibility toggles* section |
| `README.md`, `USAGE.md` | Build-profile instructions; bundled-driver notes |
| `.github/workflows/publish-to-suidistro.yml` | Actions upgraded to v5; SuiDistro checkout fix |
