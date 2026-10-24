---
title: Databases and drivers
---

# Databases and drivers

Sui works with any database that has a JDBC 4.x driver. The Connection Manager has ready-made
driver templates for the databases below, so you only fill in server, port and database name.

| Database | Driver | Notes |
|---|---|---|
| IBM Db2 for LUW and z/OS | Included in `sui-full.jar` | With `sui-minimal.jar`, add `db2jcc4.jar` yourself. See [Db2 properties](ConnManager.md#db2-common-jdbc-properties) and [Db2 SSL / TLS](ConnManager.md#db2-ssl-tls-setup) |
| Google BigQuery | Google's driver (*BigQuery-Google*) included in `sui-full.jar`; the Simba driver is also supported | OAuth login through the browser. See [BigQuery setup](ConnManager.md#bigquery-google-driver-setup-and-common-properties) |
| Microsoft SQL Server / Azure SQL | Add the Microsoft JDBC driver JAR | See [SQL Server properties and TLS](ConnManager.md#sql-server-common-jdbc-properties) |
| Oracle | Add `ojdbc*.jar` | Several JARs at once: use a pattern such as `C:\drivers\oracle\*.jar` |
| PostgreSQL | Add the PostgreSQL JDBC JAR | |
| MariaDB / MySQL | Add the MariaDB or MySQL Connector/J JAR | |
| Mimer SQL | Add the Mimer JDBC JAR | |
| Apache Derby | Add the Derby client JAR | |
| SQLite, H2 | Add the driver JAR | |
| Anything else with JDBC | Add the JAR and a custom driver row | Set the driver class and URL template |

## Adding a driver JAR

1. Download the JDBC driver from the database vendor.
2. In Sui, open **File → Connection Manager…** and switch to the **Driver / JAR** tab.
3. Select the driver row, click **Browse JAR…** and pick the file.
4. Click **Reload JARs**. The status turns green when the driver loads. No restart is needed.

All connections that use the same driver share one JAR path, so you only do this once per driver.
Full details: [Connection Manager → Driver / JAR](ConnManager.md#tab-2-driver-jar).

## Driver settings (JDBC properties)

Each driver accepts extra connection properties, for example a default schema, TLS settings or a client
program name. Sui lets you set them once for every connection of a driver, or only for one connection.
See [JDBC Properties](ConnManager.md#tab-3-jdbc-properties).

!!! tip "Db2 tip"
    Add `jdbc:db2.retrieveMessagesFromServerOnGetMessage = true` as a generic property. Db2 errors then
    show the full message text instead of only `SQLCODE=-204, SQLSTATE=42704`.

## Mainframe datasets

Besides Db2 for z/OS, Sui can browse, open and save mainframe datasets and PDS members through
Zowe / z/OSMF. This needs Java 11 and the optional `Zui.jar`. See [Mainframe Explorer](MainframeExplorer.md).
