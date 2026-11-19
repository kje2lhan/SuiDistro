# Sui - a focused desktop SQL workbench

Sui is a free, single-jar Java desktop SQL client for any database with a JDBC
driver. Connect to your databases, write SQL, and work with results in one window.

**Current version: Sui {{ sui_version }}.** Requires Java 8 or later.

[Download Sui](download.md){ .md-button .md-button--primary }
[See what's new](Changelog.md){ .md-button }

## Work with your databases

- **Manage connections:** save named profiles and configure JDBC drivers in the
  [Connection Manager](ConnManager.md).
- **Write SQL:** work in multiple [query sheets and tabs](QuerySheetsAndTabs.md),
  with formatting and other [editing tools](AdditionalEditFunctions.md).
- **Explore results:** filter, sort, copy, and export data from the
  [query result window](QueryRepWindow.md).
- **Compare data:** find differences between two result sets with
  [Result Set Compare](ResultSetCompare.md).
- **Access mainframes:** use the optional
  [Mainframe Explorer](MainframeExplorer.md) integration.

## Get started

1. [Download the full or minimal JAR](download.md).
2. Launch it with Java:

   ```sh
   java -jar Sui075-{{ sui_version }}-full-jar-with-dependencies.jar
   ```

3. Open **File > Connection Manager**, create a connection, select a driver, and
   enter your database connection details.
4. Test and save the connection, then open a query sheet and start writing SQL.

For driver setup and connection options, see the
[Connection Manager guide](ConnManager.md). Read
[Credential handling](CredentialHandling.md) for how Sui handles passwords.
