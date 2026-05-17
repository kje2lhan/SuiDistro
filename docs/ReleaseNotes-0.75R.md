# Release Notes — Sui 0.75R

**Branch:** `Sui0.75Q` → `Sui0.75R`  
**Base:** `Sui 0.75Q` (Result Set Compare filters, Query Report Trim, Preferences restructuring)  
**Date:** 2026-05-16  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| FlatLaf theming | New feature | FlatLaf Light, Dark, IntelliJ and Darcula themes selectable from **Preferences → Misc** without editing `Sui.ini` |
| FlatLaf theming | Enhancement | L&F applied before any Swing component is created — full theme coverage including menus and toolbars |
| FlatLaf theming | Bug fix | Menu bar was rendered in hardcoded gray instead of theme colour |
| FlatLaf theming | Bug fix | First connection history entry rendered with opaque green background, bypassing L&F renderer — replaced with bold font |
| FlatLaf theming | Bug fix | Syntax highlighter reset all text to `Color.black` on every keystroke — invisible on dark backgrounds; now uses `UIManager` foreground |
| FlatLaf theming | Bug fix | `JScrollPane` viewport background not updated on L&F switch — editor area appeared white in dark mode |
| Query Sheet Overview | Enhancement | Double-click on any column opens the corresponding tab (was: opened the inline name editor) |
| Query Sheet Overview | Enhancement | "Rename sheet…" context-menu item — prompts for a new name via `JOptionPane` |
| Query Sheet Overview | Enhancement | Zebra stripe renderer is theme-aware — uses `UIManager` table colours; dark-mode alternating row colour no longer hardcoded |
| Query Sheet Overview | New feature | **Clear colors** button — resets all tab background colours to the theme default and removes all `SUI.TABCOLOR.*` properties |
| Query Sheet Overview | Bug fix | Tab colours no longer saved when they equal the `JTabbedPane` theme default — prevents dark-mode colours being restored as user colours on next light-mode startup |
| Connection bar (ShowQryBox) | Bug fix | Switching connection from the connection bar in a Query Box / Sync SQL window no longer hides that window behind the main frame |
| Right-click popup | Enhancement | Format SQL, Extended Format SQL and Syntax Validate moved to top level of the popup |
| Right-click popup | Enhancement | "Additional Edit functions" submenu groups remaining edit operations |
| ShowQryBox | Enhancement | Connection bar shown for all window types (QueryBox, QuerySheet, SyncSQL) |
| ShowQryBox | Enhancement | Add Schema / Remove Schema buttons |
| DiffRep (Result Set Compare) | Enhancement | Unified column-roles panel; `batch=YES;` prefix support; Sync SQL opens in ShowQryBox |
| About dialog | Enhancement | Replaced plain `JOptionPane` with a styled `JDialog` — logo, HTML content, clickable links |
| Version | Bump | `0.75Q` → `0.75R` in `Sui.java`, `pom.xml`, About dialog |

---

## Detailed Changes by Area

---

### FlatLaf Theming (`Sui.java`, `PropmMisc.java`, `Highlighter.java`)

#### Selectable without `Sui.ini`

Four FlatLaf base themes are now registered with `UIManager.installLookAndFeel()` at startup:

| Name | Class |
|---|---|
| FlatLaf Light | `com.formdev.flatlaf.FlatLightLaf` |
| FlatLaf Dark | `com.formdev.flatlaf.FlatDarkLaf` |
| FlatLaf IntelliJ | `com.formdev.flatlaf.FlatIntelliJLaf` |
| FlatLaf Darcula | `com.formdev.flatlaf.FlatDarculaLaf` |

These appear in the **Preferences → Misc → Look and Feel** dropdown alongside the standard JDK themes and any installed FlatLaf IntelliJ Theme variants.

The Preferences dropdown now uses full-name matching to select the current L&F (`SUI.LF` property) — previously only the first character was compared, which broke for FlatLaf names that all start with "F".

#### Applied before component creation (`applyLFEarly()`)

`UIManager.setLookAndFeel()` only affects components created *after* the call. Previously `setLF()` was called after the entire main window was constructed, limiting its effect.

A new `applyLFEarly()` method is now invoked between `LoadProp()` and `LoadSheetProp()` — before any Swing component is instantiated. It reads `SUI.LF` (Preferences selection) first, then falls back to `LookandFeel=` from `Sui.ini`.

`JFrame.setDefaultLookAndFeelDecorated(true)` is set for FlatLaf to get themed window decorations.

