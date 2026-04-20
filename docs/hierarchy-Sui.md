# Call Hierarchy — `Sui.java`

Root entry point of the application. All classes reachable directly or transitively from `Sui`.

---

## Hierarchy Tree

```
Sui  (root / main entry point)
│
├── QryMon
├── TabbedPaneClassic
├── ProfProp
├── ApplComp
├── FileSuff
├── TextLineNumber
├── ConnDB
├── CopyDir
├── DelFilesOlder
├── DriverShim
├── NumericTextField
├── InNumericTextField
├── RoundField
├── getTblForAlias
├── TableAtCursor
├── connP
├── Garabage
├── GetConn
├── Propc
├── QueryAtCursor
├── UndoManagerHelper
│
├── SuiTb
│   ├── GetImageIcon
│   └── PropmAll
│       ├── PropmLogin
│       ├── PropmExp
│       ├── PropmSQL
│       ├── PropmMisc
│       ├── PropmRep
│       ├── PropmC1
│       ├── Propmcp
│       │   └── ClassLoad
│       └── PropmSheet
│           └── PropmSheetA
│
├── FormatSQL
│   ├── RemComm
│   └── ParseSQL
│
├── RemLineNo
│   └── ParseSQL
│
├── Highlighter
│
├── ReplSQL
│   ├── ReplEvent
│   ├── ReplListener
│   └── ReplStr
│
├── DrawQuery
│   ├── TableAtCursor
│   └── RunSql ──╮ (see RunSql below)
│
├── DConnInf
│   ├── ConnDB
│   └── QueryRep ──╮ (see QueryRep below)
│
├── DPropInf
│   └── QueryRep ──╮
│
├── ShowQryBox
│   ├── GetImageIcon
│   └── RunSql ──╮
│
├── SchemaProvider
│   └── ConnDB
│
├── TableProvider
│   └── ConnDB
│
├── ColumnProvider
│   └── ConnDB
│
├── Propmc
│   ├── GetPropFromJar
│   ├── GetImageIcon
│   ├── ParseSQL
│   ├── ClassLoad  (also via Propmcp)
│   ├── ConnProp
│   ├── SymbResx
│   │   ├── SymEvent
│   │   └── SymListener
│   └── AddConn
│       ├── ConnProp  (cycle ↑)
│       └── ConnAddEvent
│           └── ConnAddListener
│
├── PrintQry
│   └── PrintComponent
│       └── QueryPrinter
│
├── FavQry
│   ├── ShowSQL
│   ├── FavPop
│   │   ├── GetImageIcon
│   │   ├── FavDes
│   │   └── ShowSQL
│   ├── FavPopRing
│   │   └── FavTDes
│   └── RunSql ──╮
│
├── FileTreePanel
│   └── QryPop
│       ├── GetImageIcon
│       ├── CopyToDerby
│       ├── RunDerby
│       │   ├── ConnDB
│       │   ├── ParseSQL
│       │   ├── SymbRes
│       │   ├── ShowSQL
│       │   ├── DB2SQLCA
│       │   ├── InsStmt
│       │   └── CreateDDL
│       ├── AppendToTable
│       │   ├── RunDerby  (cycle ↑)
│       │   └── NumericTextField
│       ├── ImpXLS
│       │   ├── FileSuff
│       │   ├── SuiImpXLS
│       │   └── SuiImpXLSX
│       ├── FormSQL2
│       ├── InsStmt  (also via RunDerby, QueryRep)
│       ├── SQLSeqComp
│       ├── TableSplitter
│       └── RunSql ──╮
│
└── RunSql  ◄────────────── (referenced by DrawQuery, ShowQryBox, FavQry, FileTreePanel/QryPop)
    ├── RunDerby  (cycle to above)
    └── QueryRep
        ├── GetImageIcon
        ├── ShowSQL
        ├── ExpCSV
        ├── ExpXLS
        ├── ColorRenderer
        ├── SuiAdapter
        ├── FixedAdapter
        ├── SuiSortAdapter
        ├── ShowCol
        │   ├── formatJSON
        │   ├── FormatXML
        │   └── FormSQL2  (also via QryPop)
        ├── BlobPan
        ├── ParseSQL
        ├── FooterFormat
        ├── InsStmt  (also via QryPop, RunDerby)
        ├── TablePrinter
        ├── FilterDef
        │   ├── NumericTextField
        │   │   └── NumericDocument
        │   ├── InNumericTextField
        │   │   └── InNumericDocument
        │   ├── FiltEvent
        │   └── FiltListener
        ├── PrintPreviewer
        │   └── PrintMonitor
        └── PrintQry
```

---

## All Reachable Classes (Flat List)

