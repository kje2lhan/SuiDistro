# suidev080

Sui 0.75I
---------
- SQL Object Tree: Pressing Enter in the Schema or Table filter field now immediately refreshes the tree (no need to click the Refresh button)
- BigQuery: Improved catalog resolution — `effectiveCatalog` derived from `projectid=` in the JDBC URL, with `supportsCatalogsInTableDefinitions` check to handle catalog-vs-schema differences correctly
- Bug fix: SQL content in a tab is now preserved correctly when a new tab is opened (`newTabSQL` guard added to `TabbedPaneClassic`)

Sui 0.75H
---------
- SQLite support: SQLite JDBC driver (org.xerial sqlite-jdbc) is now bundled — SQLite databases can be connected to without installing a separate driver
- Query Editor popup: "Text → Insert Statement" — converts selected text rows into SQL `INSERT INTO schema.table VALUES (…)` statements; supports single-row and multi-row batch mode
- SQL Object Tree: Table loading now respects catalog for catalog-aware databases (`sCatalog` parameter passed to `getTables()`)
- SQL Object Tree: Mimer SQL support improved — tables are retrieved correctly with product-name detection
- TableProvider: catalog-aware table listing (`GetCatalog` used when available)
- Updated FlatLaf Look & Feel library — newer version bundled with additional built-in themes (Darker, Light, Lighter, Ocean, Oceanic, Owl, Palenight, Pro)

Sui 0.75G
---------
- Toggle Comment on selected lines (Ctrl+7)
- Go to Line dialog (Ctrl+G)
- Block Indent / Unindent (Tab / Shift+Tab with selection)
- Uppercase / Lowercase Selection (Ctrl+Shift+U / Ctrl+Shift+L)
- Parenthesis matching highlight — enable/disable from right-click menu
- Cursor position indicator (Ln / Col) displayed above query tabs
- SQL Object Tree: Schema / Table filter fields with titled border
- SQL Object Tree: Better icons — table grid for SQL Tree, pages for Query Tree toolbar buttons
- SQL Object Tree: Frame icon switches between `db.gif` (SQL tree) and `pages.gif` (file tree)
- Query Editor popup: "Build IN List from Selection" — converts selected values to SQL `IN (…)` clause
- Query Editor popup: "Copy Columns from Selection…" — extracts fixed-position column range to clipboard
- Query Report popup: "Copy WHERE clause from row" — builds `WHERE col = val AND …` from the selected row
- Bug fix: Status message not cleared before showing "Columns copied to clipboard"

Sui 0.75F
---------
- New `SQLTreePanel` — lazy-loading JTree of schemas → tables → columns
- Toolbar buttons to show SQL Object Tree / Query File Tree
- Right-click table node: "Build SQL to clipboard", "Draw SQL (SELECT)", "Draw SQL (INSERT)"
- Drag table node to query window — choose `schema.table` or full `SELECT` statement
- Drag column node to query window — inserts column name at caret
- DB2: SQLCODE -4471 resolved — `conn.commit()` added after every metadata `ResultSet` close
- DB2: System schemas (SYSIBM, SYSCAT, SYSSTAT, etc.) filtered from tree
- DB2: `getColumns()` called with `null` column-name pattern instead of `%` wildcard
- BigQuery: OAuth connection cache preserved — `closeConn()` is a no-op for BigQuery
- BigQuery: Schema list filtered to current project only (extracted from JDBC URL `ProjectId=`)
- BigQuery: `project.dataset` schema name prefix stripped before `getTables()` call
- Mimer SQL: Tables now load — `null` catalog and `null` table-type filter used in `getTables()`
- Mimer SQL: Schema name uppercased for Mimer and DB2 before metadata calls

Sui 0.75C
---------
- Fixed decimal precision for NUMERIC/DECIMAL columns in query results panel and CSV export
- Fixed compilation error in "Send query to" mail feature (java.awt.Desktop name clash)

Sui 0.75B
---------
- Security fix: command injection vulnerability in "Send query to" mail feature eliminated
- DatabaseManager now delegates to ConnDB, ensuring SuiConnPref.pro properties (including BigQuery OAuth settings) are always applied
- Connection and classpath preferences now saved immediately when the preferences dialog is closed, not only at application shutdown
- Fixed file-handle leak in profile store (StoreProf)
- Added credential handling documentation (docs/CredentialHandling.md)

Sui 0.75A
---------
- BigQuery connections now kept in a cache with a 10-hour TTL, reducing repeated connection overhead
- Row limit enforced for BigQuery result sets to prevent runaway memory use
- All cached connections are closed gracefully at application exit
- DConnInf completely rewritten — now displays approximately 80 JDBC metadata properties
- Fixed compatibility issues with older JDBC drivers (AbstractMethodError, Mimer SQLException)
- Improved thread safety: all 7 `.pro` file save methods are now synchronized
- Fixed Garabage background thread (interrupt handling, dead code removal)
- Build version and timestamp are now baked into the jar and shown in the About dialog
- New DatabaseManager helper class added
- All image assets moved to `src/imgs/` subfolder
- Unused source files moved to `src/unused/`
- Updated POM dependencies to remove known security vulnerabilities
- Added new documentation: USAGE.md and several docs/ files

Sui 0.74
------
- New Option to blank out password, when a new not previously not connected URL is selected (Misc properties 
  set PW Blank is not connected
- Added function to customize lookandFeel, added Flatlaf Sample Sui.ini to use a black theme:   
 SuiHome=c:\SuiDev;                          
 font=consolas,13;                           
 pyjamas=false;                              
 LookandFeel=com.formdev.flatlaf.FlatDarkLaf;
- New function to format/Make a JSON string readable from 


Sui 0.73

Version 0.73 up to 0.73K
------------
- Added function to mark SQL at cursor (based on usage of Semicolon as delimiter) (Shift f1)
  Example : Place cursor att the second row and press Shift-F1, SELECT * FROM SYSIBM.SYSCOLUMNS is marked.
- Added function to execute SQL at cursor (based on usage of Semicolon as delimiter) (Shift f2)
- Corrected some issues in Export Excel
- Added DB2 specific functions to list columns (F6) and Tablespace (F7)
- Improved handling using the SuiConnPref.pro file
- Changed the syntax for include statement, the syntax is now:
<include>c:\folder\file</include>  (Where c:\folder\file is a fully qualified file name)
- Changed source for extended Format SQL to make it generally available
- Removed built in support for Derby
- Did some cleanup in Find-Replace logic

Version 0.73L
-------------
- Made it possible to only execute marked SQL from query box
- Made it possible to run SQL and get result directly to Excel from query box
- Built function to search for text strings in Sheets Version (querysheetviewer) right click and query window and select from list)
- Added F8 option to list content of View only avaialable for DB2 in same way as F6 to list columns and F7 to List tablespace)
- Made it possible to use variable when setting suihome variabeln for SuiConnPref
- Made it possible to use variable when setting suihome for SuiCPProp
- Fixed nullpointer eception in startup when deleteing temp datasets
- Added confirm dialog for delete from file tree

