# Unreferenced Classes

Classes that are **not reachable** from any of the three root hierarchies:
- [Sui](hierarchy-Sui.md)
- [RunIt](hierarchy-RunIt.md)
- [RunItB](hierarchy-RunItB.md)

These classes are never instantiated or referenced along any known call path.
They may be dead code, standalone utilities, or components awaiting integration.

---

## Unreferenced Classes (21)

All 21 classes below reside in `src/unused/`.

| Class | File | Notes |
|---|---|---|
| `DirectoryReader` | DirectoryReader.java | Standalone filesystem reader |
| `DirectoryWriter` | DirectoryWriter.java | Standalone filesystem writer |
| `GetJar` | GetJar.java | Standalone JAR utility |
| `ImpXLSt` | ImpXLSt.java | Thin wrapper around ImpXLS, not called |
| `JComboBox` | JComboBox.java | Empty interface shadowing javax.swing.JComboBox, never implemented |
| `LineNumbering` | LineNumbering.java | Orphaned line numbering utility |
| `LoadFromJar` | LoadFromJar.java | Standalone JAR loader |
| `PrintComponents` | PrintComponents.java | Orphaned multi-component print helper |
| `PropcS` | PropcS.java | Orphaned property panel variant |
| `PropEdit` | PropEdit.java | Orphaned property editor |
| `Propmap` | Propmap.java | Orphaned property mapping panel |
| `PropmCAll` | PropmCAll.java | Orphaned profile sub-panel |
| `ResultsModel` | ResultsModel.java | Orphaned table model |
| `RowHeaderExample` | RowHeaderExample.java | Example/demo component, unused |
| `SrchAdapter` | SrchAdapter.java | Orphaned search adapter |
| `SrchSheet` | SrchSheet.java | Only referenced in a commented-out line in QryPop |
| `SymbThd` | SymbThd.java | Symbolic resolution thread, not started |
| `TextFilter` | TextFilter.java | Orphaned text filter |
| `TextPrinter` | TextPrinter.java | Orphaned text printer |
| `TImpXLS` | TImpXLS.java | Orphaned XLS import variant |
| `URLClassLoad` | URLClassLoad.java | Orphaned URL-based class loader |

---

## Summary

| Category | Count |
|---|---|
| Total Java classes in project | 138 |
| Reachable from Sui | ~84 |
| Reachable from RunIt (new beyond Sui) | ~9 |
| Reachable from RunItB (new beyond Sui) | 0 |
| **Not reachable from any root** | **21** |

---

> Generated: 2026-04-03
