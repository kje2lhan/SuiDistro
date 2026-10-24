---
title: Sui does SQL
hide:
  - navigation
  - toc
---

<div class="sui-hero" markdown>
<img class="sui-hero__logo" src="assets/images/sui_liten.png" alt="Sui logo">
<div markdown>
<h1>Sui does SQL</h1>
<p class="sui-hero__tagline">A fast, focused desktop SQL client for any database with a JDBC driver. One window, one jar, free.</p>
<div class="sui-hero__actions" markdown>
[Download Sui {{ sui_version }}](download.md){ .md-button .md-button--primary }
[What's new](ReleaseNotes-{{ sui_version }}.md){ .md-button }
</div>
<p class="sui-hero__meta">Runs on Windows, Linux and macOS with Java 8 or later · No limits, no ads, no strings attached</p>
</div>
</div>

<!--
Screenshot goes here. Save a current screenshot as docs/assets/images/screenshot-main.png and uncomment:
![The Sui main window](assets/images/screenshot-main.png)
-->

Open it, connect, and start writing SQL: no project setup, no per-database plug-ins, no cloud account.
Sui is made for developers, testers, DBAs and power users who move between many databases during a day
and want one tool that stays open all the time.

<div class="sui-features" markdown>

<div class="sui-feature" markdown>
### Many databases, one tool
Save every connection as a named alias and switch with one click. Run the same query against several
connections at once with *Broadcast*. [Connection Manager →](ConnManager.md)
</div>

<div class="sui-feature" markdown>
### Compare results
Run the same SQL before and after a deployment, or against DEV and PROD, and see exactly what changed,
down to the cell. [Result Set Compare →](ResultSetCompare.md)
</div>

<div class="sui-feature" markdown>
### Big result sets
Filter, sort, freeze, hide, transpose and diff-highlight. Export to CSV or Excel, or build `WHERE` clauses
and `INSERT`s straight from a row. [Query result window →](QueryRepWindow.md)
</div>

<div class="sui-feature" markdown>
### A focused SQL editor
Syntax highlighting, formatting, keyword expansion, schema rewrite, IN-list builder and a
DB2 ↔ BigQuery dialect converter. [Edit functions →](AdditionalEditFunctions.md)
</div>

<div class="sui-feature" markdown>
### Scriptable sessions
Switch connection mid-script with `#URL=`, set variables with `#SET=`, prompt for values with `&NAME`,
and include SQL files. [Inline directives →](InlineDirectives.md)
</div>

<div class="sui-feature" markdown>
### Mainframe ready
DB2 for z/OS out of the box, plus a Zowe-based Mainframe Explorer for browsing and editing datasets
and PDS members. [Mainframe Explorer →](MainframeExplorer.md)
</div>

</div>

## Works with your database

**IBM Db2** (LUW and z/OS) and **Google BigQuery** drivers are included in the full download.
**PostgreSQL**, **MariaDB / MySQL**, **Oracle**, **SQL Server**, **Mimer**, **Apache Derby**, **SQLite**, **H2**
and any other JDBC database work by pointing Sui at the driver JAR. No restart needed.
[Databases and drivers →](databases.md)

## Get started in three steps

1. Install **Java 8** or later.
2. [Download Sui](download.md) and run `java -jar sui-full.jar` (or double-click the jar).
3. Open **File → Connection Manager**, add a connection and click **Test Connection**.

Your settings live in plain-text files in one folder you choose, so they are easy to back up or move
between machines. [Where Sui keeps its files →](SuiHome.md)
