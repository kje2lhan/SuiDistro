# Sui — a fast, focused desktop SQL workbench

**Sui** (SQL Utility Interface) is a single-window, single-jar Java/Swing desktop
client for running SQL against any database that ships a JDBC driver. It is built
around a simple promise: open it, connect, and start writing SQL — no project
setup, no per-database extension to install, no cloud account, no editor licence.

If you spend your day moving between DB2, BigQuery, PostgreSQL, Oracle, MariaDB /
MySQL, SQL Server, SQLite, H2, Derby and a handful of in-house JDBC sources, Sui
is designed to be the one tool you keep open all the time.

> Looking for what changed in the latest version? See the
> [Sui 0.75V release notes](docs/ReleaseNotes-0.75V.md) — or the
> [full version history](docs/Changelog.md).

---

## What Sui is good at

- **Working across many databases at once.** Save every connection you use as a
  named alias once, then switch with a single click. Run the *same* query
  against several connections in one step with the
  [Broadcast feature](docs/ReleaseNotes-0.75U.md), or jump mid-script with the
  inline [`#URL=` directive](docs/InlineDirectives.md).
- **Comparing results.** Run the same SQL before and after a deployment, against
  DEV and PROD, or against two different vendors, and instantly see what changed
  with the [Result Set Compare](docs/ResultSetCompare.md) view.
- **Working with big result sets.** Filter, sort, freeze columns, hide columns,
  zoom, transpose, diff-highlight individual cells, copy WHERE clauses out of a
  row, build INSERT statements from a row, and export to CSV or Excel — all from
  the [query result window](docs/QueryRepWindow.md).
- **Editing SQL.** A focused SQL editor with syntax highlighting, parenthesis
  matching, F1 keyword expansion, a built-in formatter, an extended formatter
  (parser-based), a one-click [DB2 ↔ BigQuery dialect converter](docs/ReleaseNotes-0.75L.md),
  schema add / remove / replace tools, "Build IN list", "Text → INSERT", and a
  long list of other small tools collected in the
  [Additional Edit Functions](docs/AdditionalEditFunctions.md) menu.
- **Exploring a database visually.** A live SQL Object Tree with schemas →
  tables / views / aliases / synonyms / routines / indexes, right-click actions
  for "Count rows", "Generate DDL", "Sample distinct values", "Column statistics",
  "Referential integrity", vendor-specific table-space and additional-info
  lookups, and drag-and-drop of table / column / procedure names into the
  editor.
- **Saving sensitive credentials safely.** Passwords are kept in memory only
  unless you explicitly opt-in to Auto-login per connection. See
  [Credential Handling](docs/CredentialHandling.md) for the full priority rules.
- **Staying out of your way.** All configuration lives in plain-text `.pro`
  files inside one directory you choose
  ([SuiHome.md](docs/SuiHome.md)); the application is a single `Sui.jar` that
  runs anywhere a JRE 8+ is installed.

---

## Highlights at a glance

