# Release Notes — Sui 0.75S

**Branch:** `Sui0.75R` → `Sui0.75S`  
**Base:** `Sui 0.75R` (FlatLaf theming, About dialog, QuerySheetListPanel, ShowQryBox, DiffRep)  
**Date:** 2026-05-17  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Tabbed Results Window | New feature | `QueryRepTabbedFrame` — singleton JFrame hosting multiple QueryRep result panels as tabs |
| Tabbed Results Window | New feature | Each QueryRep toolbar gets a **← (left arrow)** "Pull me in" button to dock the result into the tabbed frame |
| Tabbed Results Window | New feature | Tab header shows short title (truncated to 35 chars, prefix stripped) with full title as tooltip |
| Tabbed Results Window | New feature | Tab header inline **→** (release) and **×** (close) buttons |
| Tabbed Results Window | New feature | Right-click context menu on tab: **Release me** / **Close** |
| Tabbed Results Window | New feature | **Pull all free results in** button — pulls every open free-floating QueryRep into the tabbed frame |
| Tabbed Results Window | New feature | **Free us all** button — releases every tab back to its own free-floating window |
| Tabbed Results Window | New feature | Closing the tabbed frame closes (disposes) all tabs — not releases |
| Tabbed Results Window | New feature | Clicking a tab header now correctly selects that tab (mouse events forwarded explicitly to `JTabbedPane`) |
| Preferences — Misc | New feature | **Open results in tabbed view** checkbox (`SUI.QREP.TABBED`) — auto-routes new SELECT results into the tabbed frame |
| Result Set Compare (DiffRep) | Bug fix | Tabbed QueryRep instances now appear in the diff picker (were excluded because `isDisplayable()` is false for undisplayed frames) |
| Result Set Compare (DiffRep) | Bug fix | `ArrayIndexOutOfBoundsException` when opening the diff picker from a tabbed QueryRep — fixed by anchoring popup to `mainPanel` and using `ToolBar.getHeight()` |
| Result Set Compare (DiffRep) | Enhancement | JTable now honours dark mode — default rows use `t.getBackground()` / `t.getForeground()` instead of hardcoded `Color.WHITE` |
| Result Set Compare (DiffRep) | Enhancement | Zebra striping on the diff table (theme-adaptive, ~8% blend towards foreground on odd rows) |
| Result Set Compare (DiffRep) | Enhancement | Diff-coloured rows (green/red/yellow) force `Color.BLACK` foreground for readability in dark mode |
| Result Set Compare (DiffRep) | Enhancement | Legend swatches ("Left only", "Right only", "Value differs") force `Color.BLACK` foreground — were unreadable in dark mode |
| SQL Object Tree | Enhancement | JInternalFrame icon removed when showing the SQL Object Tree (was `db.gif`, which looked out of place) |
| SQL Object Tree toolbar button | Enhancement | `TbSQLTree` now shows text label "DB tree" instead of the `selecttable_16x16.png` icon |
| Version | Bump | `0.75R` → `0.75S` in `Sui.java`, `pom.xml`, About dialog |

---

## Detailed Changes by Area

---

### Tabbed Results Window (`QueryRepTabbedFrame.java`, `QueryRep.java`, `RunIt.java`, `PropmMisc.java`, `Sui.java`)

#### Overview

A new **Query Results** tabbed frame allows result windows to be docked into a shared tab strip. Each result can be moved between free-floating and tabbed mode at any time without re-executing the query. See [QueryRepWindow.md](QueryRepWindow.md) for the full user guide.

#### QueryRep changes

