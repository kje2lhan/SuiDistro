# Call Hierarchy — `RunItB.java`

Batch/background query execution variant. Implements `Runnable`; launched via `Thread` from `RunSql`.

---

## Hierarchy Tree

```
RunItB  (Runnable — entry via Thread.start())
│
├── ConnDB                             (JDBC connection wrapper / cache)
│   └── Sui                            (application context, properties)
│       ├── QryMon
│       ├── TabbedPaneClassic
│       ├── ProfProp
│       ├── SuiTb
│       │   ├── GetImageIcon
│       │   └── PropmAll
│       │       ├── PropmLogin
│       │       ├── PropmExp
│       │       ├── PropmSQL
│       │       ├── PropmMisc
│       │       ├── PropmRep
│       │       └── PropmSheet
│       │           └── PropmSheetA
│       ├── FavQry
│       │   ├── ShowSQL
│       │   ├── FavPop
│       │   │   ├── GetImageIcon
│       │   │   ├── FavDes
│       │   │   └── ShowSQL
│       │   └── FavPopRing
│       │       └── FavTDes
│       ├── FileTreePanel
│       │   └── QryPop
│       │       ├── GetImageIcon
│       │       ├── CopyToDerby
│       │       ├── RunDerby
│       │       ├── AppendToTable
│       │       └── ImpXLS
│       │           ├── SuiImpXLS
│       │           └── SuiImpXLSX
│       ├── ReplSQL
│       │   ├── ReplEvent
│       │   └── ReplListener
│       └── [...all other Sui dependencies]
│
├── Sui                                (direct reference — see above)
│
└── ParseSQL                           (SQL parsing utility)
```

---

## All Reachable Classes (Flat List)

| Class | Reached Via |
|---|---|
| ConnDB | RunItB (direct) |
| ParseSQL | RunItB (direct) |
| Sui | RunItB (direct) |
| — | All classes reachable from Sui (see [hierarchy-Sui.md](hierarchy-Sui.md)) |

`RunItB` is a narrow class — its own logic uses only `ConnDB`, `Sui`, and `ParseSQL` directly.
All further reachability flows through `Sui`, which pulls in the full application graph
documented in [hierarchy-Sui.md](hierarchy-Sui.md).

**Total unique classes reachable (excluding Sui sub-tree): 3**
**Total including Sui sub-tree: ~83 classes**

---

> Generated: 2026-04-03
