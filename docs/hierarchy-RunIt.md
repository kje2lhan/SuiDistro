# Call Hierarchy — `RunIt.java`

Core query execution engine. Implements `Runnable`; launched via `Thread` from `RunSql`.

---

## Hierarchy Tree

```
RunIt  (Runnable — entry via Thread.start())
│
├── DatabaseManager                    (DB connection wrapper)
│
├── ParseSQL                           (SQL parsing utility)
│
├── QryMon                             (query monitoring)
│
├── DB2SQLCA                           (DB2 extended error messages)
│
├── QryInclude                         (file-based SQL includes)
│
├── nonSQL                             (non-SQL statement processor)
│   └── ParseSQL
│
├── SpOut                              (stored procedure output params)
│   └── ParseSQL
│
├── TbFlt                              (table filter dialog)
│   ├── ConnDB
│   ├── GetConn
│   ├── Propm
│   └── RunSql  (cycle ↓)
│
├── ExpXLSRS                           (direct Excel export from ResultSet)
│   ├── QryMon
│   └── Sui
│
├── BlobToFile                         (BLOB column export)
│   └── Sui
│
├── ClobToFile                         (CLOB column export)
│   └── Sui
│
├── FormatSQL                          (SQL formatter)
│   ├── RemComm                        (remove comments)
│   └── ParseSQL
│
├── SymbRes                            (symbolic variable resolver)
│   └── Sui
│
├── TableComboBox                      (combo box for table selection)
│
├── QueryRep                           (results display panel)
│   ├── GetImageIcon
│   ├── SuiAdapter
│   ├── SuiSortAdapter
│   ├── FixedAdapter
│   ├── ShowCol
│   │   ├── formatJSON
│   │   ├── FormatXML
│   │   └── FormSQL2
│   ├── BlobPan
│   ├── ShowSQL
│   ├── ExpCSV
│   ├── ExpXLS
│   ├── ColorRenderer
│   ├── FooterFormat
│   ├── InsStmt
│   ├── TablePrinter
│   ├── FilterDef
│   │   ├── NumericTextField
│   │   │   └── NumericDocument
│   │   ├── InNumericTextField
│   │   │   └── InNumericDocument
│   │   ├── FiltEvent
│   │   └── FiltListener
│   ├── PrintPreviewer
│   │   └── PrintMonitor
│   └── PrintQry
│       └── PrintComponent
│           └── QueryPrinter
│
└── RunSql                             (SQL runner launcher)
    ├── RemComm
    ├── RunIt  (circular ↑)
    └── RunDerby
        ├── ConnDB
        ├── GetConn
        ├── ParseSQL
        ├── SymbRes
        ├── ShowSQL
        ├── DB2SQLCA
        ├── InsStmt
        ├── QryMon  (also RunIt direct)
        └── CreateDDL
```

---

## All Reachable Classes (Flat List)

| Class | Reached Via |
|---|---|
| BlobPan | QueryRep |
| BlobToFile | RunIt (direct) |
| ClobToFile | RunIt (direct) |
| ColorRenderer | QueryRep |
| ConnDB | TbFlt, RunDerby |
| CreateDDL | RunDerby |
| DatabaseManager | RunIt (direct) |
| DB2SQLCA | RunIt (direct), RunDerby |
| ExpCSV | QueryRep |
| ExpXLS | QueryRep |
| ExpXLSRS | RunIt (direct) |
| FiltEvent | FilterDef |
| FiltListener | FilterDef |
| FilterDef | QueryRep |
| FixedAdapter | QueryRep |
| FooterFormat | QueryRep |
| FormSQL2 | ShowCol |
| formatJSON | ShowCol |
| FormatXML | ShowCol |
| FormatSQL | RunIt (direct) |
| GetConn | TbFlt, ConnDB (indirect via RunDerby) |
| GetImageIcon | QueryRep |
| InNumericDocument | InNumericTextField |
| InsStmt | QueryRep, RunDerby |
| InNumericTextField | FilterDef |
| nonSQL | RunIt (direct) |
| NumericDocument | NumericTextField |
| NumericTextField | FilterDef |
| ParseSQL | RunIt (direct), nonSQL, SpOut, FormatSQL, RunDerby |
| Propm | TbFlt |
| PrintComponent | PrintQry |
| PrintMonitor | PrintPreviewer |
| PrintPreviewer | QueryRep |
| PrintQry | QueryRep path |
| QryInclude | RunIt (direct) |
| QryMon | RunIt (direct), ExpXLSRS |
| QueryPrinter | PrintComponent |
| QueryRep | RunIt (direct) |
| RemComm | FormatSQL, RunSql |
| RunDerby | RunSql |
| RunSql | RunIt (direct) |
| ShowCol | QueryRep |
| TablePrinter | QueryRep |
| ShowSQL | QueryRep, RunDerby |
| SpOut | RunIt (direct) |
| SuiAdapter | QueryRep |
| SuiSortAdapter | QueryRep |
| SymbRes | RunIt (direct), RunDerby |
| TableComboBox | RunIt (direct) |
| TbFlt | RunIt (direct) |
| Sui | TbFlt, BlobToFile, ClobToFile, ExpXLSRS, SymbRes (indirect) |

**Total reachable: ~51 classes**

---

> Generated: 2026-04-03