#### `setLF()` late-pass cleanup

`setLF()` (called after the frame is built) is now a thin late-pass:

- Calls `SwingUtilities.updateComponentTreeUI(thisJFrame)` on the full frame (not just the content pane) to also re-theme the `JMenuBar`
- Calls `resetTextAreaColors()` to sync the query text area and its `JScrollPane` viewport to the theme background/foreground

#### Syntax highlighter foreground fix (`Highlighter.java`)

`processChangedLines()` previously reset all text to `Color.black` before re-applying keywords. On a dark background this made non-keyword text invisible. Now reads `UIManager.getColor("TextPane.foreground")` with `Color.black` as fallback.

---

### Query Sheet Overview (`QuerySheetListPanel.java`)

#### Double-click behaviour

Double-clicking any row (except the colour swatch in column 0) now calls `openSelectedTab()`. Previously double-clicking column 1 opened an in-place name editor.

Column 1 is no longer editable (`isCellEditable` always returns `false`).

#### Rename sheet

"Rename sheet…" added to the right-click context menu alongside "Open selected tab" and "Show content in query box". It opens a `JOptionPane.showInputDialog` pre-filled with the current tab name, and on confirmation propagates the new name via `model.setValueAt()` which the `TableModelListener` already forwards to `TabbedPane.setTitleAt()`.

#### Clear colors button

A **Clear colors** button was added to the south panel (between "Reset" and "Close"). Clicking it:

1. Calls `Sui.resetAllTabColors()` — sets all `TabbedPane` tab backgrounds to `null` and removes all `SUI.TABCOLOR.N` entries from the properties store
2. Updates the table model col 0 (colour swatches) to `null` so the list reflects the change immediately

#### Tab colour save fix

`StoreProf()` previously saved a tab colour whenever `getBackgroundAt(i)` returned non-null. In FlatLaf, uncoloured tabs return the component's theme background (non-null), causing those dark-mode colours to be written as `SUI.TABCOLOR.N` and restored on next light-mode startup.

The save condition now checks `!tc.equals(TabbedPane.getBackground())` — only colours that differ from the `JTabbedPane` default are saved as explicit user choices.

---

### Connection Bar — Window Focus Fix (`Sui.java`)

`ConnDB()` ends with `textArea.requestFocus()`, which raises the main Sui frame to the front. When a connection switch was triggered from the connection bar inside a `ShowQryBox` window, the `ShowQryBox` was pushed behind the main frame.

After `ConnDB()` returns, `makeConnBar()` now calls:

```java
Window connBarWin = SwingUtilities.getWindowAncestor(lbl);
if (connBarWin != null && connBarWin != thisJFrame)
    SwingUtilities.invokeLater(connBarWin::toFront);
```

`invokeLater` ensures this runs after all pending AWT events (including the `requestFocus`) have been processed.

---

### About Dialog (`Sui.java`)

The plain `JOptionPane.showMessageDialog` was replaced with a `JDialog` containing:

- **Header panel**: `sui.gif` logo scaled to 48×48 alongside "SQL User Interface" title and version subtitle
- **Details area**: HTML table with Build ID, home page as a clickable link (`java.awt.Desktop.browse`), support email as a `mailto:` link, and Sui home path
- **Copyright notice** in small gray text
- **Separator + OK button** (Enter key closes the dialog)
- Theme-aware — backgrounds use `UIManager.getColor("Panel.background")`

---

## Files Changed

| File | Change summary |
|---|---|
| `src/Sui.java` | `applyLFEarly()`, `resetAllTabColors()`, `setLF()` simplification, `resetTextAreaColors()` viewport sync, `makeConnBar()` window-focus fix, About dialog, version bump, `Ver` string |
| `src/PropmMisc.java` | `getBLF()` full-name matching for L&F dropdown |
| `src/Highlighter.java` | `processChangedLines()` theme-aware foreground reset |
| `src/QuerySheetListPanel.java` | Double-click opens tab, `isCellEditable` always false, "Rename sheet…" context menu, "Clear colors" button, theme-aware `ZebraRenderer` |
| `src/QryPop.java` | Format SQL / Ext Format SQL / Syntax Validate at top level; "Additional Edit functions" submenu |
| `src/ShowQryBox.java` | Connection bar for all types; Add Schema / Remove Schema buttons |
| `src/DiffRep.java` | Unified column-roles panel; `batch=YES;` prefix; Sync SQL in ShowQryBox |
