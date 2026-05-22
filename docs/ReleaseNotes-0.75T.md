# Release Notes — Sui 0.75T

**Branch:** `Sui0.75S` → `Sui0.75T`  
**Base:** `Sui 0.75S` (Tabbed Results Window, FlatLaf themes, DiffRep dark-mode polish)  
**Date:** 2026-05-22  

---

## Summary of Changes

| Area | Type | Description |
|---|---|---|
| Query editor (no-wrap) | Bug fix | Wrap cascade eliminated — typing on one row no longer causes other rows to re-flow when `SUI.WRAP=N` |
| Query editor (no-wrap) | Bug fix | `NonWrappingTextPane` now uses a custom `ViewFactory` whose `ParagraphView.layout()` is forced to `Short.MAX_VALUE` width — the canonical Swing no-wrap recipe under `StyledEditorKit` |
| Query editor popup | Bug fix | Right-click popup (`QryPop`) now opens from anywhere in the visible query window — extra `MouseListener` on the viewport handles clicks in the empty area to the right of narrow non-wrapping content |
| Result Set Compare (DiffRep) | New feature | **Named diff presets** — save column roles (Key / Compare / Ignore), trim and case settings per preset to `DiffPresets.pro` |
| Result Set Compare (DiffRep) | New feature | **Presets ▾** menu — save, apply and delete named presets per result-set pair |
| Documentation | New | `docs/AdditionalEditFunctions.md` — comprehensive reference for the QryPop "Additional Edit functions" submenu (Format SQL, Syntax Validate, Add/Remove Schema, Trim, Indent/Unindent, Toggle Comment, Build IN List, Text→Insert Statement, Paren Matching, etc.) |
| Documentation | Update | `docs/ResultSetCompare.md` — new section describing the named-preset workflow |
| QueryRep window | Enhancement | Window title now shows the connection **alias** instead of the full URL — shorter and easier to identify |
| QueryRep window | Bug fix | Visual header now correctly indicates when the max-rows limit has been reached |
| QueryRep window | Bug fix | "Copy from result set" actions corrected; assorted Look-and-Feel glitches resolved |
| Main window | Bug fix | Resize behaviour restored — the main frame correctly tracks its container again |
| Main window | Bug fix | Window **restore** (from minimised / saved layout) reliably restores position and size |
| Preferences | Bug fix | Various small fixes in `Propm`, `PropmAll`, `PropmLogin` related to restore and persistence |
| Tabbed Results Window | Bug fix | Header / max-rows indicator updated correctly when tabs are switched |
| Version | Bump | `0.75S` → `0.75T` |

---

## Detailed Changes by Area

### Query editor — non-wrapping mode (`Highlighter.java`)

When `SUI.WRAP=N` the editor must lay out each paragraph at its natural width and let the horizontal scrollbar take over. The previous implementation overrode only `getScrollableTracksViewportWidth()` on `NonWrappingTextPane`, which is **not sufficient** under `StyledEditorKit`: the styled `ParagraphView` re-flows to the allocated viewport width on every layout pass, producing the "wrap cascade" symptom — a keystroke on row 1 would cause unrelated rows further down to wrap or unwrap.

The fix uses the canonical Swing no-wrap recipe:

- `nonWrapHighlightKit` extends `StyledEditorKit` and overrides `getViewFactory()`.
- The custom factory returns:
  - `LabelView` for content runs,
  - `BoxView` (`Y_AXIS`) for sections,
  - a custom `ParagraphView` whose `layout(int w, int h)` calls `super.layout(Short.MAX_VALUE, h)` and whose `getMinimumSpan(...)` returns `getPreferredSpan(...)`.
- `NonWrappingTextPane` also overrides `setSize(Dimension)` to enforce a minimum preferred width.
- `GetPane()` selects this kit whenever `SUI.WRAP=N`.

Result: each row is laid out independently at its preferred width and the horizontal scrollbar tracks the widest line. No more cross-row re-flow.

### Query editor — right-click popup (`Sui.java`, `QryPop.java`)

Previously the right-click popup only fired when the click landed within the painted text area, which (with non-wrap) could be a narrow strip on the left. A second `MouseListener` is now attached to the scroll pane's **viewport** so right-clicks in the empty area to the right of the text still open `FavQ1Pop` at the cursor. The popup is anchored to `textArea` with a small `(+20, +20)` offset for consistent placement.

### Result Set Compare — named presets (`DiffRep.java`)

Users frequently re-run the same diff against different snapshots of the same query and want to keep the column-role configuration (Key / Compare / Ignore) plus *Trim* and *Case* checkboxes.

New inner class `DiffPresetStore` persists presets to `DiffPresets.pro` (under the Sui profile directory). The diff toolbar gains a **Presets ▾** drop-down with:

- **Save preset…** — prompts for a name; overwrites if it already exists.
- **Apply preset →** — submenu listing every saved preset; selecting one restores the role assignments and checkboxes.
- **Delete preset →** — submenu to remove a preset.

Presets are keyed by name only (not by column set), so applying a preset to a different result-set pair will simply map any column names that match and leave the rest untouched.

### Documentation

- **`docs/AdditionalEditFunctions.md`** *(new)* — full reference for every entry in the QryPop "Additional Edit functions" submenu, with a quick-reference table at the top and short workflow tips per function.
- **`docs/ResultSetCompare.md`** *(updated)* — new "Presets ▾" section describes saving, applying and deleting named presets.

### QueryRep window (`QueryRep.java`, `QueryRepTabbedFrame.java`, `RunIt.java`, `Sui.java`)

- Window title format changed from full JDBC URL to connection **alias** — much shorter, especially helpful for the tabbed results frame.
- Max-rows banner / header indicator is now updated reliably when results stop early because the limit was reached.
- Copy actions from the result-set table fixed; several FlatLaf-related rendering glitches resolved.

### Main window & layout (`Sui.java`, `Propm.java`, `PropmAll.java`, `PropmLogin.java`)

- Main frame resize tracking restored.
- Window-restore path (from saved layout or minimised state) reliably restores both position and size.
- Small persistence/restore fixes in the preference panels.

---

## Files Changed

```
docs/AdditionalEditFunctions.md   (new)
docs/ResultSetCompare.md
docs/ReleaseNotes-0.75T.md        (this file, new)
src/DiffRep.java
src/Highlighter.java
src/Propm.java
src/PropmAll.java
src/PropmLogin.java
src/QryPop.java
src/QueryRep.java
src/QueryRepTabbedFrame.java
src/RunIt.java
src/Sui.java
src/TabbedPaneClassic.java
src/TextLineNumber.java
src/ExpXLS.java
README.md
```

---

## Commits (newest first)

```
a812eda Fixed Edit Docs
9758a2f Some new functionality for Compare, and fix for overflowing editor
bccae08 Fixed visual header for maxrows reached
49a653b Set shorter Queryrep title, Alias instead of URL
e4226b5 Fix to get resize to work again
30c0edc Fix restore
33153e0 Bug fixes
bb98e16 Copy from resultset + Look and feel bugs
```

---

**Copyright:** Kjell Hansson, May 2026