| Class | Reached Via |
|---|---|
| AddConn | Propmc |
| AppendToTable | QryPop |
| ClassLoad | Propmc, Propmcp |
| ApplComp | Sui (direct) |
| BlobPan | QueryRep |
| ColorRenderer | QueryRep |
| ColumnProvider | Sui (direct) |
| connP | Sui (direct) |
| ConnAddEvent | AddConn |
| ConnAddListener | ConnAddEvent |
| ConnDB | Sui (direct), SchemaProvider, TableProvider, ColumnProvider, DConnInf, RunDerby |
| ConnProp | Propmc, AddConn |
| CopyDir | Sui (direct) |
| CopyToDerby | QryPop |
| CreateDDL | RunDerby |
| DB2SQLCA | RunDerby |
| DConnInf | Sui (direct) |
| DelFilesOlder | Sui (direct) |
| DPropInf | Sui (direct) |
| DrawQuery | Sui (direct) |
| DriverShim | Sui (direct) |
| ExpCSV | QueryRep |
| ExpXLS | QueryRep |
| FavDes | FavPop |
| FavPop | FavQry |
| FavPopRing | FavQry |
| FavQry | Sui (direct) |
| FavTDes | FavPopRing |
| FileSuff | Sui (direct), ImpXLS |
| FileTreePanel | Sui (direct) |
| FilterDef | QueryRep |
| FiltEvent | FilterDef, FiltListener |
| FiltListener | FilterDef |
| FixedAdapter | QueryRep |
| FooterFormat | QueryRep |
| formatJSON | ShowCol |
| FormSQL2 | QryPop, ShowCol |
| FormatSQL | Sui (direct) |
| FormatXML | ShowCol |
| Garabage | Sui (direct) |
| GetConn | Sui (direct), ColumnProvider, ConnDB, DConnInf, RunDerby, SchemaProvider, TableProvider |
| GetImageIcon | SuiTb, FavPop, QryPop, ShowQryBox, QueryRep, Propmc |
| GetPropFromJar | Propmc |
| getTblForAlias | Sui (direct) |
| Highlighter | Sui (direct) |
| ImpXLS | QryPop |
| InNumericDocument | InNumericTextField |
| InsStmt | QryPop, RunDerby, QueryRep |
| InNumericTextField | Sui (direct), FilterDef |
| NumericDocument | NumericTextField |
| NumericTextField | Sui (direct), AppendToTable, FilterDef |
| ParseSQL | FormatSQL, RemLineNo, Propmc, RunDerby, QueryRep |
| PrintComponent | PrintQry |
| PrintMonitor | PrintPreviewer |
| PrintPreviewer | QueryRep |
| PrintQry | Sui (direct), PrintComponent path |
| ProfProp | Sui (direct) |
| Propc | Sui (direct), ConnProp |
| PropmC1 | PropmAll |
| Propmcp | PropmAll |
| QueryAtCursor | Sui (direct) |
| PropmAll | SuiTb |
| PropmExp | PropmAll |
| PropmLogin | PropmAll |
| PropmMisc | PropmAll |
| PropmRep | PropmAll |
| PropmSheet | PropmAll |
| PropmSheetA | PropmSheet |
| PropmSQL | PropmAll |
| Propmc | Sui (direct) |
| QryMon | Sui (direct) |
| QryPop | FileTreePanel |
| QueryPrinter | PrintComponent |
| QueryRep | RunSql, DConnInf, DPropInf |
| RemComm | FormatSQL |
| RemLineNo | Sui (direct) |
| ReplEvent | ReplSQL |
| ReplListener | ReplSQL |
| ReplSQL | Sui (direct) |
| ReplStr | ReplSQL |
| RoundField | Sui (direct) |
| RunDerby | QryPop, RunSql |
| RunSql | DrawQuery, ShowQryBox, FavQry, QryPop |
| SchemaProvider | Sui (direct) |
| ShowCol | QueryRep |
| ShowQryBox | Sui (direct) |
| ShowSQL | FavQry, FavPop, RunDerby, QueryRep |
| SuiAdapter | QueryRep |
| SuiImpXLS | ImpXLS |
| SuiImpXLSX | ImpXLS |
| SuiSortAdapter | QueryRep |
| SuiTb | Sui (direct) |
| SQLSeqComp | QryPop |
| SymbRes | RunDerby |
| SymbResx | Propmc |
| SymEvent | Propmc, SymbResx, SymListener |
| SymListener | Propmc, SymbResx |
| TabbedPaneClassic | Sui (direct) |
| TablePrinter | QueryRep |
| TableSplitter | QryPop |
| TableAtCursor | Sui (direct), DrawQuery |
| TableProvider | Sui (direct) |
| TextLineNumber | Sui (direct) |
| UndoManagerHelper | Sui (direct) |

**Total reachable: ~103 classes**

---

> Generated: 2026-04-03
