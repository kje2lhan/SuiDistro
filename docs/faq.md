---
title: FAQ
---

# Frequently asked questions

## General

??? question "Is Sui really free?"
    Yes. Sui is freeware: free to use, at home and at work, and free to pass on to others as long as the
    jar is unchanged. Sui is not open source. See the [license](license.md).

??? question "Which download should I pick?"
    Take `sui-full.jar` if you use Db2 or BigQuery, or if you're unsure. `sui-minimal.jar` has every
    feature but leaves out those two drivers to save about 70 MB. See [Download](download.md).

??? question "Which Java version do I need?"
    Java 8 or later. The mainframe (Zowe) features need Java 11 or later, and their menu items are
    hidden on older Java versions.

??? question "Where are my settings stored, and how do I move them to another computer?"
    All settings are plain-text `.pro` files in one folder, by default `%USERPROFILE%\AppData\Sui\` on
    Windows. Copy that folder to move or back up your connections, query sheets and preferences. A
    `Sui.ini` next to the jar can point Sui at another folder. See [Sui home directory](SuiHome.md).

??? question "How do I upgrade?"
    Replace the jar with the new one. Your settings are not stored in the jar.

??? question "A settings file got corrupted. What now?"
    See [Profile recovery](ProFileRecovery.md).

## Writing and running SQL

??? question "How do I run several statements in one go?"
    End each statement with the statement delimiter, `;` by default. You can change the delimiter in
    the preferences (`SUI.ENDSQLSTMT`).

??? question "Can I have Sui ask me for a value when the query runs?"
    Yes. Write `&NAME` in the SQL, and Sui prompts for a value for `NAME` when you run it. Use `#SET=`
    and `&&NAME` to set a value once and reuse it without a prompt. See
    [Inline directives](InlineDirectives.md#using-set-to-suppress-the-prompt-the-prefix).

??? question "Can one script run against more than one database?"
    Yes. Put `#URL= <alias>;` before a statement to switch connection for the rest of the script, or use
    *Broadcast* to run the same query against several connections at once. See
    [Inline directives](InlineDirectives.md).

??? question "Are my passwords saved?"
    Not unless you turn on *Auto-login* for a connection. Otherwise passwords are only kept in memory
    while Sui is running. See [Credential handling](CredentialHandling.md).

## Results and export

??? question "How do I get a result into Excel?"
    Press **Ctrl+T** in the query window to run the query straight to an Excel file, or use the Excel
    button in a result window. The workbook has a *Sui-Export* sheet with the data and a *Sui-Meta* sheet
    describing the query. See [Export](QueryRepWindow.md#export).

??? question "How do I filter a result?"
    Right-click a cell and choose **Filter on value**, or right-click a column header and choose
    **Apply Filter** for operators like `>`, `BETWEEN` and `LIKE`. See [Filtering](QueryRepWindow.md#filtering).

??? question "How do I see a wide row more easily?"
    Select the row and press **Ctrl+L** (*Transpose Row*). The row opens as a two-column list of column
    names and values.

??? question "How do I compare two results?"
    Open both results and use the **≠** button in one of them. See [Result set compare](ResultSetCompare.md).

## Help and contact

??? question "I found a bug or have an idea. Where do I report it?"
    Open an issue on [GitHub](https://github.com/kje2lhan/SuiDistro/issues). Include the Sui version,
    the database and driver version, the SQL (or a smaller example) and any text from the System Log.