- `mainPanel` (`JPanel`) extracted from `getContentPane()` so its content can be reparented into a tab without rebuilding the UI.
- Key bindings (Ctrl+F, Ctrl+G) moved from `getRootPane()` to `mainPanel` so they continue to work when hosted in a tab.
- `windowClosing` guard: returns immediately when `isTabbed` is true (the JFrame is invisible; the actual close is handled by the tab's × button).
- New toolbar button `TbTab` (left arrow `left.png`) at the far right — hidden when docked, shown on release.
- New methods: `getMainPanel()`, `getRepTitle()`, `isTabbed()`, `pullIntoTabs()`, `releaseFromTabs()`, `closeRep()`.

#### QueryRepTabbedFrame (new file)

Singleton `JFrame`. Key design points:

| Feature | Detail |
|---|---|
| Singleton | `getInstance()` recreates if `!isDisplayable()` (i.e. after the window was closed) |
| Tab header | Custom `TabHeader` inner panel with label + → (release) + × (close); mouse listener on panel and label explicitly calls `setSelectedIndex()` |
| Bulk operations | "Pull all free results in" iterates `Window.getWindows()`; "Free us all" iterates `panelMap` copy |
| Close behaviour | `windowClosing` → `closeAll()` — calls `closeByQR()` on every tab (disposes `QueryRep`), does not release |
| Title trimming | Strips `"Query Report - "` / `"Query Rep "` prefix; truncates to 35 chars with `…` |

#### Preference

`PropmMisc` gains an **Open results in tabbed view** checkbox (property `SUI.QREP.TABBED`, default `N`). `Sui.isQRepTabbed()` reads it.

`RunIt.java` routes new results: when `isQRepTabbed()` is true, calls `tb.pullIntoTabs()` instead of `tb.show()`.

---

### Result Set Compare — Dark Mode & Tabbed Fixes (`DiffRep.java`, `QueryRep.java`)

#### Dark mode rendering

`DiffCellRenderer` now uses `t.getBackground()` / `t.getForeground()` for uncoloured rows instead of `Color.WHITE`. All diff-coloured rows (LEFT_ONLY green, RIGHT_ONLY red, DIFF_CELL yellow) set `Color.BLACK` foreground so text is readable against pale highlight colours in dark themes.

#### Zebra striping

`zebraColor(JTable, row)` blends 1/12 of the foreground into the background for odd rows, producing a subtle stripe that automatically adapts to both light and dark themes.

#### Legend swatches

`mkSwatch()` now calls `setForeground(Color.BLACK)` — previously the label text was nearly invisible in dark mode.

#### Tabbed QueryRep in diff picker

The `others` list now includes QueryReps where `isTabbed` is true in addition to those where `isDisplayable()` is true. Tabbed frames are never shown as visible windows, so `isDisplayable()` returns false for them.

#### Popup anchor fix

`showDiffPicker()` previously anchored the popup to `getContentPane().getComponent(0)`. When a QueryRep is tabbed its content pane has no children, causing `ArrayIndexOutOfBoundsException`. The anchor is now `mainPanel` with y-offset `ToolBar.getHeight()`.

---

### SQL Object Tree (`Sui.java`, `SuiTb.java`)

- `showSQLTree()` now calls `jif.setFrameIcon(null)` instead of setting `db.gif` — removes the out-of-place icon from the JInternalFrame title bar.
- `SuiTb`: `TbSQLTree` button constructed with text `"DB tree"` (11pt plain) and no icon; `sqlTreeI` set to `null`. `java.awt.Font` added to imports.

---

## Files Changed

| File | Change summary |
|---|---|
| `src/QueryRepTabbedFrame.java` | **New file** — singleton tabbed results frame |
| `src/QueryRep.java` | `mainPanel` extraction, `TbTab` button, `pullIntoTabs` / `releaseFromTabs` / `closeRep`, `showDiffPicker` popup anchor fix, tabbed-aware diff picker, tooltip update |
| `src/RunIt.java` | Auto-route new results to tabbed frame when `SUI.QREP.TABBED=Y` |
| `src/PropmMisc.java` | "Open results in tabbed view" checkbox |
| `src/Sui.java` | `isQRepTabbed()`, `showSQLTree()` icon removal, version bump |
| `src/SuiTb.java` | `TbSQLTree` text label instead of icon, `Font` import |
| `src/DiffRep.java` | Dark-mode cell renderer, zebra striping, swatch foreground, `zebraColor()` helper |
| `docs/QueryRepWindow.md` | Tabbed Results Window section added |
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
