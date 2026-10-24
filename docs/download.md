---
title: Download
---

# Download Sui {{ sui_version }}

Sui is free to use and share. See the [license](license.md).

## Choose a download

| Download | Size | What's included | Pick this if… |
|---|---|---|---|
| [**sui-full.jar**]({{ download_base }}/sui-full.jar){ .md-button .md-button--primary } | ~95 MB | Sui with the IBM Db2 and Google BigQuery JDBC drivers built in | You use Db2 or BigQuery, or you're not sure |
| [**sui-minimal.jar**]({{ download_base }}/sui-minimal.jar){ .md-button } | ~25 MB | The same application, without the Db2 and BigQuery drivers | You only use other databases, or want a small download |

Every feature is in both downloads. With the minimal jar, you can still add a Db2 or BigQuery driver yourself
in the [Driver / JAR tab](ConnManager.md#tab-2-driver-jar).

SHA-256 checksums for each release are in
[`SHA256SUMS.txt`]({{ download_base }}/SHA256SUMS.txt). Earlier versions are on the
[releases page]({{ releases_url }}).

## Requirements

- **Java 8 or later.** Any OpenJDK build (for example [Eclipse Temurin](https://adoptium.net/)) or Oracle Java works.
- **Java 11 or later** if you want the mainframe (Zowe) features, which also need the optional
  [Zui.jar]({{ download_base }}/Zui.jar) add-on. See [Mainframe Explorer](MainframeExplorer.md).
- Windows, Linux or macOS.

## Install and start

There is no installer. Sui is one file.

1. Save the jar in a folder of your own, for example `C:\Sui\` or `~/sui/`.
2. Start it by double-clicking the jar, or from a terminal:

    ```
    java -jar sui-full.jar
    ```

3. On the first start, Sui creates its settings folder (on Windows `%USERPROFILE%\AppData\Sui\`).
   To keep the settings next to the jar instead, for example on a USB stick, see
   [Sui home directory](SuiHome.md).
4. Open **File → Connection Manager…** to add your first connection. The
   [Connection Manager guide](ConnManager.md#workflow-first-time-setup) walks you through it.

## Upgrading

Replace the old jar with the new one. Your connections, query sheets and preferences are kept in the
settings folder, not in the jar, so nothing is lost. Read the [changelog](Changelog.md) to see what's new.
