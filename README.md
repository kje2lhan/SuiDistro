# suidev080

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