| Feature | Where to read more |
|---|---|
| Named connection profiles + driver catalog + JDBC properties editor | [docs/ConnManager.md](docs/ConnManager.md) |
| DB2 — common JDBC properties, SSL / TLS setup | [docs/ConnManager.md#db2--common-jdbc-properties](docs/ConnManager.md) |
| BigQuery — OAuth setup, sessions, region selection | [docs/ConnManager.md#bigquery--common-jdbc-properties](docs/ConnManager.md) |
| Query result window — filtering, sorting, freezing, diff-highlight, transpose, exports | [docs/QueryRepWindow.md](docs/QueryRepWindow.md) |
| Compare two result sets side-by-side, in-memory or via re-run | [docs/ResultSetCompare.md](docs/ResultSetCompare.md) |
| Inline directives — `#URL=`, `#SET=`, variable substitution | [docs/InlineDirectives.md](docs/InlineDirectives.md) |
| Editor toolbox — format, validate, schema-rewrite, IN-list, INSERT-from-text, … | [docs/AdditionalEditFunctions.md](docs/AdditionalEditFunctions.md) |
| Main window layout reference | [docs/MainWindowLayout.md](docs/MainWindowLayout.md) |
| How user IDs and passwords are stored and resolved | [docs/CredentialHandling.md](docs/CredentialHandling.md) |
| Where Sui stores its configuration files (`SuiHome`) | [docs/SuiHome.md](docs/SuiHome.md) |
| Recovering a corrupted `.pro` file | [docs/ProFileRecovery.md](docs/ProFileRecovery.md) |

---

## Supported databases

Sui talks to any database with a JDBC 4.x driver. Out of the box the bundled
driver catalog contains templates for:

- **IBM Db2** for LUW and z/OS (`db2jcc4.jar` — supply the JAR through the
  [Driver / JAR](docs/ConnManager.md) tab).
- **Google BigQuery** (Simba JDBC driver — supply the JAR, OAuth login via
  browser is the recommended flow).
- **PostgreSQL**, **MariaDB / MySQL**, **Oracle**, **Microsoft SQL Server**,
  **Mimer**, **Apache Derby**.
- **SQLite** and **H2** — bundled on the classpath, no extra JAR needed.

Any other JDBC driver works too — drop the JAR in the Driver / JAR tab, add a
custom driver row, set the URL template, and Sui will load it on the next
**Reload JARs**. No restart required.

---

## Getting started

### Prerequisites

- **Java 8** or later (an OpenJDK or Oracle JRE / JDK both work).

### Download

The latest ready-to-run jar is published at
[github.com/kje2lhan/SuiDistro](https://github.com/kje2lhan/SuiDistro).
Grab the most recent `Sui*.jar` from the repository — no Maven build is
required.

### Launch

```powershell
java -jar Sui074-0.0.1-SNAPSHOT-jar-with-dependencies.jar
```

On the first launch Sui creates its configuration directory automatically. By
default that is `%USERPROFILE%\AppData\Sui\`. You can override the location with
a `Sui.ini` file next to the jar — see [docs/SuiHome.md](docs/SuiHome.md).

### Your first connection

1. **File → Connection Manager…**
2. Click **New**, give the connection an alias (`MyDb`, `BQ-Analytics`, …).
3. Pick a **Driver** from the dropdown. The form fields (Server, Port, Database,
   Project, SID) appear or hide based on what the driver needs.
4. If the driver needs an external JAR (Db2, Oracle, …), switch to the
   **Driver / JAR** tab, point **Browse JAR…** at the driver file, and click
   **Reload JARs**. The status column should turn green.
5. Click **Test Connection** — a green confirmation with the database product
   name means you're ready.
6. **Save** to write the profile to disk.

Full walkthrough in [docs/ConnManager.md](docs/ConnManager.md).

---

## A typical session

1. Pick a saved connection from the **URL** dropdown — userid and (if
   auto-login is on) password are filled in automatically.
2. Type or paste SQL into the editor. Several query tabs ("query sheets") can
   stay open at the same time — each one is independent and gets restored on
   the next startup.
3. **Run** the current statement, the whole sheet, or selected text. Each
   `SELECT` opens its own result window — or, if you prefer, a single tabbed
   result frame collects every result you produce.
4. In the result window, sort by clicking a header, filter by right-clicking a
   cell, freeze a column to keep it visible while you scroll, transpose a row
   to see all columns vertically, or compare against another open result with
   the **≠** button.
5. Export anything to **CSV** or **Excel** when you need to share it.
6. Save your tab layout, colours, window positions and recent queries — all of
   that is restored automatically the next time you start Sui.

---

## Customising Sui

Sui is intentionally configuration-light, but most things can be tweaked from
**Options → Preferences**:

- **Look & Feel** — switch between FlatLaf Light, Dark, IntelliJ and Darcula
  themes from a dropdown; the change is applied immediately, no restart.
- **Editor** — font, font size, line wrap, syntax-highlight on/off, parenthesis
  matching, variable-substitution character.
- **Query** — default row limit, extended-format-SQL options (dialect,
  uppercase, comma position, indent), query history size.
- **Export** — CSV and Excel options (delimiter, quoting, font, decimal
  format).
- **Misc** — open results in a single tabbed frame, draw SQL snippets to the
  SQLBox instead of the clipboard, set the active tab colour, …
- **Keywords** — a three-column table mapping F1 triggers to expansions
  (`sel` → `SELECT * FROM `, etc.). Bundled defaults are merged with your
  edits.

All settings are saved to plain-text `.pro` files inside the
[SuiHome](docs/SuiHome.md) directory and can be backed up, version-controlled or
copied between machines as easily as any other text file.

---

## Project structure

| Path | What's there |
|---|---|
| [src/](src/) | Sui source — one Java class per file, no nested packages. |
| [docs/](docs/) | User and reference documentation. |
| [pom.xml](pom.xml) | Maven build descriptor. |
| [maven/](maven/) | Bundled Maven distribution (optional, used by `mvx.bat`). |
| [target/](target/) | Build output (created by Maven). |

---

## Version history

The release notes for each released version live in [docs/](docs/) and can be
read individually:

[0.75V (current)](docs/ReleaseNotes-0.75V.md) ·
[0.75U](docs/ReleaseNotes-0.75U.md) ·
[0.75T](docs/ReleaseNotes-0.75T.md) ·
[0.75S](docs/ReleaseNotes-0.75S.md) ·
[0.75R](docs/ReleaseNotes-0.75R.md) ·
[0.75Q](docs/ReleaseNotes-0.75Q.md) ·
[0.75P](docs/ReleaseNotes-0.75P.md) ·
[0.75O](docs/ReleaseNotes-0.75O.md) ·
[0.75N](docs/ReleaseNotes-0.75N.md) ·
[0.75M](docs/ReleaseNotes-0.75M.md) ·
[0.75L](docs/ReleaseNotes-0.75L.md) ·
[0.75K](docs/ReleaseNotes-0.75K.md) ·
[0.75J](docs/ReleaseNotes-0.75J.md) ·
[0.75G](docs/ReleaseNotes-0.75G.md) ·
[0.75F](docs/ReleaseNotes-0.75F.md) ·
[0.75C](docs/ReleaseNotes-0.75C.md) ·
[0.75B](docs/ReleaseNotes-0.75B.md) ·
[0.75A](docs/ReleaseNotes-0.75A.md)

A single combined per-version highlights file is also available at
[docs/Changelog.md](docs/Changelog.md).

---

## Reporting issues

If something does not work as described, or you have a request, reproduce the
issue with the latest jar from
[github.com/kje2lhan/SuiDistro](https://github.com/kje2lhan/SuiDistro) and
attach the failing SQL (or a minimal reduction of it), the driver / database
version, and any text printed to the console.

---

## Licence

See [LICENSE](maven/LICENSE) for licence details, [NOTICE](maven/NOTICE) for
third-party notices, and [SECURITY.md](SECURITY.md) for how to report security
issues.
